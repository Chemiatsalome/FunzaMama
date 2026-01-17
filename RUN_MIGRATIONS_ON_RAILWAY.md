# 🚂 Run Migrations on Railway (Not Locally)

## ❌ The Problem

You're trying to run migrations **locally**, but `postgres.railway.internal` only works **inside Railway's network**.

**Error:** `could not translate host name "postgres.railway.internal" to address`

This is **expected** - Railway's internal hostname doesn't work from your local machine.

## ✅ The Solution

Run migrations **on Railway**, not locally.

## 📋 Step-by-Step: Run Migrations on Railway

### Option A: Railway Dashboard (Easiest)

1. **Go to Railway Dashboard** → Your **Web Service** (FunzaMama app)
2. Click **"Settings"** tab
3. Scroll down to **"Run Command"** or find the terminal
4. Run this command:
   ```bash
   flask db upgrade
   ```

### Option B: Railway CLI

1. **Install Railway CLI** (if not installed):
   ```bash
   npm install -g @railway/cli
   ```

2. **Login and link:**
   ```bash
   railway login
   railway link
   ```

3. **Run migrations:**
   ```bash
   railway run flask db upgrade
   ```

### Option C: Railway Dashboard → Deploy → Run Command

1. Go to Railway Dashboard → Your **Web Service**
2. Click **"Deployments"** tab
3. Click **"..."** (three dots) → **"Run Command"**
4. Enter: `flask db upgrade`
5. Click **"Run"**

## ✅ What Should Happen

After running `flask db upgrade` on Railway, you should see:

```
INFO  [alembic.runtime.migration] Running upgrade -> [revision], [message]
✅ Tables created successfully!
```

## 🔍 Verify Tables Are Created

1. Go to Railway Dashboard → Your **Database Service** (`funzamama-db`)
2. Click **"Database"** tab → **"Data"** tab
3. You should see tables:
   - `users`
   - `badge`
   - `game_stage`
   - `user_response`
   - `quiz_question`
   - `user_scenario_progress`
   - `alembic_version`

## 🆘 Troubleshooting

### If "flask db migrate" is needed first

If you get "Target database is not up to date", create the migration first:

```bash
railway run flask db migrate -m "Initial schema"
railway run flask db upgrade
```

### If migrations folder doesn't exist

If you get "No such file or directory: migrations/versions":

```bash
railway run flask db init
railway run flask db migrate -m "Initial schema"
railway run flask db upgrade
```

### If you want to connect locally (Advanced)

If you **really** need to connect from your local machine:

1. Go to Railway Dashboard → Your **Database Service**
2. Click **"Variables"** tab
3. Look for `PGHOST` or `PUBLIC_URL` - this is the **public** hostname
4. Use that instead of `postgres.railway.internal`

**But this is NOT recommended** - just run migrations on Railway! ✅

## ✅ Success Checklist

- [ ] Ran `flask db upgrade` **on Railway** (not locally)
- [ ] Migration completed successfully
- [ ] Tables appear in Railway database dashboard
- [ ] `/signup` works without 500 error

## 📝 Quick Reference

**✅ DO THIS:**
```bash
# On Railway
railway run flask db upgrade
```

**❌ DON'T DO THIS:**
```bash
# Locally (won't work!)
python run_migrations.py
```
