# Aditya Retail - Vercel Deployment Guide

## Prerequisites

1. **Vercel Account**: Sign up at https://vercel.com
2. **Vercel CLI**: Install globally
3. **MongoDB Atlas**: Your database (already configured)
4. **GitHub Account** (optional but recommended)

---

## Step 1: Install Vercel CLI

```bash
# Install Vercel CLI globally
npm install -g vercel

# Verify installation
vercel --version

# Login to Vercel
vercel login
```

---

## Step 2: Deploy Backend (FastAPI)

### Option A: Deploy Backend to Vercel (Serverless)

```bash
# Navigate to backend directory
cd /app/backend

# Deploy to Vercel
vercel

# Follow the prompts:
# - Set up and deploy? Yes
# - Which scope? Select your account
# - Link to existing project? No
# - Project name? aditya-retail-backend
# - Directory? ./
# - Override settings? No
```

### Option B: Deploy Backend to Railway (Recommended for Full Features)

Vercel serverless has limitations (no WebSockets, cold starts). For full functionality:

1. Go to https://railway.app
2. Connect your GitHub repo
3. Select the `backend` folder
4. Add environment variables (see below)
5. Deploy

---

## Step 3: Set Backend Environment Variables

In Vercel Dashboard → Project → Settings → Environment Variables, add:

| Variable | Value | Notes |
|----------|-------|-------|
| `MONGO_URL` | `mongodb+srv://...` | Your MongoDB connection string |
| `DB_NAME` | `startup_template` | Database name |
| `EMERGENT_LLM_KEY` | `sk-emergent-...` | AI integration key |
| `PHONEPE_MERCHANT_ID` | `M224EIU0W7NHS` | PhonePe merchant ID |
| `PHONEPE_SALT_KEY` | `b8063715-a14a-418a-973f-ef6341087184` | PhonePe salt key |
| `PHONEPE_SALT_INDEX` | `1` | PhonePe salt index |
| `PHONEPE_ENVIRONMENT` | `PRODUCTION` | PhonePe environment |
| `SENDGRID_API_KEY` | `SG.xxx...` | SendGrid API key |
| `GOOGLE_MAPS_API_KEY` | `AIza...` | Google Maps API key |
| `JWT_SECRET_KEY` | `your-secret-key` | JWT signing key |

Or via CLI:
```bash
vercel env add MONGO_URL
vercel env add PHONEPE_MERCHANT_ID
# ... etc for each variable
```

---

## Step 4: Deploy Frontend (React)

```bash
# Navigate to frontend directory
cd /app/frontend

# Deploy to Vercel
vercel

# Follow the prompts:
# - Set up and deploy? Yes
# - Which scope? Select your account
# - Link to existing project? No
# - Project name? aditya-retail-frontend
# - Directory? ./
# - Override settings? No
```

---

## Step 5: Set Frontend Environment Variables

In Vercel Dashboard → Project → Settings → Environment Variables, add:

| Variable | Value |
|----------|-------|
| `REACT_APP_BACKEND_URL` | `https://your-backend-domain.vercel.app` |

**Important**: Replace with your actual backend URL from Step 2.

Or via CLI:
```bash
vercel env add REACT_APP_BACKEND_URL
# Enter: https://aditya-retail-backend.vercel.app
```

---

## Step 6: Deploy to Production

```bash
# Deploy backend to production
cd /app/backend
vercel --prod

# Deploy frontend to production
cd /app/frontend
vercel --prod
```

---

## Step 7: Configure Custom Domain (Optional)

```bash
# Add custom domain
vercel domains add yourdomain.com

# Or in Vercel Dashboard:
# Project → Settings → Domains → Add Domain
```

---

## Quick Deploy Commands Summary

```bash
# One-time setup
npm install -g vercel
vercel login

# Backend deployment
cd /app/backend
vercel --prod

# Frontend deployment  
cd /app/frontend
vercel --prod

# Check deployment status
vercel ls

# View logs
vercel logs
```

---

## Environment Variables Reference

### Backend (.env)
```env
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/
DB_NAME=startup_template
EMERGENT_LLM_KEY=sk-emergent-xxx
PHONEPE_MERCHANT_ID=M224EIU0W7NHS
PHONEPE_SALT_KEY=checkout-flow-test
PHONEPE_SALT_INDEX=1
PHONEPE_ENVIRONMENT=PRODUCTION
SENDGRID_API_KEY=SG.xxx
GOOGLE_MAPS_API_KEY=AIzaxxx
JWT_SECRET_KEY=your-secure-secret-key
REDIRECT_URL=https://your-frontend-domain.vercel.app/#/payment-success
CALLBACK_URL=https://your-backend-domain.vercel.app/api/phonepe/callback
```

### Frontend (.env)
```env
REACT_APP_BACKEND_URL=https://your-backend-domain.vercel.app
```

---

## Troubleshooting

### Build Fails
```bash
# Check build logs
vercel logs --output build

# Rebuild
vercel --force
```

### Environment Variables Not Loading
```bash
# List all env vars
vercel env ls

# Pull env vars locally
vercel env pull
```

### CORS Issues
Make sure `CORS_ORIGINS` in backend includes your frontend domain.

---

## Important Notes

1. **WebSockets**: Vercel serverless doesn't support WebSockets. The notification system will fall back to polling mode automatically.

2. **Cold Starts**: Serverless functions may have 1-2 second cold start delays on first request.

3. **For Full Features**: Consider deploying backend to Railway/Render for WebSocket support and no cold starts.

4. **Database**: Make sure your MongoDB Atlas allows connections from Vercel's IP ranges (or use 0.0.0.0/0 for all IPs).

---

## Support

If you encounter issues:
1. Check Vercel deployment logs: `vercel logs`
2. Verify environment variables are set correctly
3. Ensure MongoDB Atlas network access is configured

