# 🔧 Local Development .env Setup

## ✅ Create .env File for Local Development

Since `.env` is in `.gitignore`, you need to create it manually:

### Option 1: Create .env File Manually

Create a file named `.env` in your project root with:

```env
# Local Development Environment Variables
# This file is in .gitignore and will NOT be committed to GitHub

# Email Configuration (for local development)
MAIL_USERNAME=chemiatsalome@gmail.com
MAIL_PASSWORD=wloqvskriwrlzcrp

# Database Configuration (for local development)
# Use MySQL locally with XAMPP
# FLASK_ENV is not set, so it will use local MySQL

# Secret Key (for local development)
SECRET_KEY=my_secret_key_for_local_development
```

### Option 2: Use PowerShell (if .env doesn't exist)

```powershell
@"
# Local Development Environment Variables
# This file is in .gitignore and will NOT be committed to GitHub

# Email Configuration (for local development)
MAIL_USERNAME=chemiatsalome@gmail.com
MAIL_PASSWORD=wloqvskriwrlzcrp

# Database Configuration (for local development)
# Use MySQL locally with XAMPP
# FLASK_ENV is not set, so it will use local MySQL

# Secret Key (for local development)
SECRET_KEY=my_secret_key_for_local_development
"@ | Out-File -FilePath .env -Encoding utf8
```

## ✅ After Creating .env

1. **Restart your local Flask app** (if running)
2. **The email password will be loaded** from `.env`
3. **No more warnings** about `MAIL_PASSWORD` not set

## 🔐 Security Note

- ✅ `.env` is in `.gitignore` - it won't be committed
- ✅ Password is only stored locally
- ⚠️ Don't commit `.env` to GitHub!

## 🆘 If .env Doesn't Work

Make sure:
1. `.env` file is in the **project root** (same folder as `app.py`)
2. File name is exactly `.env` (with the dot at the start)
3. Restart your Flask app after creating `.env`
4. Check that `python-dotenv` is installed: `pip install python-dotenv`
