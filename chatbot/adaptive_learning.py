"""
Adaptive Learning System for Funza Mama
Implements Duolingo-style personalized question generation
"""

import hashlib
import json
import random
from datetime import datetime, timedelta
from models import db
from models.models import UserQuestionHistory, UserResponse
# Lazy imports to avoid circular dependency with optimized_modelintegration
# Functions imported only when needed in generate_ai_questions()

def generate_question_hash(question_text):
    """Generate a unique hash for a question to track it across sessions"""
    return hashlib.md5(question_text.encode()).hexdigest()

def get_user_question_history(user_id, stage):
    """Get user's question history for a specific stage"""
    return UserQuestionHistory.query.filter_by(
        user_id=user_id, 
        stage=stage
    ).order_by(UserQuestionHistory.last_attempted.desc()).all()

def get_failed_questions(user_id, stage, min_attempts=3):
    """Get questions that user has failed multiple times and need review"""
    return UserQuestionHistory.query.filter_by(
        user_id=user_id,
        stage=stage,
        needs_review=True
    ).filter(
        UserQuestionHistory.attempt_count >= min_attempts,
        UserQuestionHistory.is_correct == False
    ).all()

def get_recent_questions(user_id, stage, days=7):
    """Get questions answered in the last N days"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    return UserQuestionHistory.query.filter_by(
        user_id=user_id,
        stage=stage
    ).filter(
        UserQuestionHistory.last_attempted >= cutoff_date
    ).all()

def calculate_user_difficulty_level(user_id, stage):
    """Calculate user's current difficulty level based on performance"""
    recent_questions = get_recent_questions(user_id, stage, days=14)
    
    if not recent_questions:
        return 1  # Beginner level
    
    correct_count = sum(1 for q in recent_questions if q.is_correct)
    total_count = len(recent_questions)
    accuracy = correct_count / total_count if total_count > 0 else 0
    
    # Adjust difficulty based on accuracy
    if accuracy >= 0.8:
        return min(3, max(1, recent_questions[0].difficulty_level + 1))
    elif accuracy <= 0.4:
        return max(1, recent_questions[0].difficulty_level - 1)
    else:
        return recent_questions[0].difficulty_level

def generate_adaptive_questions(user_id, stage, num_questions=10):
    """
    Generate adaptive questions based on user's learning history
    Implements Duolingo-style learning with enhanced personalization:
    - 40% new questions (personalized to user's learning style)
    - 30% failed questions (for review)
    - 20% mixed difficulty questions
    - 10% cultural/contextual questions
    """
    
    # Get user's question history
    question_history = get_user_question_history(user_id, stage)
    failed_questions = get_failed_questions(user_id, stage)
    recent_questions = get_recent_questions(user_id, stage)
    
    # Calculate user's difficulty level
    difficulty_level = calculate_user_difficulty_level(user_id, stage)
    
    # Get existing question hashes to avoid repetition
    existing_hashes = {q.question_hash for q in question_history}
    
    # Generate new questions from AI
    ai_questions = generate_ai_questions(stage, difficulty_level)
    
    # Filter out questions user has already seen
    new_questions = []
    for q in ai_questions:
        q_hash = generate_question_hash(q['question'])
        if q_hash not in existing_hashes:
            new_questions.append(q)
    
    # Build adaptive question set
    adaptive_questions = []
    
    # 40% new questions (personalized)
    num_new = int(num_questions * 0.4)
    if new_questions:
        adaptive_questions.extend(new_questions[:num_new])
    elif user_id != "guest_user":
        # Generate personalized questions if no new ones available
        personalized_questions = generate_ai_questions(stage, difficulty_level, num_new, user_id)
        adaptive_questions.extend(personalized_questions)
    
    # 30% failed questions (for review)
    num_failed = int(num_questions * 0.3)
    if failed_questions:
        # Convert failed questions back to question format
        failed_q_list = []
        for fq in failed_questions[:num_failed]:
            # Reconstruct question from history (simplified)
            failed_q_list.append({
                'question': fq.question_text,
                'options': ['Option A', 'Option B', 'Option C'],  # Simplified
                'answer': 'Correct Answer',  # Simplified
                'correctReason': 'This is the correct answer.',
                'incorrectReason': 'This is why other options are wrong.',
                'is_review': True,
                'difficulty_level': fq.difficulty_level,
                'personalized_hint': f"Review question - you've attempted this {fq.attempt_count} times"
            })
        adaptive_questions.extend(failed_q_list)
    
    # 20% mixed difficulty questions
    num_mixed = int(num_questions * 0.2)
    if num_mixed > 0:
        # Generate questions with varied difficulty
        mixed_questions = generate_ai_questions(stage, difficulty_level, num_mixed, user_id)
        adaptive_questions.extend(mixed_questions[:num_mixed])
    
    # 10% cultural/contextual questions
    num_cultural = num_questions - len(adaptive_questions)
    if num_cultural > 0 and user_id != "guest_user":
        # Generate culturally relevant questions
        cultural_questions = generate_cultural_questions(stage, difficulty_level, num_cultural)
        adaptive_questions.extend(cultural_questions)
    
    # Shuffle questions to avoid predictable patterns
    random.shuffle(adaptive_questions)
    
    return adaptive_questions[:num_questions]

