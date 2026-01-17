# 🚂 Railway Final Setup Guide

## ✅ Current Status

Your files are now correctly configured:
- ✅ `runtime.txt` → `python-3.11.8` (supported version)
- ✅ `Procfile` → `gunicorn app:app --bind 0.0.0.0:$PORT`
- ✅ `railway.json` → Proper gunicorn configuration
- ✅ `start.py` → Deleted (not needed)

## 🚨 Important: Clear Railway Cache

Railway is still using **cached configuration** that references `python start.py`. You MUST clear the cache:

### Step 1: Clear Build Cache in Railway

1. Go to **Railway Dashboard** → Your **Web Service**
2. Click **"Settings"** tab
3. Scroll to **"Build & Deploy"** section
4. Click **"Clear Build Cache"** button
   - OR click **"Redeploy"** → **"Clear cache and redeploy"**

### Step 2: Verify Service Type

Make sure your service is set as **"Web Service"** (not Background Worker):
1. Go to **Settings** → **General**
2. Verify **"Service Type"** is **"Web Service"**

## 🔑 Setting Environment Variables (Including SECRET_KEY)

### Step 1: Generate SECRET_KEY

Run this locally to generate a secret key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Or use this one (I'll generate it for you):
```
<will-be-generated-below>
```

### Step 2: Add Environment Variables in Railway

1. Go to Railway Dashboard → Your **Web Service** (not the database)
2. Click **"Variables"** tab
3. Click **"+ New Variable"** for each:

```bash
FLASK_ENV=production
SECRET_KEY=<paste-the-generated-key-here>
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=chemiatsalome@gmail.com
MAIL_PASSWORD=<your-gmail-app-password>
PREFERRED_URL_SCHEME=https
```

**Important:**
- ✅ Railway automatically provides `DATABASE_URL` - **don't add it manually**
- ✅ Don't add `PORT` - Railway provides this automatically
- ✅ Use the **generated SECRET_KEY** (not the example one)

### Step 3: Verify Start Command

1. Go to **Settings** → **Build & Deploy**
2. Under **"Start Command"**, it should be:
   ```
   gunicorn app:app --bind 0.0.0.0:$PORT
   ```
   Or Railway will use your `Procfile` automatically.

## 🔄 After Setting Variables

1. **Clear build cache** (most important!)
2. **Redeploy** - Railway will:
   - Use Python 3.11.8 from `runtime.txt`
   - Install dependencies
   - Use gunicorn from `Procfile`
   - Start your app

## 📊 What You Should See (Success)

After clearing cache and redeploying, logs should show:

```
mise python@3.11.8 install
Successfully installed python@3.11.8
Installing requirements...
Starting gunicorn 23.0.0
Listening at: http://0.0.0.0:10000
Booting worker with pid...
```

## 🆘 If Still Using `python start.py`

If Railway still shows `$ python start.py` in logs:

1. **Check Railway Settings:**
   - Settings → Build & Deploy
   - Look for "Start Command" override
   - Clear it or set to: `gunicorn app:app --bind 0.0.0.0:$PORT`

2. **Check railway.json:**
   - Should have: `"startCommand": "gunicorn app:app --bind 0.0.0.0:$PORT --worker-class sync --workers 1"`

3. **Force Redeploy:**
   - Deployments → "..." → "Redeploy" → "Clear cache and redeploy"

## ✅ Final Checklist

Before redeploying:
- [x] `runtime.txt` has `python-3.11.8`
- [x] `Procfile` has `gunicorn app:app --bind 0.0.0.0:$PORT`
- [x] `start.py` is deleted
- [x] `railway.json` has correct start command
- [ ] **SECRET_KEY** is set in Railway Variables
- [ ] All other environment variables are set
- [ ] Build cache is cleared
- [ ] Service type is "Web Service"

## 🎯 Next Steps

1. **Generate SECRET_KEY** (see command above)
2. **Add all environment variables** in Railway Dashboard
3. **Clear build cache**
4. **Redeploy**
5. **Watch logs** for success

Your app should deploy successfully! 🚂
