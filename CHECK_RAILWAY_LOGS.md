# How to Check Railway Logs Without CLI

## Method 1: Railway Dashboard (Easiest)

1. **Go to Railway Dashboard**: https://railway.app/dashboard
2. **Select your project**
3. **Click on your Web Service** (the one running your app)
4. **Click "Deployments" tab** (or "Logs" tab)
5. **Find the latest deployment**
6. **Look for the "Release" phase** - this is where `init_db.py` runs

### What to Look For:
- ✅ `📦 Initializing database...`
- ✅ `✅ Tables created successfully!` or `✅ Migrations completed successfully!`
- ✅ `📋 Database tables:` followed by a list of tables
- ❌ Any error messages starting with `❌ ERROR:`

## Method 2: Check Database Directly

1. **Go to Railway Dashboard**
2. **Click on your PostgreSQL database service**
3. **Click "Data" tab**
4. **Check if tables exist**:
   - Should see: `users`, `badges`, `game_stages`, `user_responses`, `quiz_questions`, `user_scenario_progress`, `user_question_history`, `feedback`
   - Currently only seeing: `alembic_version` ❌

## Method 3: Trigger a New Deployment

If `init_db.py` didn't run, trigger a new deployment:

1. **Make a small change** (add a comment to any file)
2. **Commit and push**:
   ```bash
   git add .
   git commit -m "Trigger deployment"
   git push origin main
   ```
3. **Watch the deployment logs** in Railway Dashboard
4. **Check the "Release" phase** for `init_db.py` output

## Method 4: Check if releaseCommand is Running

1. **Go to Railway Dashboard**
2. **Click on your Web Service**
3. **Click "Settings" tab**
4. **Check "Deploy" section**
5. **Verify `releaseCommand` is set to**: `python init_db.py`

If it's not set, add it in `railway.json` (which we already did).