def generate_ai_questions(stage, difficulty_level, num_questions=10, user_id=None):
    """Generate AI questions with difficulty adaptation and personalization"""
    
    # Validate stage
    valid_stages = ['preconception', 'prenatal', 'birth', 'postnatal']
    if stage not in valid_stages:
        return []
    
    try:
        # Lazy import to avoid circular dependency
        from .optimized_modelintegration import get_hybrid_questions
        # Use hybrid approach for better performance for all users
        ai_response = get_hybrid_questions(stage, user_id, difficulty_level)
        
        if 'error' in ai_response:
            return []
        
        # Filter by difficulty level (simplified implementation)
        questions = ai_response if isinstance(ai_response, list) else []
        
        # Add difficulty metadata and personalization
        for q in questions:
            q['difficulty_level'] = difficulty_level
            q['is_review'] = False
            q['is_personalized'] = user_id is not None
        
        return questions[:num_questions]
        
    except Exception as e:
        print(f"Error generating AI questions: {e}")
        return []

def record_question_attempt(user_id, stage, question_text, is_correct, difficulty_level=1):
    """Record a question attempt in the user's history"""
    
    question_hash = generate_question_hash(question_text)
    
    # Check if this question was attempted before
    existing = UserQuestionHistory.query.filter_by(
        user_id=user_id,
        stage=stage,
        question_hash=question_hash
    ).first()
    
    if existing:
        # Update existing record
        existing.attempt_count += 1
        existing.is_correct = is_correct
        existing.last_attempted = datetime.utcnow()
        existing.difficulty_level = difficulty_level
        
        # Mark for review if failed multiple times
        if not is_correct and existing.attempt_count >= 3:
            existing.needs_review = True
            
    else:
        # Create new record
        new_record = UserQuestionHistory(
            user_id=user_id,
            stage=stage,
            question_text=question_text,
            question_hash=question_hash,
            is_correct=is_correct,
            attempt_count=1,
            difficulty_level=difficulty_level,
            needs_review=not is_correct  # Mark for review if failed on first attempt
        )
        db.session.add(new_record)
    
    db.session.commit()

def get_learning_insights(user_id, stage):
    """Get comprehensive learning insights for the user"""
    
    recent_questions = get_recent_questions(user_id, stage, days=30)
    failed_questions = get_failed_questions(user_id, stage)
    
    if not recent_questions:
        return {
            'total_questions': 0,
            'accuracy': 0,
            'streak': 0,
            'needs_review': 0,
            'difficulty_level': 1,
            'learning_style': 'beginner',
            'weak_areas': [],
            'strong_areas': [],
            'learning_velocity': 0,
            'engagement_score': 0
        }
    
    correct_count = sum(1 for q in recent_questions if q.is_correct)
    accuracy = (correct_count / len(recent_questions)) * 100
    
    # Calculate streak (consecutive correct answers)
    streak = 0
    for q in reversed(recent_questions):
        if q.is_correct:
            streak += 1
        else:
            break
    
    # Analyze learning patterns
    learning_style = analyze_learning_style(recent_questions)
    weak_areas = identify_weak_areas(user_id, stage)
    strong_areas = identify_strong_areas(user_id, stage)
    learning_velocity = calculate_learning_velocity(user_id, stage)
    engagement_score = calculate_engagement_score(user_id, stage)
    
    return {
        'total_questions': len(recent_questions),
        'accuracy': round(accuracy, 1),
        'streak': streak,
        'needs_review': len(failed_questions),
        'difficulty_level': calculate_user_difficulty_level(user_id, stage),
        'learning_style': learning_style,
        'weak_areas': weak_areas,
        'strong_areas': strong_areas,
        'learning_velocity': learning_velocity,
        'engagement_score': engagement_score
    }

def analyze_learning_style(questions):
    """Analyze user's learning style based on question patterns"""
    if not questions:
        return 'beginner'
    
    # Analyze response patterns
    correct_questions = [q for q in questions if q.is_correct]
    incorrect_questions = [q for q in questions if not q.is_correct]
    
    # Calculate learning style based on patterns
    if len(correct_questions) / len(questions) >= 0.8:
        return 'fast_learner'
    elif len(correct_questions) / len(questions) >= 0.6:
        return 'steady_learner'
    elif len(correct_questions) / len(questions) >= 0.4:
        return 'careful_learner'
    else:
        return 'needs_support'

