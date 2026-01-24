#!/usr/bin/env python3
"""
Diagnostic script to check database connection and count users.
Run this on Railway to verify database connectivity and user count.

Usage:
    python check_database_users.py
"""

import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from models.models import User, db
from sqlalchemy import text

def check_database():
    """Check database connection and user count"""
    print("=" * 60)
    print("DATABASE DIAGNOSTIC CHECK")
    print("=" * 60)
    
    with app.app_context():
        try:
            # Check database connection
            print("\n1. Checking database connection...")
            db.engine.connect()
            print("   ✅ Database connection successful")
            
            # Get database URL (masked)
            db_url = app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')
            if '@' in db_url:
                masked_url = db_url.split('@')[1] if '@' in db_url else '***'
                print(f"   Database: postgresql://***@{masked_url}")
            else:
                print(f"   Database: {db_url[:50]}...")
            
            # Check if users table exists
            print("\n2. Checking if 'users' table exists...")
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            if 'users' in tables:
                print("   ✅ 'users' table exists")
            else:
                print("   ❌ 'users' table NOT FOUND!")
                print(f"   Available tables: {', '.join(tables)}")
                return
            
            # Count users
            print("\n3. Counting users in database...")
            user_count = User.query.count()
            print(f"   📊 Total users: {user_count}")
            
            # Get user details
            if user_count > 0:
                print("\n4. User details:")
                users = User.query.order_by(User.created_at.desc()).limit(10).all()
                for i, user in enumerate(users, 1):
                    print(f"   {i}. ID: {user.user_ID}, Username: {user.username}, Email: {user.email}, Created: {user.created_at}")
                
                if user_count > 10:
                    print(f"   ... and {user_count - 10} more users")
            else:
                print("   ⚠️ No users found in database!")
            
            # Check for recent signups (last 24 hours)
            print("\n5. Recent signups (last 24 hours)...")
            from datetime import datetime, timedelta
            yesterday = datetime.utcnow() - timedelta(days=1)
            recent_users = User.query.filter(User.created_at >= yesterday).count()
            print(f"   📅 Users created in last 24 hours: {recent_users}")
            
            # Test database write
            print("\n6. Testing database write capability...")
            test_query = text("SELECT 1")
            result = db.session.execute(test_query).scalar()
            if result == 1:
                print("   ✅ Database write test successful")
            else:
                print("   ⚠️ Database write test returned unexpected result")
            
            # Check database connection pool
            print("\n7. Database connection pool info...")
            pool = db.engine.pool
            print(f"   Pool size: {pool.size()}")
            print(f"   Checked out: {pool.checkedout()}")
            print(f"   Overflow: {pool.overflow()}")
            
            print("\n" + "=" * 60)
            print("DIAGNOSTIC COMPLETE")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            return

if __name__ == '__main__':
    check_database()
