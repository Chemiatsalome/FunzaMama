#!/usr/bin/env python3
"""
MySQL Table Creation Script for Funza Mama
This script will create all necessary tables in your existing MySQL database.
"""

import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models.models import User, QuizQuestion, UserResponse, Badge, GameStage, UserScenarioProgress
from werkzeug.security import generate_password_hash
import json

def create_tables():
    """Create all database tables"""
    print("🗄️  Creating MySQL database tables...")
    
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("   ✅ All tables created successfully!")
            
            # Commit the changes
            db.session.commit()
            print("   ✅ Database structure created successfully!")
            
        except Exception as e:
            print(f"   ❌ Error creating tables: {str(e)}")
            return False
    
    return True

def populate_sample_data():
    """Populate database with sample data"""
    print("\n📊 Populating database with sample data...")
    
    with app.app_context():
        try:
            # Create sample users
            users_data = [
                {
                    'first_name': 'Sarah',
                    'second_name': 'Johnson',
                    'username': 'sarah_j',
                    'email': 'sarah@example.com',
                    'password': 'password123',
                    'avatar': 'images/woman1/avatar-happy.png'
                },
                {
                    'first_name': 'Michael',
                    'second_name': 'Brown',
                    'username': 'michael_b',
                    'email': 'michael@example.com',
                    'password': 'password123',
                    'avatar': 'images/man1/avatar-happy.png'
                },
                {
                    'first_name': 'Test',
                    'second_name': 'User',
                    'username': 'testuser',
                    'email': 'test@example.com',
                    'password': 'test123',
                    'avatar': 'images/man2/avatar-happy.png'
                }
            ]
            
            for user_data in users_data:
                # Check if user already exists
                existing_user = User.query.filter_by(email=user_data['email']).first()
                if not existing_user:
                    user = User(
                        first_name=user_data['first_name'],
                        second_name=user_data['second_name'],
                        username=user_data['username'],
                        email=user_data['email'],
                        avatar=user_data['avatar']
                    )
                    user.set_password(user_data['password'])
                    db.session.add(user)
            
            db.session.commit()
            print("   ✅ Sample users created")
            
            # Create sample quiz questions
            questions_data = [
                # Preconception Questions
                {
                    'scenario': 'preconception',
                    'question': 'What is the recommended daily folic acid intake for women planning to conceive?',
                    'options': json.dumps(['400 mcg', '800 mcg', '1200 mcg', '1600 mcg']),
                    'answer': '400 mcg',
                    'correct_reason': 'The CDC recommends 400 mcg of folic acid daily for women of childbearing age to prevent neural tube defects.',
                    'incorrect_reason': 'Higher doses may be needed for women with certain medical conditions, but 400 mcg is the standard recommendation.'
                },
                {
                    'scenario': 'preconception',
                    'question': 'How long before conception should women start taking folic acid?',
                    'options': json.dumps(['1 month', '3 months', '6 months', '1 year']),
                    'answer': '1 month',
                    'correct_reason': 'Women should start taking folic acid at least 1 month before conception for optimal protection.',
                    'incorrect_reason': 'While longer periods are beneficial, at least 1 month is the minimum recommended timeframe.'
                },
                {
                    'scenario': 'preconception',
                    'question': 'Which lifestyle factor is most important to address before pregnancy?',
                    'options': json.dumps(['Exercise routine', 'Smoking cessation', 'Diet changes', 'Sleep schedule']),
                    'answer': 'Smoking cessation',
                    'correct_reason': 'Smoking cessation is crucial as it affects fertility and can cause serious pregnancy complications.',
                    'incorrect_reason': 'While other factors are important, smoking has the most significant impact on pregnancy outcomes.'
                },
                
                # Prenatal Questions
                {
                    'scenario': 'prenatal',
                    'question': 'When should a pregnant woman have her first prenatal visit?',
                    'options': json.dumps(['As soon as she suspects pregnancy', 'After 8 weeks', 'After 12 weeks', 'After 16 weeks']),
                    'answer': 'As soon as she suspects pregnancy',
                    'correct_reason': 'Early prenatal care is essential for monitoring the health of both mother and baby.',
                    'incorrect_reason': 'Delaying prenatal care can miss important early developmental milestones and potential issues.'
                },
                {
                    'scenario': 'prenatal',
                    'question': 'What is the recommended weight gain during pregnancy for a woman with normal BMI?',
                    'options': json.dumps(['15-20 lbs', '25-35 lbs', '35-45 lbs', '45-55 lbs']),
                    'answer': '25-35 lbs',
                    'correct_reason': 'The recommended weight gain for women with normal BMI (18.5-24.9) is 25-35 pounds.',
                    'incorrect_reason': 'This range is specifically for normal BMI women; recommendations vary based on pre-pregnancy weight.'
                },
                {
                    'scenario': 'prenatal',
                    'question': 'Which trimester is most critical for fetal organ development?',
                    'options': json.dumps(['First trimester', 'Second trimester', 'Third trimester', 'All equally important']),
                    'answer': 'First trimester',
                    'correct_reason': 'The first trimester is when major organs and systems form, making it the most critical period.',
                    'incorrect_reason': 'While all trimesters are important, the first trimester is when the foundation is laid.'
                },
                
                # Birth Questions
                {
                    'scenario': 'birth',
                    'question': 'What is the first stage of labor?',
                    'options': json.dumps(['Pushing', 'Cervical dilation', 'Placenta delivery', 'Recovery']),
                    'answer': 'Cervical dilation',
                    'correct_reason': 'The first stage involves cervical dilation from 0 to 10 centimeters.',
                    'incorrect_reason': 'This stage focuses on cervical preparation, not active pushing or delivery.'
                },
                {
                    'scenario': 'birth',
                    'question': 'When should you go to the hospital during labor?',
                    'options': json.dumps(['At first contraction', 'When contractions are 5 minutes apart', 'When water breaks', 'When contractions are 2 minutes apart']),
                    'answer': 'When contractions are 5 minutes apart',
                    'correct_reason': 'The 5-1-1 rule: contractions 5 minutes apart, lasting 1 minute, for 1 hour.',
                    'incorrect_reason': 'Going too early or too late can affect the birth experience and safety.'
                },
                {
                    'scenario': 'birth',
                    'question': 'What is the normal duration of the second stage of labor for first-time mothers?',
                    'options': json.dumps(['30 minutes', '1-2 hours', '2-3 hours', '3-4 hours']),
                    'answer': '1-2 hours',
                    'correct_reason': 'The second stage (pushing) typically lasts 1-2 hours for first-time mothers.',
                    'incorrect_reason': 'This stage can vary, but 1-2 hours is the average for first-time mothers.'
                },
                
                # Postnatal Questions
                {
                    'scenario': 'postnatal',
                    'question': 'How often should a newborn be fed in the first few weeks?',
                    'options': json.dumps(['Every 2 hours', 'Every 3-4 hours', 'On demand', 'Every 6 hours']),
                    'answer': 'On demand',
                    'correct_reason': 'Newborns should be fed on demand, typically every 2-3 hours, to ensure proper nutrition.',
                    'incorrect_reason': 'Rigid schedules can interfere with the baby\'s natural feeding patterns and growth.'
                },
                {
                    'scenario': 'postnatal',
                    'question': 'What is the recommended sleeping position for newborns?',
                    'options': json.dumps(['On their stomach', 'On their side', 'On their back', 'Any position is fine']),
                    'answer': 'On their back',
                    'correct_reason': 'Back sleeping reduces the risk of SIDS and is the safest position for newborns.',
                    'incorrect_reason': 'This position has been proven to significantly reduce the risk of sudden infant death syndrome.'
                },
                {
                    'scenario': 'postnatal',
                    'question': 'When should a newborn have their first pediatric visit?',
                    'options': json.dumps(['Within 24 hours', 'Within 3-5 days', 'Within 1 week', 'Within 2 weeks']),
                    'answer': 'Within 3-5 days',
                    'correct_reason': 'The first well-baby visit should occur within 3-5 days of birth to monitor early development.',
                    'incorrect_reason': 'This timing allows for early detection of any issues while not being too overwhelming for new parents.'
                }
            ]
            
            for question_data in questions_data:
                # Check if question already exists
                existing_question = QuizQuestion.query.filter_by(
                    question=question_data['question']
                ).first()
                if not existing_question:
                    question = QuizQuestion(
                        scenario=question_data['scenario'],
                        question=question_data['question'],
                        options=question_data['options'],
                        answer=question_data['answer'],
                        correct_reason=question_data['correct_reason'],
                        incorrect_reason=question_data['incorrect_reason']
                    )
                    db.session.add(question)
            
            db.session.commit()
            print("   ✅ Sample questions created")
            
            # Create sample progress data for the first user
            user = User.query.first()
            if user:
                # Create game stage progress
                stages = ['Preconception', 'Antenatal', 'Birth', 'Postnatal']
                for stage in stages:
                    existing_stage = GameStage.query.filter_by(
                        user_ID=user.user_ID, 
                        stage_name=stage
                    ).first()
                    if not existing_stage:
                        game_stage = GameStage(
                            user_ID=user.user_ID,
                            stage_name=stage,
                            number_of_attempts=0,
                            overall_score=0
                        )
                        db.session.add(game_stage)
                
                # Create scenario progress
                scenarios = ['preconception', 'prenatal', 'birth', 'postnatal']
                for scenario in scenarios:
                    existing_progress = UserScenarioProgress.query.filter_by(
                        user_id=user.user_ID,
                        scenario=scenario
                    ).first()
                    if not existing_progress:
                        progress = UserScenarioProgress(
                            user_id=user.user_ID,
                            scenario=scenario,
                            attempt_count=0,
                            completed=False
                        )
                        db.session.add(progress)
                
                db.session.commit()
                print("   ✅ Sample progress data created")
            
            print("   ✅ Database populated successfully!")
            
        except Exception as e:
            print(f"   ❌ Error populating database: {str(e)}")
            return False
    
    return True

