# 🔧 Fix DATABASE_URL and Create Tables

## ✅ Step 1: Verify DATABASE_URL is Set in Railway

Your DATABASE_URL should be:
```
postgresql://postgres:skuXuVVCDCaaMOZWiWoMOQUcKuFrAtvb@postgres.railway.internal:5432/railway
```

**To verify:**
1. Go to Railway Dashboard → Your **Web Service** (FunzaMama app)
2. Click **"Variables"** tab
3. Look for `DATABASE_URL`
4. If it's missing, add it:
   - Click **"+ New Variable"**
   - Name: `DATABASE_URL`
   - Value: `postgresql://postgres:skuXuVVCDCaaMOZWiWoMOQUcKuFrAtvb@postgres.railway.internal:5432/railway`
   - Click **"Add"**

**Note:** `postgres.railway.internal` is Railway's internal hostname - it only works within Railway's network. This is correct for production!

## ✅ Step 2: Set FLASK_ENV=production

Make sure `FLASK_ENV=production` is set:

1. Railway Dashboard → Your **Web Service** → **Variables** tab
2. Look for `FLASK_ENV`
3. If missing, add it:
   - Name: `FLASK_ENV`
   - Value: `production`
   - Click **"Add"**

## ✅ Step 3: Run Migrations to Create Tables

After `DATABASE_URL` is set, create the tables:

### Option A: Using Railway Dashboard (Easiest)

1. Go to Railway Dashboard → Your **Web Service**
2. Click **"Settings"** tab
3. Find **"Run Command"** or terminal
4. Run:
```bash
flask db upgrade
```

### Option B: Using Railway CLI

```bash
railway login
railway link
railway run flask db upgrade
```

### Option C: Using Python Script

I've created `run_migrations.py` - you can run it:

```bash
railway run python run_migrations.py
```

## ✅ Step 4: Verify Tables Are Created

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

## ✅ Step 5: Test Signup

After tables are created:
- Go to: `https://funzamama-production.up.railway.app/signup`
- Try signing up
- Should work! ✅

## 🆘 Troubleshooting

### If DATABASE_URL is None

**Check Railway logs:**
- Look for: `⚠️ WARNING: DATABASE_URL not found!`
- Solution: Add `DATABASE_URL` to Railway web service variables

**Debug in Railway:**
```bash
railway run python -c "import os; print('DATABASE_URL:', os.environ.get('DATABASE_URL'))"
```

### If Migrations Fail

**Error: "Target database is not up to date"**
```bash
railway run flask db migrate -m "Initial schema"
railway run flask db upgrade
```

**Error: "No such file or directory: migrations/versions"**
```bash
railway run flask db init
railway run flask db migrate -m "Initial schema"
railway run flask db upgrade
```

### If Connection Fails

**Error: "could not translate host name"**
- Make sure you're using Railway's internal hostname: `postgres.railway.internal`
- Don't use external hostnames for Railway production

**Error: "password authentication failed"**
- Verify `DATABASE_URL` password is correct
- Get fresh `DATABASE_URL` from Railway Database → Variables

## ✅ Success Checklist

- [ ] `DATABASE_URL` is set in Railway web service variables
- [ ] `FLASK_ENV=production` is set
- [ ] Ran `flask db upgrade` successfully
- [ ] Tables appear in Railway database dashboard
- [ ] App starts without errors
- [ ] `/signup` works without 500 error

## 📝 Quick Commands Reference

```bash
# Check DATABASE_URL
railway run python -c "import os; print(os.environ.get('DATABASE_URL'))"

# Run migrations
railway run flask db upgrade

# Create migration (if needed)
railway run flask db migrate -m "Initial schema"

# Initialize migrations (if needed)
railway run flask db init

# Run custom migration script
railway run python run_migrations.py
```
