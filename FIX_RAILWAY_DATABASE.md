# 🔧 Fix Railway Database Connection

## ❌ The Problem

Your app is trying to connect to an invalid database hostname:
```
dpg-d037v26uk2gs73ebrb70-a
```

This is **NOT** a Railway database hostname. Railway databases have hostnames like:
- `containers-us-west-xxx.railway.app`
- Or internal service names

## ✅ The Solution

Railway **automatically provides** `DATABASE_URL` when you connect a PostgreSQL service. You just need to make sure it's connected properly.

## 📋 Step-by-Step Fix

### Step 1: Check Your Railway Database Service

1. Go to **Railway Dashboard** → Your Project
2. Look for a service called **"funzamama-db"** (or similar)
3. Make sure it's **"Online"** ✅

### Step 2: Get the Correct DATABASE_URL

**Option A: Railway Auto-Provides It (Recommended)**

Railway automatically provides `DATABASE_URL` to your web service when:
- You have a PostgreSQL database service
- The database is connected to your web service

**To check:**
1. Go to Railway Dashboard → Your **Web Service** (FunzaMama app)
2. Click **"Variables"** tab
3. Look for `DATABASE_URL` in the list
4. If it's there, Railway is providing it automatically ✅

**Option B: Get It Manually**

If `DATABASE_URL` is not in your web service variables:

1. Go to Railway Dashboard → Your **Database Service** (funzamama-db)
2. Click **"Variables"** tab
3. Find `DATABASE_URL` or `POSTGRES_URL`
4. Copy the entire connection string
5. Go to your **Web Service** → **Variables** tab
6. Click **"+ New Variable"**
7. Name: `DATABASE_URL`
8. Value: Paste the connection string
9. Click **"Add"**

### Step 3: Verify the Connection String Format

Railway's `DATABASE_URL` should look like:
```
postgresql://postgres:password@containers-us-west-xxx.railway.app:5432/railway
```

Or:
```
postgres://postgres:password@containers-us-west-xxx.railway.app:5432/railway
```

**NOT:**
```
postgresql://...@dpg-d037v26uk2gs73ebrb70-a/...  ❌ (This is Neon, not Railway)
```

### Step 4: Connect Database to Web Service (If Not Connected)

If your database and web service are not connected:

1. Go to Railway Dashboard → Your **Web Service**
2. Click **"Variables"** tab
3. Look for a message: **"Trying to connect a database? Add Variable"**
4. Click **"Add Variable"** → Select your database service
5. Railway will automatically add `DATABASE_URL`

### Step 5: Redeploy

After adding/updating `DATABASE_URL`:
- Railway will **automatically redeploy** your service
- Check the deployment logs to verify connection

## 🔍 Verify It's Working

After fixing, check Railway logs:
- Should see: `Database connection successful`
- Should NOT see: `could not translate host name`

## 🆘 Troubleshooting

**If DATABASE_URL is still missing:**

1. **Check database service exists:**
   - Railway Dashboard → Look for PostgreSQL service
   - If missing: "+ New" → "Database" → "Add PostgreSQL"

2. **Check database is online:**
   - Database service should show "Online" status
   - If not, wait for it to start

3. **Manually add DATABASE_URL:**
   - Database Service → Variables → Copy `DATABASE_URL`
   - Web Service → Variables → Add `DATABASE_URL` with copied value

**If connection still fails:**

1. Check Railway logs for exact error
2. Verify `DATABASE_URL` format is correct
3. Make sure database service is in the same project

## ✅ What I Fixed in Code

I updated `config.py` to:
- ✅ Remove the invalid hardcoded database URL
- ✅ Properly use Railway's `DATABASE_URL` environment variable
- ✅ Convert `postgres://` to `postgresql://` (SQLAlchemy requirement)
- ✅ Show clear error if `DATABASE_URL` is missing

## 🚀 Next Steps

1. **Get the correct DATABASE_URL from Railway** (see Step 2 above)
2. **Add it to your web service variables** (if not auto-provided)
3. **Railway will redeploy automatically**
4. **Your app should connect successfully!** ✅
