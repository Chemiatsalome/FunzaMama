import os

class Config:
    # Database configuration
    # Railway automatically provides DATABASE_URL when PostgreSQL service is connected
    # For production, use Railway's DATABASE_URL (automatically provided)
    # For local development, use MySQL
    if os.environ.get('FLASK_ENV') == 'production':
        # Railway automatically provides DATABASE_URL when PostgreSQL is connected
        # Get it from: Railway Dashboard → Database Service → Variables tab → DATABASE_URL
        DATABASE_URL = os.environ.get('DATABASE_URL')
        if not DATABASE_URL:
            raise ValueError(
                "DATABASE_URL not found! "
                "Railway should automatically provide this when PostgreSQL is connected. "
                "Check: Railway Dashboard → Database Service → Variables tab"
            )
        # Railway's DATABASE_URL might use 'postgres://' but SQLAlchemy needs 'postgresql://'
        SQLALCHEMY_DATABASE_URI = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    else:
        # Use MySQL locally with XAMPP
        SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root@localhost/funzamama_db'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'my_secret_key'
    
    # Server configuration for URL generation
    # For local development, use localhost
    # For production, set this to your domain (e.g., 'funzamama.org')
    SERVER_NAME = os.environ.get('SERVER_NAME') or None  # None allows Flask to auto-detect
    PREFERRED_URL_SCHEME = os.environ.get('PREFERRED_URL_SCHEME') or 'http'  # Use 'https' in production
    APPLICATION_ROOT = os.environ.get('APPLICATION_ROOT') or '/'
    
    # Email configuration
    # For Strathmore University email, they may use Office 365 or Gmail
    # Office 365: smtp.office365.com, Port 587
    # Gmail: smtp.gmail.com, Port 587 (requires App Password)
    # You can set these via environment variables or update directly here
    
    # SMTP Server Configuration
    # Office 365 often requires app passwords or has SMTP disabled
    # If Office 365 doesn't work, try Gmail (smtp.gmail.com) with an app password
    # 
    # Option 1: Office 365 (requires app password if MFA is enabled)
    #   - Get app password: https://account.microsoft.com/security > App passwords
    #   - SMTP might need to be enabled by admin
    # Option 2: Gmail (easier to set up, requires app password)
    #   - Get app password: https://myaccount.google.com/apppasswords
    #   - Must enable 2-Step Verification first
    # IMPORTANT: Since you're using Gmail (chemiatsalome@gmail.com), use Gmail's SMTP server
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'  # Gmail SMTP (required for Gmail accounts)
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    
    # Email Credentials - UPDATE THESE WITH YOUR ACTUAL CREDENTIALS
    # Option 1: Set directly here (less secure, but works immediately)
    # Option 2: Use environment variables (more secure)
    # 
    # For Windows PowerShell:
    #   $env:MAIL_USERNAME="schemiat@strathmore.edu"
    #   $env:MAIL_PASSWORD="your-actual-password"
    #
    # For Windows CMD:
    #   set MAIL_USERNAME=schemiat@strathmore.edu
    #   set MAIL_PASSWORD=your-actual-password
    #
    # For Linux/Mac:
    #   export MAIL_USERNAME="schemiat@strathmore.edu"
    #   export MAIL_PASSWORD="your-actual-password"
    
    # Email Credentials
    # For Office 365: You may need an APP PASSWORD (not your regular password)
    # For Gmail: You MUST use an APP PASSWORD (not your regular password)
    # 
    # To get a Gmail App Password:
    # 1. Go to Google Account > Security
    # 2. Enable 2-Step Verification
    # 3. Go to App passwords > Generate password for "Mail"
    # 4. Use that 16-character password here
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'chemiatsalome@gmail.com'
    # IMPORTANT: Use your Gmail APP PASSWORD (not your regular password)
    # The app password should be 16 characters with NO SPACES
    # From your screenshot: "wloq vskr iwrl zcrp" → use "wloqvskriwrlzcrp" (remove spaces)
    # If you have a different app password, paste it here WITHOUT spaces
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'wloqvskriwrlzcrp'  # Gmail app password (no spaces)

