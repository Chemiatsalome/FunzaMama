from flask import Flask, render_template, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db  # Import db from models/__init__.py
from models.models import User, Badge, GameStage, UserResponse, QuizQuestion, UserScenarioProgress # Import models
from flask_cors import CORS
from dotenv import load_dotenv

# Try to import Flask-Mail, but don't fail if it's not available
try:
    from flask_mail import Mail
    MAIL_AVAILABLE = True
except ImportError:
    MAIL_AVAILABLE = False
    print("Flask-Mail not available. Email features will be disabled.")


app = Flask(__name__)


CORS(app, supports_credentials=True)

load_dotenv()


app.config.from_object('config.Config')

db.init_app(app)
migrate = Migrate(app, db)

# Initialize Mail only if available
if MAIL_AVAILABLE:
    mail = Mail(app)
else:
    mail = None


# Import models to register them
with app.app_context():
    from models.models import *
    
    try:
        # Try to create tables first
        db.create_all()
        
        # Create admin user if it doesn't exist
        admin_user = User.query.filter_by(email='admin@funzamama.org').first()
        if not admin_user:
            admin_user = User(
                first_name='Admin',
                second_name='User',
                username='admin',
                email='admin@funzamama.org',
                email_verified=True,
                avatar='images/avatars/admin.png',
                role='admin'
            )
            admin_user.set_password('Admin123!')  # Change this password in production
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created successfully!")
        else:
            # Update existing admin user to have admin role
            if admin_user.role != 'admin':
                admin_user.role = 'admin'
                db.session.commit()
                print("Admin user role updated!")
    except Exception as e:
        print(f"Database initialization warning: {e}")
        print("Please run the migration script (migrate_database.sql) to update your database schema.")
        print("The application will still work for guest users, but some features may be limited.")


from routes.auth_routes import Login_bp, signup_bp
from routes.system_routes import home_bp, gamestages_bp, profile_bp
from routes.gamestage_routes import preconceptionstage_bp, prenatalstage_bp , birthstage_bp , postnatalstage_bp
from routes.gamelogic import quiz_bp
from routes.feedback_routes import feedback_bp

# Try to import admin routes, but don't fail if dependencies are missing
admin_bp = None
admin_available = False
try:
    from routes.admin_routes import admin_bp
    admin_available = True
except ImportError as e:
    print(f"Admin routes not available: {e}")
    admin_available = False
# Register Blueprints (modular routes)
app.register_blueprint(Login_bp)
app.register_blueprint(signup_bp)
app.register_blueprint(home_bp)
app.register_blueprint(gamestages_bp)
app.register_blueprint(preconceptionstage_bp)
app.register_blueprint(prenatalstage_bp)
app.register_blueprint(birthstage_bp )
app.register_blueprint(postnatalstage_bp)
app.register_blueprint(quiz_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(feedback_bp)

# Register admin routes only if available
if admin_available:
    app.register_blueprint(admin_bp)
    print("Admin routes registered successfully!")


# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 5000))  # Get the port from environment variables, default to 5000
#     app.run(host="0.0.0.0", port=port)

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # 10000 is Render's default
    app.run(host="0.0.0.0", port=port, debug=True)  # debug=False for production

