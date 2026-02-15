# 🚀 Backend Deployment Guide - Railway

Deploy your Budget Buddy FastAPI backend to **Railway** (100% FREE tier)

---

## ✅ What's Already Prepared

I've created these files for you:
- ✅ [Procfile](Procfile) - Tells Railway how to start your app
- ✅ [railway.json](railway.json) - Railway configuration
- ✅ [requirements.txt](requirements.txt) - Python dependencies

**Your backend is ready to deploy!** 🎉

---

## 🎯 Railway Deployment (Web Interface)

### Step 1: Sign Up for Railway

1. Go to https://railway.app/
2. Click "Login" (top right)
3. Sign up with **GitHub** (easiest - connects your repo)
4. Verify your email
5. **Free tier includes:**
   - $5 credit per month
   - Enough for small apps
   - No credit card required

---

### Step 2: Create New Project

1. **Click "New Project"** on Railway dashboard
2. **Choose "Deploy from GitHub repo"**
3. **Authorize Railway** to access your GitHub account
4. **Select your repository:**
   - Repository: `Budgeting app` or your repo name
   - Branch: `main` or `backend`

Railway will automatically detect it's a Python app!

---

### Step 3: Configure Environment Variables

**CRITICAL:** Add these environment variables in Railway:

1. Click on your deployed service
2. Go to **"Variables"** tab
3. Add each variable:

```bash
# Supabase
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_anon_key_here

# Groq (LLM)
GROQ_API_KEY=your_groq_api_key_here

# RapidAPI (Cost of Living)
RAPIDAPI_KEY=your_rapidapi_key_here

# Configuration
LLM_PROVIDER=groq
COST_API_PROVIDER=rapidapi
ENVIRONMENT=production
DEBUG=False
API_HOST=0.0.0.0
```

**Note:** Get your actual API keys from:
- Supabase: Your project settings
- Groq: https://console.groq.com/keys
- RapidAPI: https://rapidapi.com/hub

4. Click **"Add"** for each variable
5. Railway will **auto-redeploy** when you save

---

### Step 4: Get Your Backend URL

1. Once deployed, Railway gives you a URL like:
   ```
   https://budgeting-app-production.up.railway.app
   ```

2. **Test your backend:**
   - Open: `https://your-url.railway.app/docs`
   - You should see the FastAPI Swagger documentation
   - Try the `/api/v1/budgets/list` endpoint

3. **Copy this URL** - you'll need it for frontend!

---

## 🔧 Alternative: Deploy via Railway CLI

If you prefer command line:

### Install Railway CLI:
```powershell
# Windows (PowerShell)
iwr https://railway.app/install.ps1 | iex
```

### Deploy:
```bash
# Login
railway login

# Link project (creates new project if doesn't exist)
railway link

# Add environment variables
railway variables set SUPABASE_URL=https://csrqjkxfqnrhfpnvowba.supabase.co
railway variables set SUPABASE_KEY=your_key_here
railway variables set GROQ_API_KEY=your_key_here
railway variables set RAPIDAPI_KEY=your_key_here

# Deploy
railway up
```

---

## 📊 Monitor Your Deployment

### Check Logs:
1. Go to Railway dashboard
2. Click your service
3. Go to **"Deployments"** tab
4. Click on latest deployment
5. View **"Build Logs"** and **"Deploy Logs"**

### Common Issues:

**Build fails:**
- Check `requirements.txt` has all dependencies
- Make sure Python version is compatible (3.11+)

**App crashes:**
- Check environment variables are set correctly
- View logs for error messages
- Ensure `backend/__init__.py` exists

**Can't connect:**
- Wait 2-3 minutes for first deploy
- Check deployment status is "Success"
- Test with `/docs` endpoint first

---

## 🔄 Update Your Backend

Whenever you make changes:

1. **Commit to GitHub:**
   ```bash
   git add .
   git commit -m "Update backend"
   git push
   ```

2. **Railway auto-deploys!**
   - No manual steps needed
   - Watch logs in Railway dashboard
   - Takes ~2-3 minutes

---

## 💰 Free Tier Limits

**Railway Free Tier:**
- ✅ $5 credit/month
- ✅ 500 hours runtime
- ✅ 8GB RAM
- ✅ 8GB disk
- ✅ Unlimited projects

**Enough for:**
- Testing and development
- Small production apps
- ~15,000 API requests/month

**Upgrade if needed:**
- Hobby plan: $5/month
- Keeps unused credit
- More resources

---

## 🎯 Next Step: Update Frontend

Once your backend is deployed:

1. **Copy your Railway URL**
2. **Update frontend** to use production backend
3. **Deploy frontend** to Vercel/Netlify

See [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) for frontend deployment!

---

## ✅ Deployment Checklist

- [ ] Signed up for Railway
- [ ] Created new project from GitHub
- [ ] Added all environment variables
- [ ] Deployment successful (check status)
- [ ] Tested `/docs` endpoint
- [ ] Copied backend URL
- [ ] Updated frontend API URL
- [ ] Deployed frontend

---

## 🆘 Troubleshooting

### "Module not found" error:
```bash
# Make sure all imports use absolute paths:
from backend.config import settings  # ✓ Good
from config import settings          # ✗ Bad
```

### "Port already in use":
```bash
# Railway sets PORT automatically
# Make sure main.py uses $PORT env variable
```

### Environment variables not loading:
```bash
# Check variable names match exactly
# No quotes around values in Railway UI
# Restart deployment after adding vars
```

### CORS errors:
```bash
# Update backend/config.py CORS_ORIGINS to include:
# Your Railway URL
# Your Vercel URL (once deployed)
```

---

## 🎉 Success!

Your backend is now live at:
```
https://your-app-name.up.railway.app
```

**Test it:**
- API Docs: `/docs`
- Health check: `/api/v1/budgets/list?user_id=test`

**Deploy time:** ~5 minutes 🚀

Ready to deploy your frontend? See [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)!
