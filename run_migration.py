#!/usr/bin/env python3
"""
Database Migration Script for Funza Mama
This script will add the missing columns to the existing database.
"""

import mysql.connector
from config import Config
import os

def run_migration():
    """Run the database migration to add missing columns."""
    
    # Database connection parameters
    config = {
        'host': 'localhost',
        'user': 'root',  # Default XAMPP MySQL user
        'password': '',  # Default XAMPP MySQL password (empty)
        'database': 'funzamama_db',
        'port': 3306
    }
    
    try:
        # Connect to MySQL
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        print("Connected to MySQL database successfully!")
        
        # Check if columns already exist
        cursor.execute("DESCRIBE users")
        columns = [row[0] for row in cursor.fetchall()]
        
        print(f"Current columns in users table: {columns}")
        
        # Add missing columns if they don't exist
        if 'email_verified' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN email_verified tinyint(1) DEFAULT 0 AFTER avatar")
            print("Added email_verified column")
        
        if 'email_verification_token' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN email_verification_token varchar(255) DEFAULT NULL AFTER email_verified")
            print("Added email_verification_token column")
            
        if 'last_login' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN last_login datetime DEFAULT NULL AFTER email_verification_token")
            print("Added last_login column")
            
        if 'created_at' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN created_at datetime DEFAULT CURRENT_TIMESTAMP AFTER last_login")
            print("Added created_at column")
            
        if 'role' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN role varchar(20) DEFAULT 'user' AFTER created_at")
            print("Added role column")
        
        # Create feedback table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id int(11) NOT NULL AUTO_INCREMENT,
                created_at datetime DEFAULT CURRENT_TIMESTAMP,
                user_name varchar(100) NOT NULL,
                email varchar(255) NOT NULL,
                category varchar(50) NOT NULL,
                message text NOT NULL,
                status varchar(20) DEFAULT 'pending',
                admin_reply text DEFAULT NULL,
                screenshot_path varchar(255) DEFAULT NULL,
                PRIMARY KEY (id),
                KEY status (status),
                KEY category (category)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        print("Created/verified feedback table")
        
        # Update existing users to have email_verified = 1 (for backward compatibility)
        cursor.execute("UPDATE users SET email_verified = 1 WHERE email_verified IS NULL")
        print("Updated existing users to have email_verified = 1")
        
        # Set admin user role
        cursor.execute("UPDATE users SET role = 'admin' WHERE email = 'admin@funzamama.org'")
        print("Set admin user role")
        
        # Commit changes
        connection.commit()
        print("Migration completed successfully!")
        
    except mysql.connector.Error as err:
        print(f"MySQL Error: {err}")
        print("\nPlease make sure:")
        print("1. XAMPP is running")
        print("2. MySQL service is started")
        print("3. The database 'funzamama_db' exists")
        print("4. You have the correct MySQL credentials")
        
    except Exception as e:
        print(f"Error: {e}")
        
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed.")

if __name__ == "__main__":
    print("Funza Mama Database Migration")
    print("=" * 40)
    run_migration()
