# 🚨 URGENT: Render Gunicorn Fix

## The Problem
Render keeps saying `gunicorn: command not found` even though it's in requirements.txt.

## ✅ IMMEDIATE SOLUTION: Update Render Dashboard Settings

### Step 1: Go to Render Dashboard
1. Open your Render dashboard
2. Click on your **Web Service**
3. Go to **"Settings"** tab

### Step 2: Update Build Command
In **"Build & Deploy"** section, set:

**Build Command:**
```bash
pip install --upgrade pip && pip install -r requirements.txt && python -m pip show gunicorn
```

**Start Command:**
```bash
python -m gunicorn app:app
```

**Why `python -m gunicorn`?**
- This uses Python's module system
- Works even if gunicorn isn't in PATH
- More reliable on Render

### Step 3: Save and Redeploy
1. Click **"Save Changes"**
2. Go to **"Manual Deploy"** → **"Deploy latest commit"**
3. Watch the build logs

### Step 4: Verify in Build Logs
Look for these lines:
```
Successfully installed gunicorn-21.2.0
Successfully installed psycopg2-binary-2.9.9
Location: /opt/render/project/src/.venv/lib/python3.11/site-packages
```

---

## 🔄 Alternative: Use Build Script

I've created `build.sh` for you. To use it:

1. **In Render Dashboard:**
   - Build Command: `chmod +x build.sh && ./build.sh`
   - Start Command: `python -m gunicorn app:app`

2. **Commit the build script:**
   ```bash
   git add build.sh
   git commit -m "Add build script for Render"
   git push origin main
   ```

---

## 🚂 BETTER ALTERNATIVE: Switch to Railway

Render is being difficult. **Railway is much simpler:**

### Why Railway is Better:
- ✅ Auto-detects Python projects
- ✅ Automatically installs from requirements.txt
- ✅ No build command configuration needed
- ✅ Free tier with $5/month credit
- ✅ Less configuration headaches

### Quick Railway Setup:
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click **"New Project"** → **"Deploy from GitHub repo"**
4. Select your FunzaMama repository
5. Add PostgreSQL: **"+ New"** → **"Database"** → **"PostgreSQL"**
6. Set environment variables (see RAILWAY_DEPLOYMENT.md)
7. **Done!** Railway auto-deploys

**That's it!** No build command configuration needed.

---

## 🔍 Debugging Render Build

### Check Build Logs:
1. In Render dashboard → Your service → **"Logs"** tab
2. Look for the build phase
3. Check if you see:
   ```
   Running pip install -r requirements.txt
   ```

### If Build Command Isn't Running:
- Render might be using cached build
- Try: **"Manual Deploy"** → **"Clear build cache and deploy"**

### Verify requirements.txt is Being Read:
Add this to your build command temporarily:
```bash
pip install --upgrade pip && cat requirements.txt && pip install -r requirements.txt
```

This will show you what's in requirements.txt during build.

---

## 💡 Why This Happens

Render sometimes:
- Uses cached builds (old requirements.txt)
- Doesn't run build command properly
- Has PATH issues with installed packages

**Solution:** Use `python -m gunicorn` instead of just `gunicorn`

---

## ✅ Final Checklist

Before redeploying on Render:

- [ ] Build Command set to: `pip install --upgrade pip && pip install -r requirements.txt`
- [ ] Start Command set to: `python -m gunicorn app:app`
- [ ] `requirements.txt` has `gunicorn>=21.2.0`
- [ ] `runtime.txt` exists with `python-3.11.0`
- [ ] All changes committed and pushed to GitHub
- [ ] Clear build cache before redeploying

---

## 🎯 My Recommendation

**Switch to Railway.** It's:
- Easier to set up
- More reliable
- Better free tier
- Less configuration needed

See `RAILWAY_DEPLOYMENT.md` for complete instructions.

---

## 🆘 Still Not Working?

If Render still fails after all this:

1. **Check Render Status:** [status.render.com](https://status.render.com)
2. **Contact Render Support:** They're usually helpful
3. **Switch to Railway:** Seriously, it's much easier
4. **Try Heroku:** More expensive but very reliable

Good luck! 🚀
