# 🚂 Railway Quick Start Guide

## ✅ Your Project is Ready!

All your files are already configured for Railway:
- ✅ `Procfile` exists
- ✅ `requirements.txt` has all dependencies
- ✅ `app.py` is production-ready
- ✅ Database configuration is set up

## 🚀 5-Minute Setup

### Step 1: Go to Railway
Visit **[railway.app](https://railway.app)** and sign up with **GitHub**

### Step 2: Create Project
1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Find and select your **FunzaMama** repository
4. Railway will automatically detect it's a Python project ✅

### Step 3: Add PostgreSQL Database
1. In your project dashboard, click **"+ New"**
2. Select **"Database"** → **"Add PostgreSQL"**
3. ✅ Railway automatically:
   - Creates the database
   - Provides `DATABASE_URL` environment variable
   - Connects it to your app
   - **No manual setup needed!**

### Step 4: Set Environment Variables
1. Click on your **Web Service** (not the database)
2. Go to **"Variables"** tab
3. Click **"+ New Variable"** and add:

```bash
FLASK_ENV=production
SECRET_KEY=<paste-your-secret-key-here>
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=chemiatsalome@gmail.com
MAIL_PASSWORD=<your-gmail-app-password>
PREFERRED_URL_SCHEME=https
```

**Generate SECRET_KEY:**
```python
import secrets
print(secrets.token_hex(32))
```

**Important:**
- ✅ Railway automatically provides `DATABASE_URL` - **don't add it manually**
- ✅ Use your **Gmail App Password** (not regular password) for `MAIL_PASSWORD`
- ✅ Don't add `PORT` - Railway provides this automatically

### Step 5: Deploy!
Railway automatically:
- ✅ Detects Python
- ✅ Installs from `requirements.txt`
- ✅ Uses your `Procfile` (or auto-detects)
- ✅ Starts your app
- ✅ **No configuration needed!**

### Step 6: Get Your URL
Once deployed, Railway provides:
```
https://your-app-name.up.railway.app
```

### Step 7: Initialize Database
1. Click on your **Web Service**
2. Go to **"Deployments"** tab
3. Click **"..."** → **"Open Shell"**
4. Run:
   ```bash
   flask db upgrade
   ```
   Or if no migrations:
   ```bash
   python -c "from app import app, db; app.app_context().push(); db.create_all()"
   ```

### Step 8: Create Admin User (Optional)
In the same shell:
```bash
flask create-admin
```

## 🎉 That's It!

Your app is now live on Railway! 🚂

## 📊 What Railway Does Automatically

- ✅ Detects Python project
- ✅ Installs dependencies
- ✅ Handles port binding
- ✅ Provides PostgreSQL database
- ✅ Sets up HTTPS
- ✅ Auto-deploys on git push

## 🔍 Monitor Your App

- **Logs:** Click on service → "Logs" tab
- **Usage:** Settings → "Usage" tab
- **Deployments:** "Deployments" tab

## 💰 Pricing

- **Free Tier:** $5/month credit (usually enough!)
- **Hobby:** $5/month if you exceed free tier
- **Pro:** $20/month for production

## 🆘 Need Help?

- Check Railway logs for errors
- See `RAILWAY_DEPLOYMENT.md` for detailed guide
- Railway Discord: https://discord.gg/railway

Good luck! Your app should deploy successfully on Railway! 🚀
