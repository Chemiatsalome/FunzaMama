# 🔧 Fix: Railway Using MySQL Instead of PostgreSQL

## ❌ The Problem

When running migrations, you see:
```
INFO  [alembic.runtime.migration] Context impl MySQLImpl.
```

This means Railway is using **MySQL** instead of **PostgreSQL**!

## ✅ The Solution

Railway needs `FLASK_ENV=production` to use PostgreSQL.

### Step 1: Set FLASK_ENV=production in Railway

1. Go to **Railway Dashboard** → Your **Web Service** (FunzaMama app)
2. Click **"Variables"** tab
3. Look for `FLASK_ENV`
4. If it's missing or not set to `production`, add/update it:
   - Click **"+ New Variable"** (if missing)
   - Name: `FLASK_ENV`
   - Value: `production`
   - Click **"Add"**

### Step 2: Verify DATABASE_URL is Set

Also check that `DATABASE_URL` is set:
- Should be: `postgresql://postgres:password@postgres.railway.internal:5432/railway`
- If missing, add it from your Database Service → Variables

### Step 3: Run Migrations Again

After setting `FLASK_ENV=production`:

```bash
railway run python -m flask db upgrade
```

Now you should see:
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.  ✅
```

Instead of:
```
INFO  [alembic.runtime.migration] Context impl MySQLImpl.  ❌
```

## 🔍 Why This Happens

Your `config.py` checks:
```python
if os.environ.get('FLASK_ENV') == 'production':
    # Use PostgreSQL (DATABASE_URL)
else:
    # Use MySQL (local development)
```

If `FLASK_ENV` is not set to `production`, it defaults to MySQL!

## ✅ Quick Fix Checklist

- [ ] `FLASK_ENV=production` is set in Railway Variables
- [ ] `DATABASE_URL` is set in Railway Variables
- [ ] Run `railway run python -m flask db upgrade` again
- [ ] Should see `PostgresqlImpl` (not `MySQLImpl`)
