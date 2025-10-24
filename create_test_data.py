#!/usr/bin/env python3
"""
Create test data for Funza Mama admin dashboard
This script adds sample user responses to populate analytics
"""

import mysql.connector
from datetime import datetime, timedelta
import random

def create_test_data():
    """Create test user responses for analytics"""
    
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
        
        # Get all users
        cursor.execute("SELECT user_ID, first_name, second_name FROM users")
        users = cursor.fetchall()
        
        if not users:
            print("No users found. Please create some users first.")
            return
        
        print(f"Found {len(users)} users")
        
        # Stages to create data for
        stages = ['preconception', 'antenatal', 'birth', 'postnatal']
        
        # Create test responses for each user
        for user_id, first_name, second_name in users:
            if first_name == 'Admin':  # Skip admin user
                continue
                
            print(f"Creating test data for {first_name} {second_name} (ID: {user_id})")
            
            # Create responses for each stage
            for stage in stages:
                # Create 3-5 responses per stage with some correct/incorrect
                num_responses = random.randint(3, 5)
                
                for i in range(num_responses):
                    # Randomly determine if response is correct (70% chance)
                    is_correct = random.random() < 0.7
                    
                    # Create response
                    cursor.execute("""
                        INSERT INTO user_responses 
                        (user_id, selected_option, is_correct, attempt_number, stage, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        user_id,
                        f"Option {'A' if is_correct else 'B'}",
                        is_correct,
                        i + 1,
                        stage,
                        datetime.now() - timedelta(days=random.randint(0, 30))
                    ))
        
        # Create some feedback entries
        feedback_messages = [
            "Great app! Very helpful for learning about maternal health.",
            "The questions are challenging but educational.",
            "Would love to see more interactive features.",
            "Some questions seem too difficult for beginners.",
            "Excellent content, keep up the good work!",
            "The app crashes sometimes on mobile.",
            "More visual content would be helpful.",
            "Great job on the user interface!"
        ]
        
        categories = ['general', 'bug', 'feature', 'content']
        
        for i in range(5):
            cursor.execute("""
                INSERT INTO feedback 
                (user_name, email, category, message, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                f"Test User {i+1}",
                f"testuser{i+1}@example.com",
                random.choice(categories),
                random.choice(feedback_messages),
                random.choice(['pending', 'reviewed', 'resolved']),
                datetime.now() - timedelta(days=random.randint(0, 15))
            ))
        
        # Commit changes
        connection.commit()
        print("Test data created successfully!")
        
        # Show summary
        cursor.execute("SELECT COUNT(*) FROM user_responses")
        response_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM feedback")
        feedback_count = cursor.fetchone()[0]
        
        print(f"Created {response_count} user responses")
        print(f"Created {feedback_count} feedback entries")
        
    except mysql.connector.Error as err:
        print(f"MySQL Error: {err}")
        
    except Exception as e:
        print(f"Error: {e}")
        
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed.")

if __name__ == "__main__":
    print("Creating test data for Funza Mama admin dashboard")
    print("=" * 50)
    create_test_data()
