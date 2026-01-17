# 🔗 Get Public Database URL from Railway

## The Problem

Railway's `postgres.railway.internal` only works inside Railway's network. To run migrations locally, you need the **public/external** database URL.

## ✅ Solution: Get Public Database URL

### Step 1: Get Public Database URL from Railway

1. Go to **Railway Dashboard** → Your **Database Service** (`funzamama-db`)
2. Click **"Settings"** tab
3. Look for **"Connect"** or **"Connection Info"**
4. Find the **Public URL** or **External Connection String**

It should look like:
```
postgresql://postgres:password@[public-host].railway.app:5432/railway
```

**OR** look in the **Variables** tab for:
- `PUBLIC_URL`
- `PGHOST` (public hostname)
- `PGPORT`
- `PGUSER`
- `PGPASSWORD`
- `PGDATABASE`

### Step 2: Construct Public DATABASE_URL

If you have individual variables, construct it like:
```
postgresql://PGUSER:PGPASSWORD@PGHOST:PGPORT/PGDATABASE
```

### Step 3: Use Public URL Locally

Create a `.env` file in your project root:

```env
FLASK_ENV=production
DATABASE_URL=postgresql://postgres:skuXuVVCDCaaMOZWiWoMOQUcKuFrAtvb@[PUBLIC-HOST].railway.app:5432/railway
```

Replace `[PUBLIC-HOST]` with the actual public hostname from Railway.

### Step 4: Run Migrations Locally

Now you can run:
```bash
python run_migrations.py
```

Or:
```bash
flask db upgrade
```

## 🔍 Alternative: Use Railway CLI

If Railway CLI is installed:

```bash
railway login
railway link
railway run flask db upgrade
```

This runs the command **on Railway's servers**, so it can access `postgres.railway.internal`.

## 📝 Quick Check

To see what Railway provides:

1. Railway Dashboard → Database Service → **Variables** tab
2. Look for all `PG*` variables
3. Use those to construct the public URL
