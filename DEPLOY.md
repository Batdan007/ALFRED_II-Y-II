# ALFRED SYSTEMS - Deployment Guide

Quick guide to deploying the beta to Railway (backend) and Vercel (frontend).

## Prerequisites

- GitHub account (code should be pushed)
- Railway account (https://railway.app)
- Vercel account (https://vercel.com)
- Stripe account (https://stripe.com) - optional for beta
- Resend account (https://resend.com) - optional for emails

---

## 1. Deploy Backend to Railway

### Quick Deploy

1. Go to https://railway.app/new
2. Click "Deploy from GitHub repo"
3. Select your `ALFRED_II-Y-II` repository
4. Railway will auto-detect Python and use the `Procfile`

### Environment Variables (Railway Dashboard)

Add these in the Railway dashboard under "Variables":

```
# Required
PORT=8000

# AI Providers (at least one)
ANTHROPIC_API_KEY=sk-ant-...
# OR
OPENAI_API_KEY=sk-...
# OR
GROQ_API_KEY=gsk_...

# Optional - Billing
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Optional - Email
RESEND_API_KEY=re_...
FROM_EMAIL=noreply@yourdomain.com

# Frontend URL (for CORS)
FRONTEND_URL=https://your-app.vercel.app
```

### Get Your Backend URL

After deploy, Railway provides a URL like:
`https://your-app.up.railway.app`

Copy this - you'll need it for the frontend.

---

## 2. Deploy Frontend to Vercel

### Quick Deploy

1. Go to https://vercel.com/new
2. Import your GitHub repo
3. Set **Root Directory** to `web`
4. Framework will auto-detect as Next.js

### Environment Variables (Vercel Dashboard)

Add this in Vercel dashboard under "Environment Variables":

```
NEXT_PUBLIC_API_URL=https://your-backend.up.railway.app
```

### Deploy

Click "Deploy" and wait for the build to complete.

---

## 3. Set Up Stripe (Optional for Beta)

For open beta, you can skip Stripe entirely. Users get Pro features free.

If you want payments:

1. Go to https://dashboard.stripe.com
2. Create Products:
   - **Pro Monthly**: $9.99/month recurring
   - **Enterprise Monthly**: $49.99/month recurring
3. Copy the Price IDs to Railway env vars
4. Set up webhook endpoint: `https://your-backend.up.railway.app/api/billing/webhook`
5. Add webhook secret to Railway

---

## 4. Set Up Resend (Optional)

1. Go to https://resend.com
2. Create API key
3. Verify your domain (or use their test domain for beta)
4. Add `RESEND_API_KEY` to Railway

---

## 5. Test the Deployment

1. Visit your Vercel URL
2. Click "Join Beta" and enter your email
3. Check if you receive welcome email (if Resend configured)
4. Create account with the same email
5. Verify you get Pro tier automatically
6. Birth an agent and chat with it

---

## Local Development

### Backend
```bash
cd ALFRED_II-Y-II
pip install -r requirements.txt
python -m maiai_platform.server
# Runs at http://localhost:8000
```

### Frontend
```bash
cd ALFRED_II-Y-II/web
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
npm run dev
# Runs at http://localhost:3000
```

---

## Troubleshooting

### "AI generation failed" error
- Check that at least one AI provider key is set
- Ollama won't work in Railway (cloud deployment)
- Use Anthropic, OpenAI, or Groq

### CORS errors
- Make sure `FRONTEND_URL` is set in Railway
- Check it matches your Vercel URL exactly

### Database errors
- Railway uses ephemeral storage
- For production, add a Railway Postgres addon
- Update `database.py` to use PostgreSQL

### Emails not sending
- Check Resend API key is valid
- Verify domain in Resend dashboard
- Check Railway logs for errors

---

## Production Checklist

Before going fully public:

- [ ] Add rate limiting
- [ ] Set up Railway Postgres (persistent database)
- [ ] Configure custom domain
- [ ] Set up error monitoring (Sentry)
- [ ] Remove `/api/billing/test-upgrade` endpoint
- [ ] Restrict CORS to your domain only
- [ ] Set up log aggregation
- [ ] Configure backups

---

## URLs Summary

| Service | URL |
|---------|-----|
| Backend API | https://your-app.up.railway.app |
| API Docs | https://your-app.up.railway.app/api/docs |
| Frontend | https://your-app.vercel.app |
| Health Check | https://your-app.up.railway.app/health |
