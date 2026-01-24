#!/usr/bin/env python
"""
Database initialization script
Runs migrations and creates admin user automatically
Works locally (MySQL) or on Railway (PostgreSQL)
"""
import os
import sys
from app import app, db
from models.models import (
    User, Badge, GameStage, UserResponse, QuizQuestion, 
    UserScenarioProgress, UserQuestionHistory, Feedback
)

def init_database():
    """Run migrations and create admin user"""
    with app.app_context():
        try:
            # --- Step 0: Override DB URI if DATABASE_URL exists ---
            database_url = os.environ.get("DATABASE_URL")  # Railway Postgres
            if database_url:
                print(f"🌐 Using DATABASE_URL from environment: {database_url}")
                app.config['SQLALCHEMY_DATABASE_URI'] = database_url
                db.engine.dispose()  # Refresh engine with new URI

            # Step 1: Run migrations or create tables
            print("📦 Initializing database...")

            migrations_versions_dir = os.path.join('migrations', 'versions')
            has_migrations = False
            if os.path.exists(migrations_versions_dir):
                migration_files = [
                    f for f in os.listdir(migrations_versions_dir)
                    if f.endswith('.py') and not f.startswith('__')
                ]
                has_migrations = len(migration_files) > 0

            if has_migrations:
                print("   Using Flask-Migrate...")
                from flask_migrate import upgrade
                upgrade()
                print("✅ Migrations completed successfully!")
            else:
                print("   No migration files found. Creating tables directly...")
                print(f"   Database URI: {db.engine.url}")
                print("   Creating all tables from models...")
                db.create_all()
                db.session.commit()
                print("✅ Tables created successfully!")

            # Step 2: Create admin user
            print("\n👤 Checking for admin user...")
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
                admin_password = os.environ.get('ADMIN_PASSWORD', 'Admin123!')
                admin_user.set_password(admin_password)
                db.session.add(admin_user)
                db.session.commit()
                print("✅ Admin user created successfully!")
                print(f"   Email: admin@funzamama.org")
                print(f"   Password: {admin_password}")
            else:
                if admin_user.role != 'admin':
                    admin_user.role = 'admin'
                    db.session.commit()
                    print("✅ Admin user role updated!")
                else:
                    print("ℹ️ Admin user already exists with admin role.")

            # Step 3: List all tables
            print("\n📋 Database tables:")
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            for table in tables:
                print(f"   - {table}")

            print("\n✅ Database initialization complete!")

        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    init_database()
