# 🚀 Aditya Retail AI Ecommerce - Production Setup Guide

## 📋 **CREDENTIALS NEEDED**

### 1. PhonePe Business Account
**Where to find:**
- Login to https://business.phonepe.com/
- Go to **Developer** → **API Keys**
- Copy: Merchant ID, Salt Key, Salt Index

**Test Environment:**
- Use UAT credentials first: https://business-uat.phonepe.com/
- Switch to production after testing

### 2. Shiprocket Account  
**Where to find:**
- Login to https://shiprocket.in/
- Use your **email and password**
- Go to **Settings** → **API** for additional configs

### 3. Gmail App Password
**How to generate:**
1. Go to https://myaccount.google.com/security
2. Enable **2-Step Verification** (if not enabled)
3. Go to **App Passwords**
4. Select **Mail** and generate 16-character password
5. Use this password (not your regular Gmail password)

---

## ⚡ **QUICK SETUP (Once you have credentials)**

### Step 1: Configure Environment
```bash
# Copy template and add your credentials
cp /app/backend/production_config_template.env /app/backend/.env

# Edit the file with your actual credentials
nano /app/backend/.env
```

### Step 2: Restart Backend
```bash
sudo supervisorctl restart backend
```

### Step 3: Test Integration
```bash
# I'll run comprehensive tests to verify everything works
curl -X POST http://localhost:8001/api/payment-test
curl -X POST http://localhost:8001/api/shipping-test  
curl -X POST http://localhost:8001/api/email-test
```

---

## 🧪 **TESTING CHECKLIST**

### PhonePe Integration
- [ ] Payment initiation (₹1 test transaction)
- [ ] Payment callback handling
- [ ] Transaction verification
- [ ] Failed payment handling

### Shiprocket Integration  
- [ ] Pincode serviceability check
- [ ] Shipping cost calculation
- [ ] Order creation in Shiprocket
- [ ] AWB generation
- [ ] Tracking integration

### Email Notifications
- [ ] Order confirmation emails
- [ ] Shipping update notifications  
- [ ] Service request confirmations
- [ ] Email template rendering

### Complete Order Flow
- [ ] Product selection → Cart → Checkout
- [ ] Address validation → Shipping calculation
- [ ] Payment (PhonePe + COD) → Order creation
- [ ] Shiprocket booking → Email notifications
- [ ] Order tracking → Delivery updates

---

## 🎯 **PRODUCTION LAUNCH CHECKLIST**

### Pre-Launch
- [ ] All integrations tested with real credentials
- [ ] SSL certificate configured for domain
- [ ] Payment callback URLs updated with real domain
- [ ] Email templates customized with branding
- [ ] AI agents tested with business scenarios
- [ ] Admin dashboard access configured

### Go-Live
- [ ] Switch PhonePe from UAT to Production
- [ ] Enable real payment processing
- [ ] Configure business email addresses
- [ ] Set up inventory monitoring alerts
- [ ] Enable customer support workflows

### Post-Launch Monitoring
- [ ] Payment success/failure rates
- [ ] Shipping cost accuracy  
- [ ] Email delivery rates
- [ ] AI agent response quality
- [ ] System performance metrics

---

## 🆘 **SUPPORT CONTACTS**

- **PhonePe Support**: merchant.care@phonepe.com
- **Shiprocket Support**: support@shiprocket.in  
- **Platform Issues**: I'm here to help! 🤖

---

## 💡 **BUSINESS OPTIMIZATION TIPS**

### Payment Optimization
- Enable both PhonePe and COD for maximum conversion
- Set COD limits (e.g., max ₹50,000)
- Monitor payment failure reasons

### Shipping Optimization  
- Use Shiprocket's cheapest rate finder
- Enable real-time tracking for customers
- Set up delivery performance monitoring

### AI Agent Optimization
- Monitor customer queries and improve responses
- Track conversion rates for each agent
- Use insights for business strategy

**Ready to configure everything once you share the credentials!** 🚀