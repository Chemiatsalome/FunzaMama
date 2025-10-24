#!/usr/bin/env python3
"""
Simple Seed Data Generator for Funza Mama Admin Testing
Creates realistic test data without importing the full app
"""

import mysql.connector
from datetime import datetime, timedelta
import random
import json

def connect_to_db():
    """Connect to MySQL database"""
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='funzamama_db'
    )

def create_users():
    """Create diverse test users"""
    conn = connect_to_db()
    cursor = conn.cursor()
    
    users_data = [
        # Young mothers (18-25)
        ("Aisha", "Johnson", "aisha_j", "aisha@example.com", 22, "female"),
        ("Maria", "Garcia", "maria_g", "maria@example.com", 24, "female"),
        ("Fatima", "Ahmed", "fatima_a", "fatima@example.com", 20, "female"),
        
        # Middle-aged mothers (26-35)
        ("Sarah", "Williams", "sarah_w", "sarah@example.com", 28, "female"),
        ("Jennifer", "Brown", "jennifer_b", "jennifer@example.com", 32, "female"),
        ("Lisa", "Davis", "lisa_d", "lisa@example.com", 30, "female"),
        
        # Older mothers (36-45)
        ("Patricia", "Miller", "patricia_m", "patricia@example.com", 38, "female"),
        ("Linda", "Wilson", "linda_w", "linda@example.com", 42, "female"),
        
        # Partners/Support persons
        ("Michael", "Johnson", "michael_j", "michael@example.com", 25, "male"),
        ("David", "Smith", "david_s", "david@example.com", 35, "male"),
        
        # Healthcare workers
        ("Dr. Emily", "Chen", "dr_emily", "emily@example.com", 40, "female"),
        ("Nurse", "Thompson", "nurse_thompson", "nurse@example.com", 45, "female"),
    ]
    
    for first_name, last_name, username, email, age, gender in users_data:
        cursor.execute("""
            INSERT INTO users (first_name, second_name, username, email, password_hash, avatar, age, gender, email_verified, created_at, last_login)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            first_name, last_name, username, email, "hashed_password_123",
            "images/avatars/diverse-1.png", age, gender, 1,
            datetime.now() - timedelta(days=random.randint(1, 90)),
            datetime.now() - timedelta(days=random.randint(0, 7))
        ))
    
    conn.commit()
    cursor.close()
    conn.close()
    print(f"✅ Created {len(users_data)} users")

def create_quiz_questions():
    """Create quiz questions"""
    conn = connect_to_db()
    cursor = conn.cursor()
    
    questions_data = [
        # Preconception questions
        ("preconception", "What is the recommended daily folic acid intake before pregnancy?", 
         json.dumps(["400mcg", "600mcg", "800mcg", "1000mcg"]), "400mcg"),
        ("preconception", "How long before trying to conceive should you stop smoking?", 
         json.dumps(["1 month", "3 months", "6 months", "1 year"]), "3 months"),
        ("preconception", "What BMI range is considered healthy for pregnancy?", 
         json.dumps(["18.5-24.9", "20-25", "22-27", "25-30"]), "18.5-24.9"),
        ("preconception", "Which vaccine is recommended before pregnancy?", 
         json.dumps(["MMR", "Flu", "Both MMR and Flu", "None needed"]), "Both MMR and Flu"),
        
        # Antenatal questions
        ("antenatal", "How often should prenatal visits occur in the first trimester?", 
         json.dumps(["Monthly", "Every 2 weeks", "Weekly", "As needed"]), "Monthly"),
        ("antenatal", "What is the recommended weight gain for normal BMI pregnancy?", 
         json.dumps(["15-20 lbs", "25-35 lbs", "35-45 lbs", "No limit"]), "25-35 lbs"),
        ("antenatal", "When should you start taking prenatal vitamins?", 
         json.dumps(["Before pregnancy", "After 12 weeks", "Only in third trimester", "Not necessary"]), "Before pregnancy"),
        ("antenatal", "What exercise is safe during pregnancy?", 
         json.dumps(["Running", "Swimming", "Weight lifting", "All of the above"]), "Swimming"),
        
        # Birth questions
        ("birth", "What are the signs of labor?", 
         json.dumps(["Contractions only", "Water breaking only", "Both contractions and water breaking", "None of the above"]), "Both contractions and water breaking"),
        ("birth", "When should you go to the hospital?", 
         json.dumps(["First contraction", "Contractions 5 minutes apart", "Water breaking", "Any of the above"]), "Any of the above"),
        ("birth", "What is the average length of labor for first-time mothers?", 
         json.dumps(["6-8 hours", "12-18 hours", "24-48 hours", "Variable"]), "12-18 hours"),
        ("birth", "What is delayed cord clamping?", 
         json.dumps(["Cutting cord immediately", "Waiting 1-3 minutes", "Never cutting cord", "Only in emergencies"]), "Waiting 1-3 minutes"),
        
        # Postnatal questions
        ("postnatal", "How often should newborns feed?", 
         json.dumps(["Every 4 hours", "Every 2-3 hours", "Once daily", "On demand"]), "On demand"),
        ("postnatal", "What is postpartum depression?", 
         json.dumps(["Normal baby blues", "Serious mood disorder", "Hormonal imbalance", "All of the above"]), "All of the above"),
        ("postnatal", "When can you resume exercise after birth?", 
         json.dumps(["Immediately", "After 6 weeks", "After 3 months", "Never"]), "After 6 weeks"),
        ("postnatal", "What is the recommended duration of exclusive breastfeeding?", 
         json.dumps(["3 months", "6 months", "12 months", "2 years"]), "6 months"),
    ]
    
    for scenario, question, options, answer in questions_data:
        cursor.execute("""
            INSERT INTO quiz_questions (scenario, question, options, answer, correct_reason, incorrect_reason, used)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            scenario, question, options, answer,
            f"Correct answer: {answer}", "Please review the material and try again.", 0
        ))
    
    conn.commit()
    cursor.close()
    conn.close()
    print(f"✅ Created {len(questions_data)} questions")

