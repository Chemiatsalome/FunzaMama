# 🚂 Railway Migration Commands

## ✅ Correct Commands for Railway

Railway doesn't have `flask` in PATH, so use `python -m flask` instead:

### Create Migration (if needed):
```bash
railway run python -m flask db migrate -m "Initial schema"
```

### Run Migrations:
```bash
railway run python -m flask db upgrade
```

### Or use the custom command:
```bash
railway run python -m flask migrate
```

## ✅ Quick Fix

Run this command:

```bash
railway run python -m flask db upgrade
```

This will:
1. Create all database tables
2. Fix the `/signup` 500 error
3. Make your app fully functional

## 🔍 Why `python -m flask`?

- Railway's environment might not have `flask` in PATH
- `python -m flask` uses Python's module system to find Flask
- This works reliably in all environments

## ✅ Alternative: Use releaseCommand

I've updated `railway.json` to use `python -m flask db upgrade` in the `releaseCommand`.

**To trigger it:**
1. Make any small change to your code
2. Push to GitHub
3. Railway will automatically run migrations during deployment

## 🆘 Troubleshooting

### If "flask db migrate" is needed first:
```bash
railway run python -m flask db migrate -m "Initial schema"
railway run python -m flask db upgrade
```

### If migrations folder doesn't exist:
```bash
railway run python -m flask db init
railway run python -m flask db migrate -m "Initial schema"
railway run python -m flask db upgrade
```

### Check if it worked:
After running migrations, check Railway logs or database dashboard to see if tables were created.
