#!/usr/bin/env python
"""
Script to run database migrations on Railway
Usage: python run_migrations.py
"""
import os
import sys
from app import app, db

def run_migrations():
    """Run Flask-Migrate upgrade to create/update database tables"""
    with app.app_context():
        try:
            # Check if DATABASE_URL is set
            database_url = os.environ.get('DATABASE_URL')
            if not database_url:
                print("❌ ERROR: DATABASE_URL not found!")
                print("   Set DATABASE_URL in Railway Dashboard → Variables")
                sys.exit(1)
            
            # Mask password in logs
            masked_url = database_url.split('@')[1] if '@' in database_url else '***'
            print(f"✅ DATABASE_URL found: postgresql://***@{masked_url}")
            
            # Check current database URI
            print(f"📊 Using database: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set').split('@')[1] if '@' in app.config.get('SQLALCHEMY_DATABASE_URI', '') else 'Not set'}")
            
            # Try to connect to database
            print("🔌 Testing database connection...")
            db.engine.connect()
            print("✅ Database connection successful!")
            
            # Run migrations
            print("📦 Running database migrations...")
            from flask_migrate import upgrade
            upgrade()
            print("✅ Migrations completed successfully!")
            
            # List all tables
            print("\n📋 Current database tables:")
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            if tables:
                for table in tables:
                    print(f"   - {table}")
            else:
                print("   ⚠️ No tables found. Run 'flask db migrate' first.")
            
            print("\n✅ Database setup complete!")
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    run_migrations()
