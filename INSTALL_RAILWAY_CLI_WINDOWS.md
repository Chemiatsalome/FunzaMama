# Install Railway CLI on Windows

## Method 1: Download from GitHub (Recommended)

### Step 1: Download
1. Go to: https://github.com/railwayapp/cli/releases/latest
2. Download: **`railway-v4.25.2-x86_64-pc-windows-msvc.zip`** (or latest version)
   - This is the ZIP file for 64-bit Windows

### Step 2: Extract
1. Extract the ZIP file
2. You'll get a file named `railway.exe`

### Step 3: Add to PATH (Option A - Easy)
1. **Copy `railway.exe`** to: `C:\Windows\System32\`
2. Now you can use `railway` from anywhere in PowerShell

### Step 3: Add to PATH (Option B - Better Practice)
1. Create a folder: `C:\railway\`
2. **Move `railway.exe`** to `C:\railway\railway.exe`
3. **Add to PATH**:
   - Press `Win + X` → **System** → **Advanced system settings**
   - Click **Environment Variables**
   - Under **User variables**, find **Path** → **Edit**
   - Click **New** → Add: `C:\railway`
   - Click **OK** on all dialogs
4. **Restart PowerShell** (close and reopen)

### Step 4: Verify Installation
```powershell
railway --version
```
Should show: `railway v4.25.2` (or your version)

### Step 5: Login
```powershell
railway login
```
This opens your browser to authenticate.

### Step 6: Link Your Project
```powershell
cd C:\Users\Admin\Desktop\FunzaMama
railway link
```
Select your Railway project when prompted.

### Step 7: Run init_db.py
```powershell
railway run python init_db.py
```

---

## Method 2: Using npm (If you have Node.js)

```powershell
npm i -g @railway/cli
railway --version
railway login
```

---

## Method 3: Using winget (Windows Package Manager)

```powershell
winget install Railway.CLI
railway --version
railway login
```

---

## Quick Test After Installation

```powershell
# Check version
railway --version

# Login
railway login

# Navigate to project
cd C:\Users\Admin\Desktop\FunzaMama

# Link project
railway link

# Run init_db.py to create tables
railway run python init_db.py
```

This will show you all the output from `init_db.py` and create your database tables!
