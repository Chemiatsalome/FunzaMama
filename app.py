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

# Initialize database connection (lazy - doesn't connect until first use)
db.init_app(app)
migrate = Migrate(app, db)

# Ensure database connection is lazy (don't connect at import time)
# SQLAlchemy will connect only when first query is made

# Initialize Mail only if available
if MAIL_AVAILABLE:
    mail = Mail(app)
else:
    mail = None


# Import models to register them (but don't run DB operations at import time!)
# Database operations should be done via Flask-Migrate or CLI commands, not at import time
# This prevents blocking Gunicorn from starting on Render
from models.models import *

# NOTE: Database initialization (db.create_all(), admin creation, etc.) has been removed
# from import time to prevent blocking Gunicorn startup on Render.
# 
# To initialize the database:
# 1. Use Flask-Migrate: flask db upgrade
# 2. Create admin user via CLI command (see below)
#
# For local development, you can still run: python app.py
# For production (Render), Gunicorn will start the app without blocking

# Fallback: Create tables on first request if they don't exist (only runs once)
# This ensures tables are created even if releaseCommand fails
import threading
_tables_created = False
_table_creation_lock = threading.Lock()

def create_tables_if_not_exist():
    """Create database tables if they don't exist - fallback for when releaseCommand fails"""
    global _tables_created
    if _tables_created:
        return
    
    with _table_creation_lock:
        if _tables_created:  # Double-check pattern
            return
        
        try:
            with app.app_context():
                # Check if users table exists
                from sqlalchemy import inspect
                inspector = inspect(db.engine)
                existing_tables = inspector.get_table_names()
                
                # Only create if tables don't exist
                if 'users' not in existing_tables:
                    print("⚠️ Tables not found. Creating them now...")
                    db.create_all()
                    print("✅ Tables created successfully!")
                    
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
                        import os
                        admin_user.set_password(os.environ.get('ADMIN_PASSWORD', 'Admin123!'))
                        db.session.add(admin_user)
                        db.session.commit()
                        print("✅ Admin user created!")
                else:
                    print("✅ Database tables already exist.")
                _tables_created = True
        except Exception as e:
            print(f"⚠️ Warning: Could not create tables on startup: {e}")
            # Don't fail the app, just log the warning

@app.before_request
def ensure_tables_exist():
    """Ensure tables exist before handling requests"""
    create_tables_if_not_exist()


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

# CLI command to create admin user (run once: flask create-admin)
@app.cli.command("create-admin")
def create_admin():
    """Create admin user - run once: flask create-admin"""
    with app.app_context():
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
            print("✅ Admin user created successfully!")
        else:
            # Update existing admin user to have admin role
            if admin_user.role != 'admin':
                admin_user.role = 'admin'
                db.session.commit()
                print("✅ Admin user role updated!")
            else:
                print("ℹ️ Admin user already exists with admin role.")

# CLI command to run migrations (alternative to flask db upgrade)
@app.cli.command("migrate")
def migrate_db():
    """Run database migrations - run: flask migrate"""
    from flask_migrate import upgrade, migrate
    import sys
    
    with app.app_context():
        try:
            print("📦 Running database migrations...")
            upgrade()
            print("✅ Migrations completed successfully!")
            
            # List tables
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            if tables:
                print(f"\n📋 Database tables ({len(tables)}):")
                for table in tables:
                    print(f"   - {table}")
            else:
                print("\n⚠️ No tables found. Run 'flask db migrate' first.")
        except Exception as e:
            print(f"❌ Migration error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 5000))  # Get the port from environment variables, default to 5000
#     app.run(host="0.0.0.0", port=port)

import os

# This block is for local development only
# On Render, Gunicorn will start the app using: gunicorn app:app --bind 0.0.0.0:$PORT
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)  # debug=False for production
