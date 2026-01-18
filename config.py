import os

class Config:
    # Database configuration
    # Railway automatically provides either:
    # - DATABASE_URL (for PostgreSQL)
    # - MYSQLHOST, MYSQLUSER, etc. (for MySQL)
    # For local development, use MySQL with XAMPP
    
    # BEST PRACTICE: Check for database variables directly (not FLASK_ENV)
    # Railway doesn't set FLASK_ENV=production by default
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    # Check if DATABASE_URL has internal hostname (won't work locally)
    # If so, try to build from PostgreSQL environment variables (PGHOST, PGPORT, etc.)
    if DATABASE_URL and 'postgres.railway.internal' in DATABASE_URL:
        # Internal hostname detected - try to use public hostname from PGHOST
        pg_host = os.environ.get('PGHOST')
        pg_port = os.environ.get('PGPORT', '5432')
        pg_user = os.environ.get('PGUSER', 'postgres')
        # Safely handle PGPASSWORD - split and take first word if present, otherwise use empty string
        pg_password_raw = os.environ.get('PGPASSWORD', '')
        pg_password_split = pg_password_raw.split()
        pg_password = pg_password_split[0] if pg_password_split else ''
        pg_database = os.environ.get('PGDATABASE', 'railway')
        
        if pg_host:
            # Build DATABASE_URL from PostgreSQL variables
            DATABASE_URL = f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_database}"
            print(f"🌐 Using public PostgreSQL hostname from PGHOST: {pg_host}:{pg_port}")
        else:
            print("⚠️ DATABASE_URL has internal hostname. Set PGHOST for local access.")
    
    if DATABASE_URL:
        # PostgreSQL detected - Railway provides DATABASE_URL
        # Mask password in logs for security
        masked_url = DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else '***'
        print(f"✅ DATABASE_URL loaded: postgresql://***@{masked_url}")
        
        # Railway's DATABASE_URL might use 'postgres://' but SQLAlchemy needs 'postgresql://'
        if DATABASE_URL.startswith('postgres://'):
            SQLALCHEMY_DATABASE_URI = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        elif DATABASE_URL.startswith('postgresql://'):
            SQLALCHEMY_DATABASE_URI = DATABASE_URL
        else:
            # If it doesn't start with postgres/postgresql, assume it needs the prefix
            SQLALCHEMY_DATABASE_URI = f'postgresql://{DATABASE_URL}' if not DATABASE_URL.startswith('postgresql://') else DATABASE_URL
    else:
        # Check for MySQL variables (Railway MySQL)
        mysql_host = os.environ.get('MYSQLHOST')
        mysql_user = os.environ.get('MYSQLUSER')
        mysql_password = os.environ.get('MYSQLPASSWORD')
        mysql_database = os.environ.get('MYSQLDATABASE')
        mysql_port = os.environ.get('MYSQLPORT', '3306')
        
        if mysql_host and mysql_user and mysql_database:
            # Build MySQL connection string from Railway MySQL variables
            SQLALCHEMY_DATABASE_URI = (
                f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@"
                f"{mysql_host}:{mysql_port}/{mysql_database}"
            )
            print(f"✅ Using MySQL from Railway variables: {mysql_host}:{mysql_port}/{mysql_database}")
        else:
            # Local development - use MySQL with XAMPP
            SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root@localhost/funzamama_db'
            print("ℹ️ Using local MySQL (XAMPP) for development")

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'my_secret_key'
    
    # Server configuration for URL generation
    # For local development, use localhost
    # For production, set this to your domain (e.g., 'funzamama.org')
    # Railway: Set SERVER_NAME in Railway Dashboard → Variables to override
    SERVER_NAME = os.environ.get('SERVER_NAME') or None  # None allows Flask to auto-detect
    
    # Prefer HTTPS in production (Railway uses HTTPS)
    # Detect production by checking if PORT is set (Railway sets this)
    if os.environ.get('PORT') and not os.environ.get('FLASK_ENV') == 'development':
        PREFERRED_URL_SCHEME = os.environ.get('PREFERRED_URL_SCHEME') or 'https'
    else:
        PREFERRED_URL_SCHEME = os.environ.get('PREFERRED_URL_SCHEME') or 'http'
    
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
    # Email Credentials - MUST be set via environment variables for security
    # Set these in Railway Dashboard → Variables:
    #   MAIL_USERNAME = chemiatsalome@gmail.com
    #   MAIL_PASSWORD = wloqvskriwrlzcrp (your Gmail app password)
    # 
    # SECURITY: Never hardcode passwords in code!
    # The app password should be 16 characters with NO SPACES
    # Email Credentials - MUST be set via environment variables for security
    # For local development: Set in .env file (already in .gitignore)
    # For Railway production: Set in Railway Dashboard → Variables
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'chemiatsalome@gmail.com'
    MAIL_PASSWORD = (os.environ.get('MAIL_PASSWORD') or '').strip()  # REQUIRED: Set in .env (local) or Railway Variables (production)
    
    if not MAIL_PASSWORD:
        print("⚠️ WARNING: MAIL_PASSWORD not set! Email features will not work.")
        print("⚠️ For local: Set MAIL_PASSWORD in .env file")
        print("⚠️ For Railway: Set MAIL_PASSWORD in Railway Dashboard → Variables")

