"""
Test script to verify question filtering across rounds
Tests all 4 stages to ensure Round 2 gets different questions than Round 1

Run this from your Flask app directory with: 
    python test_question_filtering.py
    
Or from within Flask shell:
    flask shell
    exec(open('test_question_filtering.py').read())
"""

import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Try to use existing Flask app context
try:
    from app import app
    from models import db
    from models.models import User, UserResponse, QuizQuestion
    from chatbot.optimized_modelintegration import get_hybrid_questions, get_questions_seen_in_database
    from chatbot.adaptive_learning import generate_question_hash
except ImportError as e:
    print(f"Import error: {e}")
    print(f"\n⚠️  Current working directory: {os.getcwd()}")
    print(f"⚠️  Project root: {project_root}")
    print(f"⚠️  Python path: {sys.path[:3]}")
    print("\n⚠️  Please run this script from your Flask app directory")
    print("   And activate your virtual environment first:")
    print("   myenv\\Scripts\\activate  (Windows)")
    print("   source myenv/bin/activate  (Linux/Mac)")
    print("\n   Then run: python test_question_filtering.py")
    sys.exit(1)

# Test user ID (you can change this to an actual user ID)
TEST_USER_ID = 1  # Change this to a real user ID in your database
TEST_STAGES = ["preconception", "prenatal", "birth", "postnatal"]

def setup_test_data():
    """Setup test data - clear previous test responses"""
    with app.app_context():
        print("🔧 Setting up test data...")
        # Clear test responses
        UserResponse.query.filter_by(user_id=TEST_USER_ID).delete()
        db.session.commit()
        print("✅ Cleared previous test responses\n")

def simulate_round(stage, round_num):
    """Simulate playing a round and saving responses"""
    with app.app_context():
        print(f"📝 Round {round_num} - Stage: {stage}")
        
        # Get questions for this round
        questions = get_hybrid_questions(stage, TEST_USER_ID, difficulty_level=1)
        
        if not questions or len(questions) == 0:
            print(f"❌ No questions returned for {stage}!")
            return []
        
        print(f"   Got {len(questions)} questions")
        print(f"   Questions:")
        for i, q in enumerate(questions[:5], 1):  # Show first 5
            print(f"     {i}. {q.get('question', '')[:60]}...")
        if len(questions) > 5:
            print(f"     ... and {len(questions) - 5} more")
        
        # Simulate answering all questions (save to database)
        attempt_number = round_num
        question_texts = []
        
        for idx, q in enumerate(questions):
            question_text = q.get('question', '')
            question_texts.append(question_text)
            
            # Normalize stage name - MUST match normalization in get_questions_seen_in_database
            # This ensures database queries can find questions saved with normalized stage names
            # See chatbot/optimized_modelintegration.py line 106-112 for reference
            normalized_stage = stage
            if stage == "birth":
                normalized_stage = "birth_and_delivery"
            # Note: "preconception", "prenatal", "postnatal" don't need normalization
            # They stay as-is: "preconception", "prenatal", "postnatal"
            
            # Find or create quiz question
            existing_question = QuizQuestion.query.filter_by(
                question=question_text, 
                user_id=TEST_USER_ID, 
                scenario=normalized_stage
            ).first()
            
            if existing_question:
                question_id = existing_question.id
            else:
                # Create quiz question
                quiz_question = QuizQuestion(
                    scenario=normalized_stage,
                    question=question_text,
                    options=str(q.get('options', [])),
                    answer=q.get('answer', ''),
                    correct_reason=q.get('correctReason', ''),
                    incorrect_reason=q.get('incorrectReason', ''),
                    user_id=TEST_USER_ID
                )
                db.session.add(quiz_question)
                db.session.commit()
                question_id = quiz_question.id
            
            # Create user response
            user_response = UserResponse(
                user_id=TEST_USER_ID,
                question_id=question_id,
                selected_option=q.get('answer', ''),
                is_correct=True,  # Simulate correct answer
                stage=normalized_stage,
                attempt_number=attempt_number
            )
            db.session.add(user_response)
        
        db.session.commit()
        print(f"✅ Saved {len(questions)} responses to database\n")
        
        return question_texts

