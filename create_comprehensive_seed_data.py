#!/usr/bin/env python3
"""
Comprehensive Seed Data Generator for Funza Mama Admin Testing
Creates realistic test data for all admin features
"""

from app import app
from models import db
from models.models import User, UserResponse, Badge, Feedback, QuizQuestion
from datetime import datetime, timedelta
import random
import hashlib

def create_users():
    """Create diverse test users with demographics"""
    users_data = [
        # Young mothers (18-25)
        {"first_name": "Aisha", "second_name": "Johnson", "username": "aisha_j", "email": "aisha@example.com", "age": 22, "gender": "female"},
        {"first_name": "Maria", "second_name": "Garcia", "username": "maria_g", "email": "maria@example.com", "age": 24, "gender": "female"},
        {"first_name": "Fatima", "second_name": "Ahmed", "username": "fatima_a", "email": "fatima@example.com", "age": 20, "gender": "female"},
        
        # Middle-aged mothers (26-35)
        {"first_name": "Sarah", "second_name": "Williams", "username": "sarah_w", "email": "sarah@example.com", "age": 28, "gender": "female"},
        {"first_name": "Jennifer", "second_name": "Brown", "username": "jennifer_b", "email": "jennifer@example.com", "age": 32, "gender": "female"},
        {"first_name": "Lisa", "second_name": "Davis", "username": "lisa_d", "email": "lisa@example.com", "age": 30, "gender": "female"},
        
        # Older mothers (36-45)
        {"first_name": "Patricia", "second_name": "Miller", "username": "patricia_m", "email": "patricia@example.com", "age": 38, "gender": "female"},
        {"first_name": "Linda", "second_name": "Wilson", "username": "linda_w", "email": "linda@example.com", "age": 42, "gender": "female"},
        
        # Partners/Support persons
        {"first_name": "Michael", "second_name": "Johnson", "username": "michael_j", "email": "michael@example.com", "age": 25, "gender": "male"},
        {"first_name": "David", "second_name": "Smith", "username": "david_s", "email": "david@example.com", "age": 35, "gender": "male"},
        
        # Healthcare workers
        {"first_name": "Dr. Emily", "second_name": "Chen", "username": "dr_emily", "email": "emily@example.com", "age": 40, "gender": "female"},
        {"first_name": "Nurse", "second_name": "Thompson", "username": "nurse_thompson", "email": "nurse@example.com", "age": 45, "gender": "female"},
    ]
    
    users = []
    for user_data in users_data:
        user = User(
            first_name=user_data["first_name"],
            second_name=user_data["second_name"],
            username=user_data["username"],
            email=user_data["email"],
            password_hash="hashed_password_123",  # In real app, this would be properly hashed
            avatar="images/avatars/diverse-1.png",
            age=user_data["age"],
            gender=user_data["gender"],
            email_verified=True,
            created_at=datetime.now() - timedelta(days=random.randint(1, 90)),
            last_login=datetime.now() - timedelta(days=random.randint(0, 7))
        )
        users.append(user)
        db.session.add(user)
    
    db.session.commit()
    return users

