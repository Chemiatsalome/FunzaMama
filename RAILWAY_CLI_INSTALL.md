# How to Install and Use Railway CLI

## Install Railway CLI

### Windows (PowerShell)
```powershell
# Using npm (if you have Node.js installed)
npm i -g @railway/cli

# OR using winget
winget install Railway.CLI

# OR using Scoop
scoop bucket add railway https://github.com/railwayapp/homebrew-tap
scoop install railway
```

### Alternative: Download Binary
1. Go to: https://github.com/railwayapp/cli/releases
2. Download `railway-windows-amd64.exe`
3. Rename to `railway.exe`
4. Add to your PATH or use full path

## Login to Railway
```bash
railway login
```
This will open your browser to authenticate.

## Link to Your Project
```bash
# Navigate to your project directory
cd C:\Users\Admin\Desktop\FunzaMama

# Link to your Railway project
railway link
```

## Run init_db.py
```bash
railway run python init_db.py
```

This will:
- Connect to your Railway database
- Run the script on Railway's servers
- Show you all the output in real-time

## Check Deployment Logs
```bash
# View recent logs
railway logs

# View logs for a specific service
railway logs --service your-service-name
```