def check_question_overlap(round1_questions, round2_questions):
    """Check how many questions overlap between rounds"""
    round1_set = {q.strip().lower() for q in round1_questions}
    round2_set = {q.strip().lower() for q in round2_questions}
    
    overlap = round1_set.intersection(round2_set)
    overlap_count = len(overlap)
    total_round1 = len(round1_set)
    total_round2 = len(round2_set)
    
    return {
        'overlap_count': overlap_count,
        'total_round1': total_round1,
        'total_round2': total_round2,
        'overlap_percentage': (overlap_count / max(total_round1, 1)) * 100
    }

def test_stage(stage):
    """Test a single stage with 2 rounds"""
    print(f"\n{'='*70}")
    print(f"🧪 Testing Stage: {stage.upper()}")
    print(f"{'='*70}\n")
    
    # Round 1
    round1_questions = simulate_round(stage, 1)
    
    if not round1_questions:
        print(f"❌ Stage {stage} failed - no questions in Round 1\n")
        return False
    
    # Check database tracking
    with app.app_context():
        seen_in_db = get_questions_seen_in_database(TEST_USER_ID, stage)
        print(f"📊 After Round 1: {len(seen_in_db)} questions tracked in database")
    
    # Round 2
    round2_questions = simulate_round(stage, 2)
    
    if not round2_questions:
        print(f"❌ Stage {stage} failed - no questions in Round 2\n")
        return False
    
    # Check overlap
    overlap_data = check_question_overlap(round1_questions, round2_questions)
    
    print(f"📊 Overlap Analysis:")
    print(f"   Round 1 questions: {overlap_data['total_round1']}")
    print(f"   Round 2 questions: {overlap_data['total_round2']}")
    print(f"   Overlapping questions: {overlap_data['overlap_count']}")
    print(f"   Overlap percentage: {overlap_data['overlap_percentage']:.1f}%")
    
    # Check final database state
    with app.app_context():
        seen_in_db_final = get_questions_seen_in_database(TEST_USER_ID, stage)
        print(f"   Total unique questions in DB: {len(seen_in_db_final)}")
    
    # Result
    if overlap_data['overlap_count'] == 0:
        print(f"✅ SUCCESS: Round 2 has completely new questions!")
    elif overlap_data['overlap_percentage'] < 30:
        print(f"⚠️  PARTIAL: Round 2 has mostly new questions ({overlap_data['overlap_percentage']:.1f}% overlap)")
    else:
        print(f"❌ FAIL: Round 2 has too many repeated questions ({overlap_data['overlap_percentage']:.1f}% overlap)")
    
    print()
    return overlap_data['overlap_count'] < 3  # Pass if less than 3 overlaps

def main():
    """Run tests for all stages"""
    print("🚀 Starting Question Filtering Test")
    print("="*70)
    print(f"Test User ID: {TEST_USER_ID}")
    print(f"Testing stages: {', '.join(TEST_STAGES)}")
    print("="*70)
    
    with app.app_context():
        # Verify user exists
        user = User.query.get(TEST_USER_ID)
        if not user:
            print(f"\n❌ ERROR: User ID {TEST_USER_ID} not found in database!")
            print("   Please update TEST_USER_ID to an existing user ID")
            return
        
        print(f"✅ Found user: {user.first_name} {user.second_name}")
    
    # Setup
    setup_test_data()
    
    # Test each stage
    results = {}
    for stage in TEST_STAGES:
        results[stage] = test_stage(stage)
    
    # Summary
    print("\n" + "="*70)
    print("📋 TEST SUMMARY")
    print("="*70)
    for stage, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {stage.upper()}")
    
    total_passed = sum(1 for p in results.values() if p)
    total_stages = len(results)
    print(f"\nTotal: {total_passed}/{total_stages} stages passed")
    
    if total_passed == total_stages:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()