def create_quiz_questions():
    """Create diverse quiz questions for all stages"""
    questions_data = [
        # Preconception questions
        {"stage": "preconception", "text": "What is the recommended daily folic acid intake before pregnancy?", "options": ["400mcg", "600mcg", "800mcg", "1000mcg"], "correct": 0},
        {"stage": "preconception", "text": "How long before trying to conceive should you stop smoking?", "options": ["1 month", "3 months", "6 months", "1 year"], "correct": 1},
        {"stage": "preconception", "text": "What BMI range is considered healthy for pregnancy?", "options": ["18.5-24.9", "20-25", "22-27", "25-30"], "correct": 0},
        {"stage": "preconception", "text": "Which vaccine is recommended before pregnancy?", "options": ["MMR", "Flu", "Both MMR and Flu", "None needed"], "correct": 2},
        
        # Antenatal questions
        {"stage": "antenatal", "text": "How often should prenatal visits occur in the first trimester?", "options": ["Monthly", "Every 2 weeks", "Weekly", "As needed"], "correct": 0},
        {"stage": "antenatal", "text": "What is the recommended weight gain for normal BMI pregnancy?", "options": ["15-20 lbs", "25-35 lbs", "35-45 lbs", "No limit"], "correct": 1},
        {"stage": "antenatal", "text": "When should you start taking prenatal vitamins?", "options": ["Before pregnancy", "After 12 weeks", "Only in third trimester", "Not necessary"], "correct": 0},
        {"stage": "antenatal", "text": "What exercise is safe during pregnancy?", "options": ["Running", "Swimming", "Weight lifting", "All of the above"], "correct": 1},
        
        # Birth questions
        {"stage": "birth", "text": "What are the signs of labor?", "options": ["Contractions only", "Water breaking only", "Both contractions and water breaking", "None of the above"], "correct": 2},
        {"stage": "birth", "text": "When should you go to the hospital?", "options": ["First contraction", "Contractions 5 minutes apart", "Water breaking", "Any of the above"], "correct": 3},
        {"stage": "birth", "text": "What is the average length of labor for first-time mothers?", "options": ["6-8 hours", "12-18 hours", "24-48 hours", "Variable"], "correct": 1},
        {"stage": "birth", "text": "What is delayed cord clamping?", "options": ["Cutting cord immediately", "Waiting 1-3 minutes", "Never cutting cord", "Only in emergencies"], "correct": 1},
        
        # Postnatal questions
        {"stage": "postnatal", "text": "How often should newborns feed?", "options": ["Every 4 hours", "Every 2-3 hours", "Once daily", "On demand"], "correct": 3},
        {"stage": "postnatal", "text": "What is postpartum depression?", "options": ["Normal baby blues", "Serious mood disorder", "Hormonal imbalance", "All of the above"], "correct": 3},
        {"stage": "postnatal", "text": "When can you resume exercise after birth?", "options": ["Immediately", "After 6 weeks", "After 3 months", "Never"], "correct": 1},
        {"stage": "postnatal", "text": "What is the recommended duration of exclusive breastfeeding?", "options": ["3 months", "6 months", "12 months", "2 years"], "correct": 1},
    ]
    
    questions = []
    for q_data in questions_data:
        question = QuizQuestion(
            scenario=q_data["stage"],
            question=q_data["text"],
            options=str(q_data["options"]),  # Convert to JSON string
            answer=q_data["options"][q_data["correct"]],  # Store the correct answer text
            correct_reason=f"Correct answer: {q_data['options'][q_data['correct']]}",
            incorrect_reason="Please review the material and try again.",
            used=False
        )
        questions.append(question)
        db.session.add(question)
    
    db.session.commit()
    return questions

def create_user_responses(users, questions):
    """Create realistic user response patterns"""
    stages = ["preconception", "antenatal", "birth", "postnatal"]
    
    for user in users:
        # Each user attempts different stages with varying success rates
        for stage in stages:
            stage_questions = [q for q in questions if q.stage == stage]
            if not stage_questions:
                continue
                
            # Number of attempts per stage (1-5)
            num_attempts = random.randint(1, 5)
            
            for attempt in range(num_attempts):
                # Select random questions for this attempt
                selected_questions = random.sample(stage_questions, min(5, len(stage_questions)))
                
                for question in selected_questions:
                    # Parse options from JSON string
                    import json
                    try:
                        options = json.loads(question.options)
                    except:
                        options = ["Option A", "Option B", "Option C", "Option D"]
                    
                    # User performance varies by age and experience
                    if user.age < 25:
                        correct_probability = 0.6  # Younger users less experienced
                    elif user.age < 35:
                        correct_probability = 0.8  # Prime age group
                    else:
                        correct_probability = 0.7  # Older users, more experience but less tech-savvy
                    
                    # Healthcare workers perform better
                    if "dr_" in user.username or "nurse" in user.username:
                        correct_probability = 0.9
                    
                    is_correct = random.random() < correct_probability
                    selected_option = question.answer if is_correct else random.choice(options)
                    
                    response = UserResponse(
                        user_id=user.user_ID,
                        question_id=question.id,
                        selected_option=selected_option,
                        is_correct=is_correct,
                        attempt_number=attempt + 1,
                        stage=stage
                    )
                    db.session.add(response)
    
    db.session.commit()

