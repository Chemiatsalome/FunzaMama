import os

class Config:
    # Check for the environment variable for the production URI
    if os.environ.get('FLASK_ENV') == 'production':
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://funzamama_db_user:o23lLt5Kl3tVoeHDOvqpPwcrU16wlzG3@dpg-d037v26uk2gs73ebrb70-a/funzamama_db')
    else:
        # Use MySQL locally by default
        SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root@localhost/funzamama_db'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'my_secret_key'