def identify_weak_areas(user_id, stage):
    """Identify areas where user struggles most"""
    failed_questions = get_failed_questions(user_id, stage)
    
    # Simple keyword analysis (can be enhanced with NLP)
    weak_areas = []
    if len(failed_questions) > 0:
        # Group by difficulty level
        difficulty_groups = {}
        for q in failed_questions:
            level = q.difficulty_level
            if level not in difficulty_groups:
                difficulty_groups[level] = 0
            difficulty_groups[level] += 1
        
        # Identify most problematic difficulty level
        if difficulty_groups:
            max_level = max(difficulty_groups, key=difficulty_groups.get)
            weak_areas.append(f"Level {max_level} concepts")
    
    return weak_areas

def identify_strong_areas(user_id, stage):
    """Identify areas where user excels"""
    recent_questions = get_recent_questions(user_id, stage, days=14)
    correct_questions = [q for q in recent_questions if q.is_correct]
    
    strong_areas = []
    if len(correct_questions) > 0:
        # Group by difficulty level
        difficulty_groups = {}
        for q in correct_questions:
            level = q.difficulty_level
            if level not in difficulty_groups:
                difficulty_groups[level] = 0
            difficulty_groups[level] += 1
        
        # Identify strongest difficulty level
        if difficulty_groups:
            max_level = max(difficulty_groups, key=difficulty_groups.get)
            strong_areas.append(f"Level {max_level} concepts")
    
    return strong_areas

def calculate_learning_velocity(user_id, stage):
    """Calculate how quickly user is learning (questions per day)"""
    recent_questions = get_recent_questions(user_id, stage, days=7)
    return len(recent_questions) / 7 if recent_questions else 0

def calculate_engagement_score(user_id, stage):
    """Calculate user engagement score (0-100)"""
    recent_questions = get_recent_questions(user_id, stage, days=7)
    
    if not recent_questions:
        return 0
    
    # Factors: frequency, accuracy, consistency
    frequency_score = min(100, len(recent_questions) * 10)  # Max 10 questions per day
    accuracy_score = sum(1 for q in recent_questions if q.is_correct) / len(recent_questions) * 100
    
    # Consistency: how many days in a row they've been active
    days_active = len(set(q.last_attempted.date() for q in recent_questions))
    consistency_score = min(100, days_active * 20)  # Max 5 days
    
    return round((frequency_score + accuracy_score + consistency_score) / 3, 1)

def get_personalized_question_prompt(user_id, stage, difficulty_level):
    """Generate personalized question prompts based on user profile"""
    
    insights = get_learning_insights(user_id, stage)
    learning_style = insights.get('learning_style', 'beginner')
    weak_areas = insights.get('weak_areas', [])
    
    # Base prompt
    base_prompts = {
        "preconception": "You are an AI that generates maternal health quizzes focused on preconception care.",
        "prenatal": "You are an AI that generates maternal health quizzes focused on prenatal care.",
        "birth": "You are an AI that generates maternal health quizzes focused on birth and delivery.",
        "postnatal": "You are an AI that generates maternal health quizzes focused on postnatal care."
    }
    
    base_prompt = base_prompts.get(stage, "You are an AI that generates maternal health quizzes.")
    
    # Personalization based on learning style
    if learning_style == 'fast_learner':
        personalization = " Focus on advanced concepts and complex scenarios. Include challenging questions that test deep understanding."
    elif learning_style == 'careful_learner':
        personalization = " Focus on foundational concepts with clear explanations. Include step-by-step reasoning questions."
    elif learning_style == 'needs_support':
        personalization = " Focus on basic concepts with extra explanations. Include visual and practical examples."
    else:
        personalization = " Focus on balanced difficulty with clear explanations."
    
    # Add weak area focus
    if weak_areas:
        personalization += f" Pay special attention to: {', '.join(weak_areas)}."
    
    # Difficulty level adjustment
    if difficulty_level == 1:
        personalization += " Use simple language and basic concepts."
    elif difficulty_level == 2:
        personalization += " Use intermediate concepts with some complexity."
    else:
        personalization += " Use advanced concepts and complex scenarios."
    
    return base_prompt + personalization

def generate_cultural_questions(stage, difficulty_level, num_questions):
    """Generate culturally relevant questions for African/Swahili context"""
    
    cultural_prompts = {
        "preconception": "Generate maternal health questions relevant to African communities, focusing on traditional practices, cultural beliefs, and local health challenges.",
        "prenatal": "Create prenatal care questions that consider African healthcare systems, traditional birth attendants, and community-based care.",
        "birth": "Develop birth and delivery questions that address common practices in African communities, including home births and traditional methods.",
        "postnatal": "Generate postnatal care questions relevant to African families, including traditional postpartum practices and community support."
    }
    
    base_prompt = cultural_prompts.get(stage, "Generate culturally relevant maternal health questions.")
    
    # Add difficulty context
    if difficulty_level == 1:
        base_prompt += " Use simple language and basic concepts suitable for community health workers."
    elif difficulty_level == 2:
        base_prompt += " Use intermediate concepts with some cultural complexity."
    else:
        base_prompt += " Use advanced concepts with deep cultural understanding."
    
    # For now, return empty list - can be enhanced with actual AI generation
    # This is a placeholder for future cultural question generation
    return []
