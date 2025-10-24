import os

class Config:
    # Check for the environment variable for the production URI
    if os.environ.get('FLASK_ENV') == 'production':
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://funzamama_db_user:o23lLt5Kl3tVoeHDOvqpPwcrU16wlzG3@dpg-d037v26uk2gs73ebrb70-a/funzamama_db')
    else:
        # Use MySQL locally with XAMPP
        SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root@localhost/funzamama_db'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'my_secret_key'
    
    # Email configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'noreply@funzamama.org'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or ''
