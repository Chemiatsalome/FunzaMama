# 🔧 Set FLASK_ENV=production in Railway

## ❌ The Problem

You're still seeing:
```
INFO  [alembic.runtime.migration] Context impl MySQLImpl.
```

This means `FLASK_ENV=production` is **not set** in Railway.

## ✅ Solution: Set FLASK_ENV in Railway Dashboard

### Step 1: Go to Railway Dashboard

1. Go to **Railway Dashboard** → Your **Web Service** (FunzaMama app)
2. Click **"Variables"** tab (or "Environment Variables")

### Step 2: Add FLASK_ENV

1. Look for `FLASK_ENV` in the list
2. If it's **missing**:
   - Click **"+ New Variable"** button
   - **Variable Name**: `FLASK_ENV`
   - **Value**: `production`
   - Click **"Add"**
3. If it **exists but is wrong**:
   - Click on the variable
   - Change value to: `production`
   - Click **"Save"**

### Step 3: Verify DATABASE_URL

Also make sure `DATABASE_URL` is set:
- Should be: `postgresql://postgres:password@postgres.railway.internal:5432/railway`
- If missing, get it from: Database Service → Variables → `DATABASE_URL`

### Step 4: Run Migrations Again

After setting `FLASK_ENV=production`:

```bash
railway run python -m flask db upgrade
```

**Expected output:**
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.  ✅
```

## 🔍 Alternative: Set Environment Variable in Command

If Railway dashboard doesn't work, you can set it in the command:

```bash
railway run --env FLASK_ENV=production python -m flask db upgrade
```

## ✅ Quick Checklist

- [ ] Go to Railway Dashboard → Web Service → Variables
- [ ] Add/Update `FLASK_ENV` = `production`
- [ ] Verify `DATABASE_URL` is set
- [ ] Run `railway run python -m flask db upgrade`
- [ ] Should see `PostgresqlImpl` (not `MySQLImpl`)

## 🆘 If Still Not Working

Check what Railway sees:

```bash
railway run python -c "import os; print('FLASK_ENV:', os.environ.get('FLASK_ENV')); print('DATABASE_URL:', 'SET' if os.environ.get('DATABASE_URL') else 'NOT SET')"
```

This will show you what environment variables Railway has.
