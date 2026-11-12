# RCA — email-audit-panel DEPLOY readiness timeout (run 8acbe2c9)

## Verdict
The pod did **not** fail for any app/code reason. It failed because **cluster-level infrastructure on target-8 (CNI + node capacity) consumed ~7 of the 10-minute deploy readiness window before the app container could even start.** By the time the container ran and the backend came up, there wasn't enough time left for nginx (:8080) to pass the startup probe. Your code/preview ruling-out was correct.

This is **NOT** CrashLoopBackOff, **NOT** ImagePullBackOff, **NOT** OOMKilled, and **NOT** a readiness/DB/secrets bug. Container termination shows no OOM (exit 137) or crash; image pulled successfully; the backend connected to Atlas and served startup.

## Failed run
- run_id: `8acbe2c9-63a0-479b-8bb1-cd6b1f2f219b` (redeploy, trigger user_deploy, job 2d674e41)
- Failed step: `deploy` (k8s rollout readiness timeout). `health_check` never ran (earlier step failed).
- Tier: tier_1, cluster target-8, image 1.38 GB.
- Deploy window: manifest applied 09:02:12 → timed out 09:12:12 (10 min).

## Timeline reconstructed from pod events (the smoking gun)
| Time (UTC) | Event | Elapsed into window |
|---|---|---|
| 09:02:10 | Deployment scaled RS 0→2; manifest applied 09:02:12 | 0s |
| 09:02:11–09:02:56 | **FailedScheduling** ×many: `Too many pods`, `Insufficient cpu`, `Insufficient memory`, `Insufficient ephemeral-storage` (0/147 nodes available) | 0–45s |
| 09:03:05 | Both pods (m6r6k, sv9m2) finally Scheduled | ~55s |
| 09:05:16–09:08:45 | **FailedCreatePodSandBox** ×repeated: `plugin type="cilium-cni" failed (add): agent is down ... context deadline exceeded` and `putEndpointIdTooManyRequests` (HTTP 429) | ~3–6.5 min |
| 09:08:58–09:09:51 | Image pull (`in 51.2s / 53.1s incl waiting`, 1.38 GB) | ~6.7–7.6 min |
| 09:09:51 / 09:10:05 | Containers **finally Started** | ~7.6–7.9 min |
| 09:09:55–09:11:40 | **Startup probe failed**: `Get http://10.x:8080/health: connect: connection refused` (nginx not yet listening on 8080) | 7.6–9.5 min |
| 09:11:43 | RS created replacement pods (rollout churn) | ~9.5 min |
| 09:12:12 | **Deploy readiness TIMEOUT** | 10 min |

**~7.5 minutes of a 10-minute window were lost to scheduling + CNI sandbox failures + image pull, before the app container ran at all.**

## What the container itself did (from pod logs) — app is healthy
Once the container started (09:09:51 / 09:10:05), the backend came up cleanly:
- `INFO: Uvicorn running on http://0.0.0.0:8001`
- `INFO:server:✅ MongoDB connection successful`
- `Database already has 1213 products` / `Database initialized with indexes`
- `INFO: Application startup complete.` / `✅ AI Ecommerce Platform started successfully!`

**Secrets + DB binding are intact** — the failed pod authenticated to Atlas and read live data (1213 products). `mongodb_migrate` and `manage_secrets` steps both succeeded.

## Contributing factor (secondary, app-side — not the cause, but it shrinks the safety margin)
The entrypoint **serializes** startup: it starts the backend, then waits **up to 120s** for port 8001, and only **then** starts nginx on 8080 — the port the k8s startup probe hits. Logs show:
- `Waiting for backend... (2s…120s elapsed)` then `Backend process is running but not responding on port 8001 after 120s` → `Continuing anyway...` → `Starting nginx...`

So nginx:8080 did not begin listening until ~120s after the container started — which is why the probe saw `connection refused`. Two things worth E1's attention (both resilience, neither is THE root cause):
1. **The entrypoint's own backend check reported "not responding on port 8001 after 120s" even though the backend logged `Application startup complete` / `Uvicorn running on 0.0.0.0:8001` well within that window.** The entrypoint's readiness detection is not matching the backend's actual ready state, forcing the full 120s wait before nginx binds 8080. Fixing this would let nginx come up in seconds instead of ~2 minutes.
2. Combined with a 1.38 GB image (≈1 min pull) and heavy init (1213 products, index build, several scheduler loops), the cold-start budget is already large. When infra ate 7.5 min, the remaining ~2.5 min could not absorb the serialized 120s backend-wait + nginx bind.

## Root cause (primary)
Transient **platform/infrastructure failure on cluster target-8**:
- **Cilium CNI agent down / rate-limited** (`agent is down`, `putEndpointIdTooManyRequests` 429) → repeated `FailedCreatePodSandBox` for ~6 minutes.
- **Node capacity pressure** (`Too many pods`, insufficient cpu/memory/ephemeral-storage across 0/147 nodes) → `FailedScheduling`.
These delayed pod start until 7.5 min into a 10-min window, guaranteeing the readiness timeout regardless of app health. The identical Sep 5 occurrence + the separate `[WAKEUP_ENVIRONMENT] ... unexpected status: 500` are consistent with intermittent target-8 infra instability.

## Remediation
1. **Redeploy** — the infra conditions are transient; a redeploy when target-8 is healthy will very likely go green (the app boots fine). This is the fastest path.
2. **Platform escalation** — Emergent should investigate target-8 cilium-cni agent instability (429 endpoint rate-limiting, agent-down timeouts) and node capacity pressure; consider rescheduling this deployment to a healthier cluster if it recurs.
3. **App hardening (optional, E1)** — fix the entrypoint's backend-readiness check so nginx starts as soon as the backend is actually up (it logs `Application startup complete` well before the 120s cap), and/or start nginx in parallel. This restores the safety margin so a slow/contended cluster doesn't tip the deploy over the readiness timeout. Reducing image size (1.38 GB) would also cut pull time.

## Not the cause (ruled out with evidence)
- CrashLoopBackOff: no restart/crash events; container Started once and ran.
- ImagePullBackOff: image pulled successfully (53s).
- OOMKilled: no OOM/exit-137; app reported 26 MB RSS class workload; no memory-kill events.
- Readiness probe logic / DB / secrets: backend reached `Application startup complete` and connected to Atlas with live data.
