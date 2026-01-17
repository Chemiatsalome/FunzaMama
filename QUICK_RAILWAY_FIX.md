# 🚀 Quick Railway Database Fix

## The Problem
- Internal Server Error
- Railway didn't auto-generate `DATABASE_URL`
- You created your own `DATABASE_URL`

## ✅ Quick Fix (3 Steps)

### Step 1: Delete Your Manual DATABASE_URL

1. Go to **Railway Dashboard** → Your **Web Service** (`FunzaMama`)
2. Click **"Variables"** tab
3. Find `DATABASE_URL` in the list
4. Click the **trash icon** to delete it

### Step 2: Connect Database to Web Service

1. Still in **Variables** tab
2. Look for **"Connect Database"** or **"Reference Variable"** button
3. Click it
4. Select your PostgreSQL database: **`funzamama-db`**
5. Railway will **automatically add** `DATABASE_URL`

### Step 3: Verify Required Variables

Make sure these are set:

✅ **SECRET_KEY** = `w12hClWwR49l9-MNbfby1pRyVKosOiPZCsKAJiXd-ss`  
✅ **FLASK_ENV** = `production`  
✅ **DATABASE_URL** = (Auto-generated - don't add manually!)

---

## 🔍 If "Connect Database" Button is Missing

1. Go to **Railway Dashboard** → Your **PostgreSQL Database** (`funzamama-db`)
2. Click **"Variables"** tab
3. Copy the connection string (looks like `postgresql://postgres:...@...:5432/railway`)
4. Go back to **Web Service** → **Variables**
5. Add `DATABASE_URL` = (paste the connection string)

**Important:** Make sure it starts with `postgresql://` (not `postgres://`)

---

## ✅ After Fixing

Railway will automatically redeploy. Check logs for:
- ✅ `Database connection successful`
- ✅ No more "Internal Server Error"

---

## 🆘 Still Getting Errors?

Share the **exact error message** from Railway logs:
1. Railway Dashboard → Web Service → **Deployments**
2. Click latest deployment
3. Check **logs** for red error messages