def create_user_responses():
    """Create realistic user response patterns"""
    conn = connect_to_db()
    cursor = conn.cursor()
    
    # Get all users and questions
    cursor.execute("SELECT user_ID, age, username FROM users WHERE email != 'admin@funzamama.org'")
    users = cursor.fetchall()
    
    cursor.execute("SELECT id, scenario FROM quiz_questions")
    questions = cursor.fetchall()
    
    stages = ["preconception", "antenatal", "birth", "postnatal"]
    
    for user_id, age, username in users:
        for stage in stages:
            stage_questions = [q for q in questions if q[1] == stage]
            if not stage_questions:
                continue
                
            # Number of attempts per stage (1-5)
            num_attempts = random.randint(1, 5)
            
            for attempt in range(num_attempts):
                # Select random questions for this attempt
                selected_questions = random.sample(stage_questions, min(5, len(stage_questions)))
                
                for question_id, _ in selected_questions:
                    # User performance varies by age and experience
                    if age < 25:
                        correct_probability = 0.6  # Younger users less experienced
                    elif age < 35:
                        correct_probability = 0.8  # Prime age group
                    else:
                        correct_probability = 0.7  # Older users, more experience but less tech-savvy
                    
                    # Healthcare workers perform better
                    if "dr_" in username or "nurse" in username:
                        correct_probability = 0.9
                    
                    is_correct = random.random() < correct_probability
                    
                    # Get question options
                    cursor.execute("SELECT options, answer FROM quiz_questions WHERE id = %s", (question_id,))
                    question_data = cursor.fetchone()
                    if question_data:
                        options = json.loads(question_data[0])
                        correct_answer = question_data[1]
                        selected_option = correct_answer if is_correct else random.choice(options)
                        
                        cursor.execute("""
                            INSERT INTO user_responses (user_id, question_id, selected_option, is_correct, attempt_number, stage)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (user_id, question_id, selected_option, is_correct, attempt + 1, stage))
    
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Created realistic response patterns")

def create_badges():
    """Create badge progress for users"""
    conn = connect_to_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT user_ID FROM users WHERE email != 'admin@funzamama.org'")
    users = cursor.fetchall()
    
    badge_stages = ["preconception", "antenatal", "birth", "postnatal"]
    
    for (user_id,) in users:
        for stage in badge_stages:
            # Calculate user's progress in this stage
            cursor.execute("""
                SELECT COUNT(*), SUM(is_correct) FROM user_responses 
                WHERE user_id = %s AND stage = %s
            """, (user_id, stage))
            result = cursor.fetchone()
            
            if result and result[0] > 0:
                total_count = result[0]
                correct_count = result[1] or 0
                progress = (correct_count / total_count) * 100
                
                # Get number of unique attempts
                cursor.execute("""
                    SELECT COUNT(DISTINCT attempt_number) FROM user_responses 
                    WHERE user_id = %s AND stage = %s
                """, (user_id, stage))
                num_attempts = cursor.fetchone()[0]
                
                # Create badge based on progress
                cursor.execute("""
                    INSERT INTO badge (user_ID, badge_name, score, number_of_attempts, progress, claimed)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    user_id, f"{stage.title()} Expert", int(progress), 
                    num_attempts, progress, progress >= 80
                ))
    
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Created badge progress")

