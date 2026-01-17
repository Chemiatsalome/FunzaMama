# 🚂 Railway CLI Setup - Run Migrations Remotely

## Why Railway CLI?

Railway dashboard doesn't have a built-in terminal, but **Railway CLI** lets you run commands on Railway's servers remotely.

## ✅ Step 1: Install Railway CLI

**On Windows (PowerShell):**
```powershell
npm install -g @railway/cli
```

**Or using Chocolatey:**
```powershell
choco install railway-cli
```

**Or download directly:**
- Go to: https://github.com/railwayapp/cli/releases
- Download the Windows executable
- Add it to your PATH

## ✅ Step 2: Login to Railway

```bash
railway login
```

This will open your browser to authenticate.

## ✅ Step 3: Link to Your Project

```bash
railway link
```

Select your FunzaMama project when prompted.

## ✅ Step 4: Run Migrations on Railway

Now you can run commands on Railway's servers:

```bash
railway run flask db upgrade
```

This runs `flask db upgrade` **on Railway's servers**, so it can access `postgres.railway.internal`.

## ✅ Alternative: Use Railway's Release Command

I've already added `"releaseCommand": "flask db upgrade"` to `railway.json`.

**To trigger it:**
1. Make a small change to your code (or just push again)
2. Railway will automatically run `flask db upgrade` during deployment

## 🆘 Troubleshooting

### If Railway CLI not found:
```bash
# Check if installed
railway --version

# If not found, install via npm
npm install -g @railway/cli
```

### If "project not found":
```bash
railway link
# Select your project from the list
```

### If migrations fail:
```bash
# Create migration first (if needed)
railway run flask db migrate -m "Initial schema"
railway run flask db upgrade
```

## ✅ Quick Commands

```bash
# Login
railway login

# Link project
railway link

# Run migrations
railway run flask db upgrade

# Check logs
railway logs

# View variables
railway variables
```
