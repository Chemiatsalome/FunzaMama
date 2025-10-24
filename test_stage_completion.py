#!/usr/bin/env python3
"""
Test script to verify stage completion calculation
"""

import mysql.connector
from datetime import datetime, timedelta

def test_stage_completion():
    """Test the stage completion calculation"""
    
    # Database connection parameters
    config = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'funzamama_db',
        'port': 3306
    }
    
    try:
        # Connect to MySQL
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        print("Testing Stage Completion Calculation")
        print("=" * 40)
        
        # Get total users (excluding admin)
        cursor.execute("SELECT COUNT(*) FROM users WHERE role != 'admin'")
        total_users = cursor.fetchone()[0]
        print(f"Total users (excluding admin): {total_users}")
        
        stages = ['preconception', 'antenatal', 'birth', 'postnatal']
        
        for stage in stages:
            print(f"\n--- {stage.upper()} STAGE ---")
            
            # Get users who have attempted this stage
            cursor.execute("""
                SELECT user_id, 
                       COUNT(*) as total_attempts,
                       AVG(CASE WHEN is_correct = 1 THEN 100 ELSE 0 END) as avg_score
                FROM user_responses 
                WHERE stage = %s 
                GROUP BY user_id
            """, (stage,))
            
            stage_attempts = cursor.fetchall()
            print(f"Users who attempted {stage}: {len(stage_attempts)}")
            
            # Count users who have "completed" the stage (5+ attempts with 70%+ average score)
            completed_users = 0
            for user_id, total_attempts, avg_score in stage_attempts:
                is_completed = total_attempts >= 5 and avg_score >= 70
                print(f"  User {user_id}: {total_attempts} attempts, {avg_score:.1f}% avg score, Completed: {is_completed}")
                if is_completed:
                    completed_users += 1
            
            # Calculate completion rate
            if total_users > 0:
                completion_rate = round((completed_users / total_users) * 100, 1)
            else:
                completion_rate = 0
                
            print(f"Completed users: {completed_users}/{total_users} ({completion_rate}%)")
        
    except mysql.connector.Error as err:
        print(f"MySQL Error: {err}")
        
    except Exception as e:
        print(f"Error: {e}")
        
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("\nMySQL connection closed.")

if __name__ == "__main__":
    test_stage_completion()
