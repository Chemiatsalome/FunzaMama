# 🗑️ How to Clear Railway Build Cache

## Method 1: Clear Cache via Settings (Recommended)

### Step-by-Step:

1. **Go to Railway Dashboard**
   - Visit [railway.app](https://railway.app)
   - Log in to your account

2. **Select Your Project**
   - Click on your **FunzaMama** project

3. **Select Your Web Service**
   - Click on your **Web Service** (not the database)
   - It should be named something like "funzamama-app" or similar

4. **Go to Settings**
   - Click on the **"Settings"** tab at the top

5. **Find Build & Deploy Section**
   - Scroll down to **"Build & Deploy"** section

6. **Clear Build Cache**
   - Look for **"Clear Build Cache"** button
   - Click it
   - OR look for **"Redeploy"** button → Click it → Select **"Clear cache and redeploy"**

## Method 2: Clear Cache via Deployments

### Step-by-Step:

1. **Go to Railway Dashboard**
   - Select your project → Web Service

2. **Go to Deployments Tab**
   - Click on **"Deployments"** tab

3. **Redeploy with Cache Clear**
   - Find the latest deployment
   - Click the **"..."** (three dots) menu
   - Select **"Redeploy"**
   - Choose **"Clear cache and redeploy"** option

## Method 3: Manual Redeploy

### Step-by-Step:

1. **Trigger a New Deployment**
   - Make a small change to any file (or just push an empty commit)
   - Push to GitHub:
     ```bash
     git commit --allow-empty -m "Trigger Railway redeploy"
     git push origin main
     ```
   - Railway will automatically redeploy

2. **Or Use Railway CLI** (if installed):
   ```bash
   railway redeploy --clear-cache
   ```

## Method 4: Delete and Recreate Service (Last Resort)

⚠️ **Only if other methods don't work:**

1. **Delete the Service**
   - Settings → Scroll to bottom → **"Delete Service"**
   - Confirm deletion

2. **Recreate the Service**
   - Click **"+ New"** → **"GitHub Repo"**
   - Select your repository again
   - Railway will create a fresh service with no cache

## ✅ After Clearing Cache

Once you clear the cache, Railway will:
- ✅ Re-detect your project (without old `runtime.txt` cache)
- ✅ Use Python 3.11.8 from your new `runtime.txt`
- ✅ Use gunicorn from your `Procfile`
- ✅ Start fresh build

## 🔍 Verify Cache is Cleared

After clearing cache, check the build logs. You should see:
- ✅ Fresh Python installation (not cached)
- ✅ `mise python@3.11.8 install` (not 3.11.0)
- ✅ `gunicorn app:app` (not `python start.py`)

## 📝 Quick Checklist

- [ ] Go to Railway Dashboard
- [ ] Select your Web Service
- [ ] Go to Settings → Build & Deploy
- [ ] Click "Clear Build Cache" or "Redeploy" → "Clear cache and redeploy"
- [ ] Wait for new deployment
- [ ] Check logs to verify fresh build

## 🆘 Still Having Issues?

If cache still isn't clearing:

1. **Check Railway Status:** [status.railway.app](https://status.railway.app)
2. **Contact Railway Support:** They can clear cache manually
3. **Try Method 4:** Delete and recreate the service (fresh start)

Good luck! 🚂