def create_feedback():
    """Create diverse feedback entries"""
    conn = connect_to_db()
    cursor = conn.cursor()
    
    feedback_data = [
        ("Sarah Williams", "sarah@example.com", "bug", "The quiz questions sometimes don't load properly on mobile devices.", "pending", None),
        ("Maria Garcia", "maria@example.com", "feature", "It would be great to have a progress tracker showing which topics I've mastered.", "reviewed", None),
        ("Dr. Emily Chen", "emily@example.com", "content", "The prenatal nutrition section could include more information about vegetarian diets during pregnancy.", "resolved", None),
        ("Michael Johnson", "michael@example.com", "feature", "Could you add a partner mode so fathers can also learn about pregnancy and childbirth?", "pending", None),
        ("Fatima Ahmed", "fatima@example.com", "other", "The app has been incredibly helpful! Thank you for creating such a valuable resource.", "replied", "Thank you for your kind words! We're so glad the app is helping you on your journey."),
        ("Jennifer Brown", "jennifer@example.com", "bug", "The sound effects sometimes overlap and create audio issues.", "pending", None),
        ("Lisa Davis", "lisa@example.com", "feature", "Would love to see a community forum where mothers can share experiences and tips.", "reviewed", None),
        ("Patricia Miller", "patricia@example.com", "content", "The postnatal care section needs more information about mental health support resources.", "pending", None),
    ]
    
    for user_name, email, category, message, status, admin_reply in feedback_data:
        cursor.execute("""
            INSERT INTO feedback (user_name, email, category, message, status, admin_reply, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            user_name, email, category, message, status, admin_reply,
            datetime.now() - timedelta(days=random.randint(1, 30))
        ))
    
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Created feedback entries")

def main():
    """Main function to create all seed data"""
    print("🌱 Creating comprehensive seed data for Funza Mama...")
    
    # Clear existing data
    print("🧹 Clearing existing test data...")
    conn = connect_to_db()
    cursor = conn.cursor()
    
    # Delete in correct order to respect foreign key constraints
    cursor.execute("DELETE FROM user_responses")
    cursor.execute("DELETE FROM badge")
    cursor.execute("DELETE FROM feedback")
    cursor.execute("DELETE FROM quiz_questions")
    cursor.execute("DELETE FROM user_question_history")
    cursor.execute("DELETE FROM users WHERE email != 'admin@funzamama.org'")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("👥 Creating users...")
    create_users()
    
    print("📝 Creating quiz questions...")
    create_quiz_questions()
    
    print("📊 Creating user responses...")
    create_user_responses()
    
    print("🏆 Creating badges...")
    create_badges()
    
    print("💬 Creating feedback...")
    create_feedback()
    
    print("\n🎉 Seed data creation complete!")
    print("\n📈 You can now test:")
    print("  • User management with diverse demographics")
    print("  • Analytics with realistic performance data")
    print("  • Feedback management with various categories")
    print("  • Badge progress tracking")
    print("  • Stage completion rates")
    print("  • PDF report generation")

if __name__ == "__main__":
    main()
