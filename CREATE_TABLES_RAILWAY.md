# 🗄️ Create Database Tables on Railway

## The Problem
Your `/signup` route returns 500 because **PostgreSQL has no tables**.

## The Solution
Run `flask db upgrade` on Railway to create all tables.

## ✅ Step-by-Step Fix

### Step 1: Create Initial Migration (if not exists)

**On Railway (Recommended):**

1. Go to Railway Dashboard → Your **Web Service**
2. Click **"Settings"** tab
3. Find **"Run Command"** or use the terminal
4. Run these commands one by one:

```bash
flask db migrate -m "Initial schema - all tables"
flask db upgrade
```

**Or using Railway CLI:**
```bash
railway login
railway link
railway run flask db migrate -m "Initial schema - all tables"
railway run flask db upgrade
```

### Step 2: Verify Migration File Was Created

After running `flask db migrate`, you should have:
```
migrations/
  └── versions/
      └── [timestamp]_initial_schema_all_tables.py
```

**If the migration file was created on Railway:**
- Download it from Railway logs or use Railway CLI to get it
- Commit it to your GitHub repo
- This ensures future deployments work

### Step 3: Run Migration on Railway

I've updated `railway.json` to automatically run `flask db upgrade` on every deploy.

**Manual Option (if auto doesn't work):**

1. Go to Railway Dashboard → Your **Web Service**
2. Click **"Settings"** tab
3. Find **"Run Command"** or terminal
4. Run:
```bash
flask db upgrade
```

### Step 4: Verify Tables Are Created

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

### Step 5: Test Signup

After tables are created:
- Go to your app: `https://funzamama-production.up.railway.app/signup`
- Try signing up
- Should work! ✅

## 🆘 Troubleshooting

**If `flask db migrate` fails:**
- Make sure `DATABASE_URL` is set
- Make sure `FLASK_ENV=production` is set
- Check Railway logs for errors

**If `flask db upgrade` fails:**
- Check Railway logs
- Verify `DATABASE_URL` format is correct
- Make sure database service is "Online"

**If tables still don't appear:**
- Run `flask db upgrade` again
- Check Railway logs for SQL errors
- Verify you're looking at the correct database service

## ✅ Success Checklist

- [ ] Ran `flask db migrate` successfully
- [ ] Migration file exists in `migrations/versions/`
- [ ] Ran `flask db upgrade` successfully
- [ ] Tables appear in Railway database dashboard
- [ ] `/signup` works without 500 error
- [ ] Can create a user account
