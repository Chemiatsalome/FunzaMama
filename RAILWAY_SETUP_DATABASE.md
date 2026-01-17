# 🗄️ Setting Up Railway Database and Creating Tables

## Step 1: Get DATABASE_URL from Railway

### Option A: Railway Auto-Provides (Recommended)

1. Go to **Railway Dashboard** → Your **Web Service** (FunzaMama app)
2. Click **"Variables"** tab
3. Look for `DATABASE_URL` in the list
4. If it's there, Railway is providing it automatically ✅

### Option B: Get It Manually

If `DATABASE_URL` is NOT in your web service variables:

1. Go to Railway Dashboard → Your **Database Service** (`funzamama-db`)
2. Click **"Variables"** tab
3. Find `DATABASE_URL` or `POSTGRES_URL`
4. Copy the entire connection string (it looks like: `postgresql://postgres:password@host:port/railway`)
5. Go to your **Web Service** → **Variables** tab
6. Click **"+ New Variable"**
7. Name: `DATABASE_URL`
8. Value: Paste the connection string
9. Click **"Add"**

### Option C: Connect Database to Web Service

1. Go to Railway Dashboard → Your **Web Service**
2. Click **"Variables"** tab
3. Look for message: **"Trying to connect a database? Add Variable"**
4. Click **"Add Variable"** → Select your database service (`funzamama-db`)
5. Railway will automatically add `DATABASE_URL`

## Step 2: Create Database Tables

After `DATABASE_URL` is set, you need to create the tables. You have two options:

### Option A: Using Flask-Migrate (Recommended)

1. **Connect to Railway via Railway CLI or SSH:**

   **Using Railway CLI:**
   ```bash
   railway login
   railway link  # Link to your project
   railway run flask db upgrade
   ```

   **Or using Railway Dashboard:**
   - Go to Railway Dashboard → Your **Web Service**
   - Click **"Settings"** tab
   - Scroll to **"Deploy Logs"** or use **"View Logs"**
   - Or use **"Deploy"** → **"Run Command"** → Enter: `flask db upgrade`

2. **If migrations don't exist, create them first:**
   ```bash
   railway run flask db init  # Only if migrations folder doesn't exist
   railway run flask db migrate -m "Initial migration"
   railway run flask db upgrade
   ```

### Option B: Using db.create_all() (Quick but not recommended for production)

1. **Connect to Railway:**
   ```bash
   railway run python
   ```

2. **In Python shell:**
   ```python
   from app import app, db
   with app.app_context():
       db.create_all()
       print("✅ Tables created!")
   ```

## Step 3: Verify Tables Are Created

1. Go to Railway Dashboard → Your **Database Service** (`funzamama-db`)
2. Click **"Database"** tab → **"Data"** tab
3. You should see tables like:
   - `user`
   - `badge`
   - `game_stage`
   - `user_response`
   - `quiz_question`
   - `user_scenario_progress`
   - `alembic_version` (for migrations)

## Step 4: Create Admin User (Optional)

After tables are created, create an admin user:

```bash
railway run flask create-admin
```

This creates an admin user:
- Email: `admin@funzamama.org`
- Password: `Admin123!` (change this in production!)

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

**If tables don't create:**

1. Check Railway logs for errors
2. Verify `DATABASE_URL` format is correct
3. Make sure `FLASK_ENV=production` is set
4. Try `railway run flask db upgrade` again

**If app still crashes:**

1. Check Railway logs for the exact error
2. Verify all environment variables are set:
   - `DATABASE_URL` ✅
   - `FLASK_ENV=production` ✅
   - `SECRET_KEY` ✅

## ✅ Success Checklist

- [ ] `DATABASE_URL` is set in Railway web service variables
- [ ] Database service is "Online"
- [ ] Ran `flask db upgrade` successfully
- [ ] Tables appear in Railway database dashboard
- [ ] App starts without errors
- [ ] Can access the app URL
