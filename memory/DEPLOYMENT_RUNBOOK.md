# 🚀 Production Deployment Runbook — Pine Labs & My Orders Fixes

## What's Fixed on Preview (Verified Working)

All fixes are tested and working on the preview environment. The preview has 1 order belonging to `rohit.gadiya@gmail.com` displaying correctly in:
- ✅ My Account → My Orders (1 order shown, ₹52,190 total spent)
- ✅ Pine Labs Transactions Dashboard (5 events tracked, 80% success rate)

## Step-by-Step: Deploy to Production

### Step 1 — Redeploy preview to production
Use Emergent's deployment flow. All these files have new/changed code:

**Backend:**
- `backend/pine_labs_routes.py` — fixed payload, signature verification (callback + webhook), 7 NEW admin/recovery endpoints, return_origin support
- `backend/customer_dashboard_routes.py` — order matching by email fallback, back-fill endpoint
- `backend/server.py` — `/orders/create` accepts both `customer_id` and `user_id`

**Frontend:**
- `frontend/src/components/Checkout.js` — sends `return_origin` to Pine Labs
- `frontend/src/components/PaymentSuccess.js` — calls `/api/pine-labs/confirm-payment`, recovers from backend when localStorage is empty
- `frontend/src/components/PineLabsTransactions.js` — NEW admin dashboard with Reconcile tool
- `frontend/src/components/AdminDashboardHome.js` — adds dashboard module card
- `frontend/src/components/UnifiedDashboard.js` — adds sidebar entry
- `frontend/src/App.js` — adds `/admin/pine-labs` route

### Step 2 — After redeploy, run back-fill (one curl):
```bash
curl -X POST https://adityaretail.com/api/customer/admin/backfill-customer-ids
```
This will link all your orphan production orders to customer accounts by email.

### Step 3 — Recover your stuck test transaction:
1. Go to https://adityaretail.com/admin/pine-labs
2. Click **"Reconcile Order"** in the header
3. Paste: `v1-260511144149-aa-k4hnm0`
4. The system will fetch live status from Pine Labs and link it to the matching internal order

### Step 4 — Place a fresh test order
With redeployed code, the full flow now works:
- Checkout writes `customer_id` correctly (Bug 1 fixed)
- Pine Labs redirects to same origin (Bug 2 fixed)
- `PaymentSuccess` calls `/api/pine-labs/confirm-payment` (Bug 3 fixed)
- Order's `payment_status` updates to `completed`
- Customer sees order in My Orders
- Admin sees transaction in Pine Labs Dashboard

### Step 5 — (Recommended) Set canonical domain in DNS
Configure your DNS to 301-redirect `www.adityaretail.com → adityaretail.com` (or vice versa). This prevents future cross-origin localStorage issues.

## Verification Checklist (Run after redeploy)

```bash
# 1. Check Pine Labs config
curl https://adityaretail.com/api/pine-labs/config

# 2. Run back-fill
curl -X POST https://adityaretail.com/api/customer/admin/backfill-customer-ids

# 3. Check transactions admin
curl https://adityaretail.com/api/pine-labs/admin/transactions

# 4. Login as customer, then check
curl "https://adityaretail.com/api/customer/orders?user_id=YOUR_USER_ID"
```

## Why You Keep Seeing the Same Bug

Your production deployment still runs the OLD code (before my fixes). Each test transaction hits the same bugs because the new code is only on preview. **Once you redeploy, the new flow takes over.**
