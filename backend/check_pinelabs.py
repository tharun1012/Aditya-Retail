import os, uuid, requests
from datetime import datetime, timezone

cid = os.environ["PL_CID"].strip()
sec = os.environ["PL_SEC"].strip()
print("lengths (client id should be 36, secret should be 32):", len(cid), len(sec))

hosts = [
    ("LIVE", "https://api.pluralpay.in/api"),
    ("UAT", "https://pluraluat.v2.pinepg.in/api"),
]
for name, base in hosts:
    try:
        r = requests.post(
            f"{base}/auth/v1/token",
            json={"client_id": cid, "client_secret": sec, "grant_type": "client_credentials"},
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Request-ID": str(uuid.uuid4()),
                "Request-Timestamp": datetime.now(timezone.utc).isoformat(),
            },
            timeout=30,
        )
        body = r.text
        if r.status_code == 200:
            body = "token received (fields: %s)" % sorted(r.json().keys())
        print(f"{name:4} {base} -> HTTP {r.status_code} | {body[:200]}")
    except Exception as e:
        print(name, "error:", type(e).__name__, str(e)[:120])
