# PhonePe Payment Gateway Testing Guide

## Prerequisites
1. PhonePe Test App installed on your phone
2. Test credentials (already configured in backend)
3. Your backend URL: https://acct-workflow-1.preview.emergentagent.com

## Testing Methods

### Method 1: Using Postman or Thunder Client

#### Step 1: Test Payment Initiation

**Endpoint:** `POST https://acct-workflow-1.preview.emergentagent.com/api/phonepe/initiate`

**Headers:**
```
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "order_id": "ORDER_12345",
  "amount": 10000,
  "merchant_user_id": "user_001",
  "customer_name": "John Doe",
  "customer_email": "john@example.com",
  "customer_phone": "9999999999"
}
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Payment initiated successfully",
  "payment_url": "https://mercury-uat.phonepe.com/...",
  "merchant_transaction_id": "TXN_ORDER_12345_abcd1234"
}
```

#### Step 2: Open Payment URL
- Copy the `payment_url` from the response
- Open it in a browser
- You'll be redirected to PhonePe payment page
- Use PhonePe Test App to complete payment

#### Step 3: Check Payment Status

**Endpoint:** `GET https://acct-workflow-1.preview.emergentagent.com/api/phonepe/status/{merchant_transaction_id}`

**Example:**
```
GET https://acct-workflow-1.preview.emergentagent.com/api/phonepe/status/TXN_ORDER_12345_abcd1234
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "state": "COMPLETED",
    "amount": 10000,
    "transactionId": "T2409281234567890"
  },
  "code": "PAYMENT_SUCCESS",
  "message": "Transaction completed successfully"
}
```

### Method 2: Using CURL Commands

#### Test Payment Initiation:
```bash
curl -X POST "https://acct-workflow-1.preview.emergentagent.com/api/phonepe/initiate" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "ORDER_TEST_001",
    "amount": 50000,
    "merchant_user_id": "user_test_001",
    "customer_name": "Test User",
    "customer_email": "test@example.com",
    "customer_phone": "9876543210"
  }'
```

#### Check Payment Status:
```bash
curl -X GET "https://acct-workflow-1.preview.emergentagent.com/api/phonepe/status/TXN_ORDER_TEST_001_xyz"
```

#### Test Refund:
```bash
curl -X POST "https://acct-workflow-1.preview.emergentagent.com/api/phonepe/refund" \
  -H "Content-Type: application/json" \
  -d '{
    "original_transaction_id": "TXN_ORDER_TEST_001_xyz",
    "refund_amount": 25000,
    "reason": "Product return"
  }'
```

### Method 3: Testing with PhonePe Test App

#### Download PhonePe Test App:
- **Android:** Search "PhonePe Simulator" in Play Store (package: com.phonepe.simulator)
- **iOS:** Request TestFlight invite from PhonePe team

#### Configure Test App:
1. Open PhonePe Test App
2. Set API environment to "UAT/Sandbox"
3. Enter your merchant ID: `M224EIU0W7NHS`

#### Complete Payment Flow:
1. Initiate payment from your API
2. Copy the payment URL
3. Open URL in browser
4. Select PhonePe as payment method
5. Choose payment scenario in test app:
   - **Success:** Payment completes successfully
   - **Failure:** Payment fails with error
   - **Pending:** Payment stuck in pending state

### Method 4: Frontend Integration Testing

I can create a simple test page for you. Would you like me to create:

1. **Payment Test Page** - Simple form to initiate payments
2. **Payment Success Page** - Shows payment completion
3. **Payment Status Checker** - Check any transaction status

## Common Testing Scenarios

### Scenario 1: Successful Payment (₹500)
```json
{
  "order_id": "ORD001",
  "amount": 50000,
  "merchant_user_id": "user001",
  "customer_phone": "9999999999"
}
```

### Scenario 2: Small Amount Payment (₹10)
```json
{
  "order_id": "ORD002",
  "amount": 1000,
  "merchant_user_id": "user002",
  "customer_phone": "9999999999"
}
```

### Scenario 3: Large Amount Payment (₹50,000)
```json
{
  "order_id": "ORD003",
  "amount": 5000000,
  "merchant_user_id": "user003",
  "customer_phone": "9999999999"
}
```

## Troubleshooting

### Error: "Key not found for the merchant"
**Cause:** Merchant credentials not properly configured in PhonePe sandbox
**Solution:** 
1. Contact PhonePe integration team
2. Verify merchant ID is activated in sandbox
3. Check if UAT testing is enabled for your account

### Error: "Invalid checksum"
**Cause:** Checksum calculation issue
**Solution:** Backend automatically handles this - check server logs

### Error: "Amount validation failed"
**Cause:** Amount less than minimum (₹1 = 100 paise)
**Solution:** Ensure amount is at least 100 paise (₹1)

### Payment URL not redirecting
**Cause:** Redirect URL misconfigured
**Solution:** Verify REDIRECT_URL in backend .env file

## Webhook Testing

To test webhooks (payment callbacks):

1. **Use webhook.site temporarily:**
   - Go to https://webhook.site
   - Copy your unique URL
   - Update CALLBACK_URL in backend .env
   - Restart backend
   - Make a payment
   - Check webhook.site for incoming callbacks

2. **Check Backend Logs:**
```bash
tail -f /var/log/supervisor/backend.*.log | grep -i "callback\|payment"
```

## PhonePe Sandbox Account Activation

If you're getting "Key not found" error, you need to:

1. **Contact PhonePe Support:**
   - Email: merchantsupport@phonepe.com
   - Provide your Merchant ID: M224EIU0W7NHS
   - Request UAT sandbox activation

2. **Verify Credentials:**
   - Login to PhonePe Merchant Dashboard
   - Go to Settings → API Credentials
   - Verify sandbox credentials match your .env file

3. **Test Mode Activation:**
   - Ensure your merchant account has "Test Mode" enabled
   - Check if IP whitelisting is required

## Amount Conversion Helper

Remember: PhonePe uses **paise** (1 Rupee = 100 paise)

| Rupees (₹) | Paise |
|-----------|--------|
| ₹1        | 100    |
| ₹10       | 1000   |
| ₹100      | 10000  |
| ₹500      | 50000  |
| ₹1000     | 100000 |
| ₹10000    | 1000000|

## Next Steps

Would you like me to:
1. Create a frontend payment testing page?
2. Build the complete checkout flow with cart integration?
3. Add payment gateway to the product detail pages?
4. Create an admin panel to view all transactions?

Let me know what you'd like to implement next!