def main():
    """Main function to create tables and populate data"""
    print("🚀 Starting Funza Mama MySQL Table Creation...")
    print("=" * 60)
    
    try:
        # Create tables
        if not create_tables():
            print("❌ Failed to create tables. Please check your MySQL connection.")
            return False
        
        # Populate with sample data
        if not populate_sample_data():
            print("❌ Failed to populate sample data.")
            return False
        
        print("\n" + "=" * 60)
        print("✅ MySQL table creation completed successfully!")
        print("\n📋 Summary:")
        print("   • 6 database tables created:")
        print("     - users")
        print("     - quiz_questions") 
        print("     - user_responses")
        print("     - badges")
        print("     - game_stages")
        print("     - user_scenario_progress")
        print("   • 3 sample users created")
        print("   • 12 sample questions created")
        print("   • Sample progress data created")
        print("\n🔑 Sample Login Credentials:")
        print("   • Username: sarah_j, Password: password123")
        print("   • Username: michael_b, Password: password123")
        print("   • Username: testuser, Password: test123")
        print("\n🎯 You can now run your Flask application!")
        print("   Make sure XAMPP MySQL is running before starting the app.")
        
    except Exception as e:
        print(f"\n❌ Error during table creation: {str(e)}")
        print("Please check your MySQL connection and try again.")
        return False
    
    return True

if __name__ == "__main__":
    main()