def create_badges(users):
    """Create badge progress for users"""
    badge_stages = ["preconception", "antenatal", "birth", "postnatal"]
    
    for user in users:
        for stage in badge_stages:
            # Calculate user's progress in this stage
            stage_responses = UserResponse.query.filter_by(user_id=user.user_ID, stage=stage).all()
            if stage_responses:
                correct_count = sum(1 for r in stage_responses if r.is_correct)
                total_count = len(stage_responses)
                progress = (correct_count / total_count) * 100
                
                # Create badge based on progress
                badge = Badge(
                    user_ID=user.user_ID,
                    badge_name=f"{stage.title()} Expert",
                    score=int(progress),
                    number_of_attempts=len(set(r.attempt_number for r in stage_responses)),
                    progress=progress,
                    claimed=progress >= 80
                )
                db.session.add(badge)
    
    db.session.commit()

def create_feedback():
    """Create diverse feedback entries"""
    feedback_data = [
        {"user_name": "Sarah Williams", "email": "sarah@example.com", "category": "bug", "message": "The quiz questions sometimes don't load properly on mobile devices.", "status": "pending"},
        {"user_name": "Maria Garcia", "email": "maria@example.com", "category": "feature", "message": "It would be great to have a progress tracker showing which topics I've mastered.", "status": "reviewed"},
        {"user_name": "Dr. Emily Chen", "email": "emily@example.com", "category": "content", "message": "The prenatal nutrition section could include more information about vegetarian diets during pregnancy.", "status": "resolved"},
        {"user_name": "Michael Johnson", "email": "michael@example.com", "category": "feature", "message": "Could you add a partner mode so fathers can also learn about pregnancy and childbirth?", "status": "pending"},
        {"user_name": "Fatima Ahmed", "email": "fatima@example.com", "category": "other", "message": "The app has been incredibly helpful! Thank you for creating such a valuable resource.", "status": "replied", "admin_reply": "Thank you for your kind words! We're so glad the app is helping you on your journey."},
        {"user_name": "Jennifer Brown", "email": "jennifer@example.com", "category": "bug", "message": "The sound effects sometimes overlap and create audio issues.", "status": "pending"},
        {"user_name": "Lisa Davis", "email": "lisa@example.com", "category": "feature", "message": "Would love to see a community forum where mothers can share experiences and tips.", "status": "reviewed"},
        {"user_name": "Patricia Miller", "email": "patricia@example.com", "category": "content", "message": "The postnatal care section needs more information about mental health support resources.", "status": "pending"},
    ]
    
    for fb_data in feedback_data:
        feedback = Feedback(
            user_name=fb_data["user_name"],
            email=fb_data["email"],
            category=fb_data["category"],
            message=fb_data["message"],
            status=fb_data["status"],
            admin_reply=fb_data.get("admin_reply"),
            created_at=datetime.now() - timedelta(days=random.randint(1, 30))
        )
        db.session.add(feedback)
    
    db.session.commit()

def main():
    """Main function to create all seed data"""
    with app.app_context():
        print("🌱 Creating comprehensive seed data for Funza Mama...")
        
        # Clear existing data (optional - comment out if you want to keep existing data)
        print("🧹 Clearing existing test data...")
        # Delete in correct order to respect foreign key constraints
        UserResponse.query.delete()
        Badge.query.delete()
        Feedback.query.delete()
        QuizQuestion.query.delete()
        # Delete user_question_history first
        from models.models import UserQuestionHistory
        UserQuestionHistory.query.delete()
        # Then delete users
        User.query.filter(User.email != 'admin@funzamama.org').delete()
        
        print("👥 Creating users...")
        users = create_users()
        print(f"✅ Created {len(users)} users")
        
        print("📝 Creating quiz questions...")
        questions = create_quiz_questions()
        print(f"✅ Created {len(questions)} questions")
        
        print("📊 Creating user responses...")
        create_user_responses(users, questions)
        print("✅ Created realistic response patterns")
        
        print("🏆 Creating badges...")
        create_badges(users)
        print("✅ Created badge progress")
        
        print("💬 Creating feedback...")
        create_feedback()
        print("✅ Created feedback entries")
        
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
