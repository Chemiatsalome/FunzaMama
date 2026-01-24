"""
Optimized Model Integration for Funza Mama
High-performance question generation with caching and async support
"""

from together import Together
import json
import time
import hashlib
from functools import lru_cache
from threading import Lock
# Lazy imports to avoid import errors when module is loaded outside Flask context
# db and models are imported only when needed inside functions that check for Flask context
# from models import db  # Imported lazily in get_questions_seen_in_database()
# from models.models import UserResponse, QuizQuestion  # Imported lazily in get_questions_seen_in_database()
# Lazy import to avoid circular dependency - only import when needed
# from chatbot.adaptive_learning import generate_question_hash

# Initialize Together AI client - use environment variable
import os
together_api_key = os.getenv('TOGETHER_API_KEY')
if not together_api_key:
    print("⚠️ WARNING: TOGETHER_API_KEY not set. Question generation will fail.")
    together_client = None
else:
    try:
        together_client = Together(api_key=together_api_key)
        print("✅ Together AI client initialized for question generation")
    except Exception as e:
        print(f"⚠️ WARNING: Failed to initialize Together AI client: {e}")
        together_client = None

# Cache for storing generated questions
question_cache = {}
cache_lock = Lock()
CACHE_SIZE = 100  # Maximum number of cached question sets
CACHE_TTL = 3600  # Cache time-to-live in seconds (1 hour)

# Session-based question tracking to prevent repetition
session_questions = {}
session_lock = Lock()

# Enhanced session management with localStorage fallback
def get_session_storage_key(stage, user_id):
    """Generate a localStorage key for client-side session tracking"""
    return f"funza_mama_questions_{stage}_{user_id}"

def clear_stage_session(stage, user_id):
    """Clear session data for a specific stage and user"""
    with session_lock:
        session_key = get_session_key(stage, user_id)
        if session_key in session_questions:
            del session_questions[session_key]
    
    # Also clear from localStorage (will be handled by frontend)
    print(f"Cleared session data for {stage} stage, user {user_id}")

def reset_stage_questions(stage, user_id):
    """Reset all question tracking for a stage restart"""
    clear_stage_session(stage, user_id)
    
    # Clear cache for this stage/user combination
    cache_key = generate_cache_key(stage, user_id, 1)
    with cache_lock:
        if cache_key in question_cache:
            del question_cache[cache_key]
    
    print(f"Reset all question data for {stage} stage, user {user_id}")

# Optimized prompts - shorter and more focused
OPTIMIZED_PROMPTS = {
    "preconception": """Generate 10 completely unique and diverse maternal health quiz questions for preconception care. Each question must be different from the others. Cover: folic acid timing/dosage, pre-pregnancy checkups, lifestyle changes, genetic counseling, fertility awareness, vaccinations, chronic disease management. Each question should have 3 specific, realistic options (NOT generic A, B, C), correct answer, and explanations. IMPORTANT: Return ONLY valid JSON array format with proper commas and no multiline strings in options. Each option must be on one line. Format: [{"question": "text", "options": ["option1", "option2", "option3"], "answer": "answer", "correctReason": "reason", "incorrectReason": "reason"}]""",
    
    "prenatal": """Generate exactly 10 completely unique and diverse maternal health quiz questions for prenatal care. Each question must be different from the others. Cover: trimester-specific nutrition, safe exercise, prenatal visits, warning signs, weight gain, discomforts, screening tests, complications. Each question must have 3 specific, realistic options (NOT generic A, B, C), correct answer, and explanations. Return ONLY valid JSON array:
[{"question": "What is the recommended daily calorie increase during pregnancy?", "options": ["300-500 extra calories", "500-700 extra calories", "No increase needed"], "answer": "300-500 extra calories", "correctReason": "Most women need 300-500 extra calories per day during pregnancy.", "incorrectReason": "Other amounts are not typically recommended for healthy pregnancies."}]""",
    
    "birth": """Generate 10 completely unique and diverse maternal health quiz questions for birth and delivery. Each question must be different from the others. Cover: labor stages, pain management, delivery positions, medical interventions, emergencies, postpartum recovery, newborn care, breastfeeding initiation. Each question should have 3 specific, realistic options (NOT generic A, B, C), correct answer, and explanations. IMPORTANT: Return ONLY valid JSON array format with proper commas and no multiline strings in options. Each option must be on one line. Format: [{"question": "text", "options": ["option1", "option2", "option3"], "answer": "answer", "correctReason": "reason", "incorrectReason": "reason"}]""",
    
    "postnatal": """Generate 10 completely unique and diverse maternal health quiz questions for postnatal care. Each question must be different from the others. Cover: newborn feeding, sleep patterns, developmental milestones, maternal recovery, breastfeeding challenges, family planning, postpartum depression, infant safety. Each question should have 3 specific, realistic options (NOT generic A, B, C), correct answer, and explanations. Return ONLY valid JSON array format:
[{"question": "...", "options": ["...", "...", "..."], "answer": "...", "correctReason": "...", "incorrectReason": "..."}]"""
}

def generate_cache_key(stage, user_id, difficulty_level=1):
    """Generate a cache key for question sets"""
    return hashlib.md5(f"{stage}_{user_id}_{difficulty_level}".encode()).hexdigest()

def get_session_key(stage, user_id):
    """Generate a session key for question tracking"""
    return f"{stage}_{user_id}"

def track_session_question(stage, user_id, question_text):
    """Track a question shown in the current session"""
    with session_lock:
        session_key = get_session_key(stage, user_id)
        if session_key not in session_questions:
            session_questions[session_key] = set()
        session_questions[session_key].add(question_text.strip().lower())

def is_question_seen_in_session(stage, user_id, question_text):
    """Check if a question has been shown in the current session"""
    with session_lock:
        session_key = get_session_key(stage, user_id)
        if session_key not in session_questions:
            return False
        return question_text.strip().lower() in session_questions[session_key]

def get_questions_seen_in_database(user_id, stage):
    """Get all questions user has seen in this stage from database (across all rounds)"""
    if user_id == "guest_user":
        return set()
    
    try:
        # Lazy import to avoid circular dependencies
        from sqlalchemy import and_
        
        # Normalize stage name to match database storage (birth -> birth_and_delivery)
        # IMPORTANT: This normalization MUST match what's used when saving UserResponse.stage
        # See routes/gamelogic.py submit_response() and test_question_filtering.py simulate_round()
        # "preconception", "prenatal", "postnatal" stay as-is (no change)
        # "birth" -> "birth_and_delivery" (must match database storage)
        stage_normalization = {
            "birth": "birth_and_delivery",
            "preconception": "preconception",  # No change needed
            "prenatal": "prenatal",  # No change needed
            "postnatal": "postnatal"  # No change needed
        }
        db_stage = stage_normalization.get(stage, stage)
        
        # Get all quiz questions that user has responded to for this stage
        # Join UserResponse with QuizQuestion to get the question text
        # Use try-except for app context in case called outside Flask request
        try:
            from flask import has_app_context, current_app
            if not has_app_context():
                # No app context - return empty set (can't query database)
                print(f"Debug - No app context for database query, returning empty set")
                return set()
        except ImportError:
            # Not in Flask context - return empty set
            return set()
        
        # Lazy import to avoid errors when module is loaded outside Flask context
        from models import db
        from models.models import UserResponse, QuizQuestion
        
        responses = db.session.query(QuizQuestion.question).join(
            UserResponse, QuizQuestion.id == UserResponse.question_id
        ).filter(
            and_(
                UserResponse.user_id == user_id,
                UserResponse.stage == db_stage
            )
        ).distinct().all()
        
        # Extract question texts and normalize
        seen_questions = set()
        for (question_text,) in responses:
            if question_text:
                seen_questions.add(question_text.strip().lower())
        
        print(f"Debug - Found {len(seen_questions)} unique questions in database for {stage} (db_stage={db_stage})")
        return seen_questions
    except Exception as e:
        print(f"Error getting questions from database: {e}")
        import traceback
        traceback.print_exc()
        return set()  # Return empty set on error - better to show questions than crash

def get_failed_questions_from_database(user_id, stage, max_count=5):
    """Get failed questions (is_correct=False) for user/stage from database for adaptive learning
    
    Returns a list of question dictionaries (similar to QuizQuestion format) that user got wrong,
    prioritizing questions that were failed multiple times.
    
    Args:
        user_id: User ID
        stage: Stage name
        max_count: Maximum number of failed questions to return
    
    Returns:
        List of question dictionaries with 'question', 'options', 'answer', 'correctReason', 'incorrectReason'
    """
    if user_id == "guest_user":
        return []
    
    try:
        # Lazy import to avoid circular dependencies
        from sqlalchemy import and_, func
        import json
        
        # Normalize stage name to match database storage
        stage_normalization = {
            "birth": "birth_and_delivery",
            "preconception": "preconception",
            "prenatal": "prenatal",
            "postnatal": "postnatal"
        }
        db_stage = stage_normalization.get(stage, stage)
        
        # Check Flask app context
        try:
            from flask import has_app_context
            if not has_app_context():
                print(f"Debug - No app context for failed questions query, returning empty list")
                return []
        except ImportError:
            return []
        
        # Lazy import to avoid errors when module is loaded outside Flask context
        from models import db
        from models.models import UserResponse, QuizQuestion
        
        # Query for failed questions (is_correct=False)
        # Join UserResponse with QuizQuestion to get full question details
        # Group by question_id and count failures to prioritize questions failed multiple times
        failed_questions_query = db.session.query(
            QuizQuestion.id,
            QuizQuestion.question,
            QuizQuestion.options,
            QuizQuestion.answer,
            QuizQuestion.correct_reason,
            QuizQuestion.incorrect_reason,
            func.count(UserResponse.id).label('failure_count')
        ).join(
            UserResponse, QuizQuestion.id == UserResponse.question_id
        ).filter(
            and_(
                UserResponse.user_id == user_id,
                UserResponse.stage == db_stage,
                UserResponse.is_correct == False  # Only failed questions
            )
        ).group_by(
            QuizQuestion.id,
            QuizQuestion.question,
            QuizQuestion.options,
            QuizQuestion.answer,
            QuizQuestion.correct_reason,
            QuizQuestion.incorrect_reason
        ).order_by(
            func.count(UserResponse.id).desc()  # Prioritize questions failed more times
        ).limit(max_count).all()
        
        # Convert to question dictionaries
        failed_questions = []
        for (q_id, question_text, options_json, answer, correct_reason, incorrect_reason, failure_count) in failed_questions_query:
            try:
                # Parse options JSON string
                options = json.loads(options_json) if isinstance(options_json, str) else options_json
                if not isinstance(options, list):
                    options = []
            except (json.JSONDecodeError, TypeError):
                options = []
            
            question_dict = {
                'question': question_text,
                'options': options,
                'answer': answer,
                'correctReason': correct_reason or '',
                'incorrectReason': incorrect_reason or '',
                'failure_count': failure_count,  # Track how many times this was failed
                'needs_review': True  # Mark as needing review
            }
            failed_questions.append(question_dict)
        
        print(f"Debug - Found {len(failed_questions)} failed questions for {stage} (db_stage={db_stage})")
        return failed_questions
    except Exception as e:
        print(f"Error getting failed questions from database: {e}")
        import traceback
        traceback.print_exc()
        return []  # Return empty list on error - better to continue than crash

def filter_unseen_questions(stage, user_id, questions):
    """Filter out questions that have been seen in current session OR database (all rounds)"""
    # Get questions seen in database (persistent across rounds)
    db_seen_questions = get_questions_seen_in_database(user_id, stage)
    
    unseen_questions = []
    for q in questions:
        question_text = q.get('question', '').strip().lower()
        # Skip if seen in current session OR in database
        if question_text and not is_question_seen_in_session(stage, user_id, question_text):
            if question_text not in db_seen_questions:
                unseen_questions.append(q)
    
    print(f"Debug - filter_unseen_questions: {len(questions)} total, {len(db_seen_questions)} seen in DB, {len(unseen_questions)} unseen")
    return unseen_questions

def is_cache_valid(cache_entry):
    """Check if cache entry is still valid"""
    return time.time() - cache_entry['timestamp'] < CACHE_TTL

def get_cached_questions(stage, user_id, difficulty_level=1):
    """Get questions from cache if available and valid"""
    cache_key = generate_cache_key(stage, user_id, difficulty_level)
    
    with cache_lock:
        if cache_key in question_cache:
            cache_entry = question_cache[cache_key]
            if is_cache_valid(cache_entry):
                print(f"Cache hit for {stage} questions")
                return cache_entry['questions']
            else:
                # Remove expired cache entry
                del question_cache[cache_key]
    
    return None

def cache_questions(stage, user_id, questions, difficulty_level=1):
    """Cache generated questions"""
    cache_key = generate_cache_key(stage, user_id, difficulty_level)
    
    with cache_lock:
        # Remove oldest entries if cache is full
        if len(question_cache) >= CACHE_SIZE:
            oldest_key = min(question_cache.keys(), key=lambda k: question_cache[k]['timestamp'])
            del question_cache[oldest_key]
        
        question_cache[cache_key] = {
            'questions': questions,
            'timestamp': time.time()
        }
    
    print(f"Cached {len(questions)} questions for {stage}")

def generate_questions_optimized(stage, user_id="guest_user", difficulty_level=1, skip_cache=False):
    """Optimized question generation with caching and faster AI parameters
    
    Args:
        stage: Stage name
        user_id: User ID
        difficulty_level: Difficulty level
        skip_cache: If True, bypass cache and generate new questions
    """
    
    # Check cache first (unless explicitly skipped)
    if not skip_cache:
        cached_questions = get_cached_questions(stage, user_id, difficulty_level)
        if cached_questions:
            return cached_questions
    
    print(f"Generating new questions for {stage}...")
    start_time = time.time()
    
    try:
        # Use optimized AI parameters for speed - SWITCHED TO FASTER 8B MODEL
        # Using 8B model instead of 405B for 10-20x faster generation
        # Try different model name formats in case API changes
        # Using Llama as primary since GLM-4.7 returns empty responses
        # GLM-4.7 might not be available or might require different parameters
        model_names = [
            "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",  # Primary - proven to work
            "meta-llama/Llama-3.1-8B-Instruct",  # Without Turbo suffix
            "zai-org/GLM-4.7",  # GLM-4.7 as fallback (currently returns empty, may need different setup)
        ]
        
        response = None
        last_error = None
        for model_name in model_names:
            try:
                response = together_client.chat.completions.create(
                    model=model_name,  # Try each model name
                    messages=[
                        {"role": "system", "content": OPTIMIZED_PROMPTS[stage]},
                        {"role": "user", "content": f"Generate 10 {stage} quiz questions in JSON format. CRITICAL: Return ONLY a valid JSON array with proper commas. Each option must be on one line without newlines inside quotes."}
                    ],
                    max_tokens=2000,   # Increased to allow complete JSON responses
                    temperature=0.3,  # Slightly higher for variety but still focused
                    top_p=0.95,        # Higher for better quality
                    top_k=50,         # Balanced for speed/quality
                    repetition_penalty=1.1,
                    stop=["\n\n\n", "```"],  # Only stop on triple newlines
                )
                print(f"✅ Successfully used model: {model_name}")
                break  # Success, exit loop
            except Exception as e:
                last_error = e
                print(f"❌ Model {model_name} failed: {e}")
                continue  # Try next model
        
        # If all models failed, raise the last error
        if response is None:
            raise Exception(f"All model attempts failed. Last error: {last_error}")
        
        # Parse response - check if content exists
        if not response.choices or not response.choices[0].message.content:
            print(f"Debug - Model {model_name} returned empty response")
            print(f"Debug - Response object: {response}")
            print(f"Debug - Choices: {response.choices if hasattr(response, 'choices') else 'No choices attr'}")
            raise Exception(f"Model {model_name} returned empty content")
        
        response_text = response.choices[0].message.content.strip()
        
        # Debug: Print first 1000 chars of response to see what model returned
        print(f"Debug - Raw response from {model_name} (first 1000 chars): {response_text[:1000]}")
        
        # Clean and parse JSON
        response_text = response_text.strip()
        
        # Remove markdown code blocks
        if response_text.startswith("```json"):
            response_text = response_text[7:-3]
        elif response_text.startswith("```"):
            response_text = response_text[3:-3]
        
        # Find JSON array in the response - improved parsing
        start_idx = response_text.find('[')
        end_idx = response_text.rfind(']')
        
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            response_text = response_text[start_idx:end_idx + 1]
        else:
            # Try to find JSON objects and wrap them in an array
            import re
            # Look for JSON objects in the text (more flexible pattern)
            json_objects = re.findall(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response_text, re.DOTALL)
            if json_objects:
                response_text = '[' + ','.join(json_objects) + ']'
                print(f"Debug - Found {len(json_objects)} JSON objects, wrapped in array")
            else:
                # If no JSON found, print more details and try regex extraction
                print(f"Debug - No valid JSON array found in response")
                print(f"Debug - Response length: {len(response_text)}")
                has_bracket = '[' in response_text
                has_brace = '{' in response_text
                print(f"Debug - Contains '[': {has_bracket}, Contains '{{': {has_brace}")
                # Don't return empty yet - let regex extraction try
        
        try:
            questions = json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Response text: {response_text[:500]}...")
            
            # Try to fix common JSON errors
            try:
                # Fix missing commas between array elements
                import re
                # Add comma before closing quotes in arrays if missing
                fixed_json = re.sub(r'"\s*\n\s*"', '",\n"', response_text)  # Fix missing commas in arrays
                # Fix missing commas before closing braces
                fixed_json = re.sub(r'"\s*\n\s*\}', '"\n}', fixed_json)
                # Fix missing commas between objects in array
                fixed_json = re.sub(r'\}\s*\n\s*\{', '},\n{', fixed_json)
                
                # Try parsing again with fixed JSON
                questions = json.loads(fixed_json)
                print(f"✅ Fixed JSON parsing errors and successfully parsed {len(questions)} questions")
            except (json.JSONDecodeError, Exception) as e2:
                print(f"❌ Could not fix JSON errors: {e2}")
                # Last resort: try to extract questions manually using improved regex
                # Handle multiline JSON that the model generates
                try:
                    # Better regex patterns that handle multiline strings
                    question_pattern = r'"question"\s*:\s*"((?:[^"\\]|\\.)*)"'
                    options_pattern = r'"options"\s*:\s*\[(.*?)\]'
                    answer_pattern = r'"answer"\s*:\s*"((?:[^"\\]|\\.)*)"'
                    correct_reason_pattern = r'"correctReason"\s*:\s*"((?:[^"\\]|\\.)*)"'
                    incorrect_reason_pattern = r'"incorrectReason"\s*:\s*"((?:[^"\\]|\\.)*)"'
                    
                    # Extract all JSON objects (including multiline)
                    # Use a more robust pattern that handles nested structures
                    json_objects = re.findall(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response_text, re.DOTALL)
                    if not json_objects:
                        # Try simpler pattern if complex one fails
                        json_objects = re.findall(r'\{[^}]+\}', response_text, re.DOTALL)
                    
                    if json_objects:
                        parsed = []
                        for obj_str in json_objects:
                            q_match = re.search(question_pattern, obj_str, re.DOTALL)
                            a_match = re.search(answer_pattern, obj_str, re.DOTALL)
                            opts_match = re.search(options_pattern, obj_str, re.DOTALL)
                            cr_match = re.search(correct_reason_pattern, obj_str, re.DOTALL)
                            ir_match = re.search(incorrect_reason_pattern, obj_str, re.DOTALL)
                            
                            if q_match and a_match:
                                options = []
                                if opts_match:
                                    opts_str = opts_match.group(1)
                                    # Extract quoted strings (handles newlines and escaped quotes)
                                    option_matches = re.findall(r'"(?:[^"\\]|\\.)*"', opts_str)
                                    options = [opt.strip('"').replace('\\"', '"').replace('\\n', ' ') for opt in option_matches]
                                
                                # Need at least 3 options, but extract as many as possible
                                if len(options) >= 3:
                                    parsed.append({
                                        "question": q_match.group(1).replace('\\"', '"').replace('\\n', ' '),
                                        "options": options[:3],
                                        "answer": a_match.group(1).replace('\\"', '"').replace('\\n', ' '),
                                        "correctReason": cr_match.group(1).replace('\\"', '"').replace('\\n', ' ') if cr_match else "This is the correct answer.",
                                        "incorrectReason": ir_match.group(1).replace('\\"', '"').replace('\\n', ' ') if ir_match else "This is incorrect."
                                    })
                        
                        if parsed:
                            questions = parsed
                            print(f"✅ Extracted {len(questions)} questions from AI model using regex fallback")
                        else:
                            questions = []
                    else:
                        questions = []
                except Exception as e3:
                    print(f"❌ Regex extraction also failed: {e3}")
                    questions = []
        
        # Validate and clean questions
        cleaned_questions = []
        for q in questions:
            if isinstance(q, dict) and 'question' in q and 'options' in q and 'answer' in q:
                # Check if options are generic and skip if so
                options = q.get('options', [])
                if len(options) == 3 and all(opt in ['A', 'B', 'C', 'Option A', 'Option B', 'Option C'] for opt in options):
                    print(f"Skipping question with generic options: {q.get('question', '')[:50]}...")
                    continue
                
                # Ensure all required fields exist
                cleaned_q = {
                    'question': q.get('question', ''),
                    'options': options if options else ['Option A', 'Option B', 'Option C'],
                    'answer': q.get('answer', ''),
                    'correctReason': q.get('correctReason', 'This is the correct answer.'),
                    'incorrectReason': q.get('incorrectReason', 'This is incorrect.'),
                    'difficulty_level': difficulty_level,
                    'is_personalized': user_id != "guest_user"
                }
                cleaned_questions.append(cleaned_q)
        
        # Cache the questions
        if cleaned_questions:
            cache_questions(stage, user_id, cleaned_questions, difficulty_level)
        
        generation_time = time.time() - start_time
        print(f"Generated {len(cleaned_questions)} questions in {generation_time:.2f} seconds")
        
        return cleaned_questions
        
    except Exception as e:
        print(f"Error generating questions: {e}")
        return {"error": f"Failed to generate questions: {str(e)}"}

# Optimized wrapper functions
def get_chatbot_response_preconception(user_id):
    """Fast preconception question generation"""
    return generate_questions_optimized("preconception", user_id)

def get_chatbot_response_prenatal(user_id):
    """Fast prenatal question generation"""
    return generate_questions_optimized("prenatal", user_id)

def get_chatbot_response_birth(user_id):
    """Fast birth question generation"""
    return generate_questions_optimized("birth", user_id)

def get_chatbot_response_postnatal(user_id):
    """Fast postnatal question generation"""
    return generate_questions_optimized("postnatal", user_id)

# Pre-generated question pools for instant response
PREDEFINED_QUESTIONS = {
    "preconception": [
        {
            "question": "What is the recommended amount of folic acid supplements before conception?",
            "options": ["400 mcg daily", "800 mcg daily", "1200 mcg daily"],
            "answer": "400 mcg daily",
            "correctReason": "400 mcg daily is the standard recommendation for women planning pregnancy.",
            "incorrectReason": "Higher doses are only recommended for women with specific risk factors."
        },
        {
            "question": "When should you start taking prenatal vitamins?",
            "options": ["After getting pregnant", "3 months before conception", "1 year before conception"],
            "answer": "3 months before conception",
            "correctReason": "Starting 3 months before conception helps ensure optimal nutrient levels.",
            "incorrectReason": "Starting too late may not provide adequate preparation for pregnancy."
        },
        {
            "question": "What lifestyle changes should you make before getting pregnant?",
            "options": ["Stop smoking and drinking", "Start exercising regularly", "Both A and B"],
            "answer": "Both A and B",
            "correctReason": "Both smoking cessation and regular exercise improve pregnancy outcomes.",
            "incorrectReason": "Only one change alone is not sufficient for optimal preparation."
        },
        {
            "question": "How much weight should you gain during pregnancy if you're at a healthy weight?",
            "options": ["15-25 pounds", "25-35 pounds", "35-45 pounds"],
            "answer": "25-35 pounds",
            "correctReason": "25-35 pounds is the recommended weight gain for women with healthy BMI.",
            "incorrectReason": "Other amounts are recommended for different BMI categories."
        },
        {
            "question": "What should you avoid during preconception planning?",
            "options": ["Raw fish and unpasteurized foods", "Excessive caffeine", "Both A and B"],
            "answer": "Both A and B",
            "correctReason": "Both raw fish and excessive caffeine should be limited before and during pregnancy.",
            "incorrectReason": "Only avoiding one is not sufficient for optimal health."
        },
        {
            "question": "How long before conception should you start taking folic acid?",
            "options": ["1 month", "3 months", "6 months"],
            "answer": "3 months",
            "correctReason": "Starting folic acid 3 months before conception helps prevent birth defects.",
            "incorrectReason": "Starting too late may not provide adequate protection."
        },
        {
            "question": "What is the recommended BMI range for optimal fertility?",
            "options": ["18.5-24.9", "25-29.9", "30-34.9"],
            "answer": "18.5-24.9",
            "correctReason": "A BMI between 18.5-24.9 is associated with optimal fertility outcomes.",
            "incorrectReason": "Higher or lower BMI can affect fertility and pregnancy outcomes."
        },
        {
            "question": "When should you stop using hormonal contraception before trying to conceive?",
            "options": ["Immediately", "1-3 months before", "6 months before"],
            "answer": "1-3 months before",
            "correctReason": "Stopping 1-3 months before allows your cycle to normalize.",
            "incorrectReason": "Stopping too early or too late can affect conception timing."
        },
        {
            "question": "What lifestyle factor most affects male fertility?",
            "options": ["Exercise", "Smoking", "Diet"],
            "answer": "Smoking",
            "correctReason": "Smoking significantly reduces sperm count and motility.",
            "incorrectReason": "While exercise and diet matter, smoking has the most direct impact on fertility."
        },
        {
            "question": "What is the recommended daily water intake before pregnancy?",
            "options": ["6-8 glasses", "8-10 glasses", "10-12 glasses"],
            "answer": "8-10 glasses",
            "correctReason": "Adequate hydration (8-10 glasses daily) supports overall health and fertility.",
            "incorrectReason": "Other amounts may not provide optimal hydration for preconception health."
        },
        {
            "question": "What vaccinations should you get before pregnancy?",
            "options": ["MMR and varicella", "Flu shot only", "No vaccinations needed"],
            "answer": "MMR and varicella",
            "correctReason": "MMR and varicella vaccines protect against serious infections during pregnancy.",
            "incorrectReason": "Flu shot is also important but MMR and varicella are critical before conception."
        },
        {
            "question": "When should you stop drinking alcohol before trying to conceive?",
            "options": ["When you find out you're pregnant", "1 month before", "3 months before"],
            "answer": "3 months before",
            "correctReason": "Stopping alcohol 3 months before conception helps ensure optimal health.",
            "incorrectReason": "Waiting until pregnancy confirmation may be too late to prevent issues."
        },
        {
            "question": "What is the recommended amount of vitamin D for preconception?",
            "options": ["400 IU daily", "600 IU daily", "1000 IU daily"],
            "answer": "600 IU daily",
            "correctReason": "600 IU daily of vitamin D supports fertility and bone health before pregnancy.",
            "incorrectReason": "Other amounts may not provide adequate vitamin D for preconception health."
        }
    ],
    "prenatal": [
        {
            "question": "How often should you visit your healthcare provider during pregnancy?",
            "options": ["Once a month", "Every 2 weeks", "As recommended by your provider"],
            "answer": "As recommended by your provider",
            "correctReason": "Visit frequency varies based on individual needs and pregnancy stage.",
            "incorrectReason": "A fixed schedule doesn't account for individual health needs."
        },
        {
            "question": "What is the recommended daily calorie increase during pregnancy?",
            "options": ["300-500 extra calories", "500-700 extra calories", "No increase needed"],
            "answer": "300-500 extra calories",
            "correctReason": "Most women need 300-500 extra calories per day during pregnancy.",
            "incorrectReason": "Other amounts are not typically recommended for healthy pregnancies."
        },
        {
            "question": "When should you start feeling fetal movement?",
            "options": ["12-16 weeks", "16-20 weeks", "20-24 weeks"],
            "answer": "16-20 weeks",
            "correctReason": "Most women feel fetal movement between 16-20 weeks of pregnancy.",
            "incorrectReason": "Earlier or later timing may indicate other factors."
        },
        {
            "question": "What is the recommended amount of iron during pregnancy?",
            "options": ["18 mg daily", "27 mg daily", "45 mg daily"],
            "answer": "27 mg daily",
            "correctReason": "Pregnant women need 27 mg of iron daily to prevent anemia.",
            "incorrectReason": "Other amounts are not sufficient for pregnancy needs."
        },
        {
            "question": "How much water should you drink daily during pregnancy?",
            "options": ["6-8 glasses", "8-10 glasses", "10-12 glasses"],
            "answer": "8-10 glasses",
            "correctReason": "8-10 glasses of water daily helps maintain proper hydration during pregnancy.",
            "incorrectReason": "Other amounts may not provide adequate hydration."
        },
        {
            "question": "What is the recommended weight gain for a woman with normal BMI?",
            "options": ["15-25 pounds", "25-35 pounds", "35-45 pounds"],
            "answer": "25-35 pounds",
            "correctReason": "Women with normal BMI should gain 25-35 pounds during pregnancy.",
            "incorrectReason": "Other amounts are recommended for different BMI categories."
        },
        {
            "question": "When should you start taking prenatal vitamins?",
            "options": ["Before pregnancy", "After getting pregnant", "In the second trimester"],
            "answer": "Before pregnancy",
            "correctReason": "Starting prenatal vitamins before pregnancy ensures optimal nutrient levels.",
            "incorrectReason": "Starting too late may not provide adequate preparation."
        },
        {
            "question": "What exercise is generally safe during pregnancy?",
            "options": ["High-intensity workouts", "Moderate walking and swimming", "Contact sports"],
            "answer": "Moderate walking and swimming",
            "correctReason": "Moderate exercise like walking and swimming is safe and beneficial during pregnancy.",
            "incorrectReason": "High-intensity or contact sports may pose risks during pregnancy."
        },
        {
            "question": "How often should you eat during pregnancy?",
            "options": ["3 large meals", "6 small meals", "Only when hungry"],
            "answer": "6 small meals",
            "correctReason": "Eating 6 small meals helps maintain stable blood sugar and reduces nausea.",
            "incorrectReason": "Large meals or irregular eating may cause discomfort."
        },
        {
            "question": "What should you avoid during pregnancy?",
            "options": ["Raw fish and unpasteurized foods", "Fresh fruits and vegetables", "Whole grains"],
            "answer": "Raw fish and unpasteurized foods",
            "correctReason": "Raw fish and unpasteurized foods may contain harmful bacteria.",
            "incorrectReason": "Fresh fruits, vegetables, and whole grains are beneficial during pregnancy."
        },
        {
            "question": "When should you call your healthcare provider during pregnancy?",
            "options": ["Only at scheduled visits", "For any concerns or unusual symptoms", "Only for severe pain"],
            "answer": "For any concerns or unusual symptoms",
            "correctReason": "It's important to contact your provider for any concerns during pregnancy.",
            "incorrectReason": "Waiting for severe symptoms may delay important care."
        },
        {
            "question": "What is the recommended sleep position during pregnancy?",
            "options": ["On your back", "On your stomach", "On your left side"],
            "answer": "On your left side",
            "correctReason": "Sleeping on your left side improves circulation and reduces pressure on major blood vessels.",
            "incorrectReason": "Other positions may cause discomfort or circulation issues."
        },
        {
            "question": "How much folic acid should you take during pregnancy?",
            "options": ["400 mcg daily", "600 mcg daily", "800 mcg daily"],
            "answer": "600 mcg daily",
            "correctReason": "Pregnant women need 600 mcg of folic acid daily to prevent birth defects.",
            "incorrectReason": "Other amounts are not sufficient for pregnancy needs."
        }
    ],
    "birth": [
        {
            "question": "What are the signs of true labor?",
            "options": ["Regular contractions", "Water breaking", "Both A and B"],
            "answer": "Both A and B",
            "correctReason": "True labor involves regular contractions and may include water breaking.",
            "incorrectReason": "Only one sign alone may not indicate true labor."
        },
        {
            "question": "When should you go to the hospital during labor?",
            "options": ["At first contraction", "When contractions are 5 minutes apart", "When water breaks"],
            "answer": "When contractions are 5 minutes apart",
            "correctReason": "Go to hospital when contractions are 5 minutes apart for 1 hour.",
            "incorrectReason": "Going too early or too late can cause complications."
        },
        {
            "question": "What is the average duration of active labor?",
            "options": ["2-4 hours", "4-8 hours", "8-12 hours"],
            "answer": "4-8 hours",
            "correctReason": "Active labor typically lasts 4-8 hours for first-time mothers.",
            "incorrectReason": "Other durations may indicate complications or different labor stages."
        },
        {
            "question": "What breathing technique helps during labor?",
            "options": ["Deep breathing", "Shallow panting", "Holding breath"],
            "answer": "Deep breathing",
            "correctReason": "Deep breathing helps manage pain and provides oxygen during labor.",
            "incorrectReason": "Other breathing patterns may not be as effective."
        },
        {
            "question": "What should you bring to the hospital for delivery?",
            "options": ["Insurance card and ID", "Comfortable clothes", "Both A and B"],
            "answer": "Both A and B",
            "correctReason": "Both identification and comfortable clothes are essential for hospital delivery.",
            "incorrectReason": "Only bringing one is not sufficient preparation."
        },
        {
            "question": "What is the first stage of labor?",
            "options": ["Pushing", "Contractions and dilation", "Delivery"],
            "answer": "Contractions and dilation",
            "correctReason": "The first stage involves contractions that dilate the cervix.",
            "incorrectReason": "Pushing and delivery occur in later stages of labor."
        },
        {
            "question": "When should you call your healthcare provider during labor?",
            "options": ["At first contraction", "When contractions are 5 minutes apart", "When water breaks"],
            "answer": "When contractions are 5 minutes apart",
            "correctReason": "Call when contractions are 5 minutes apart for 1 hour.",
            "incorrectReason": "Calling too early or too late can cause complications."
        },
        {
            "question": "What is the average duration of the second stage of labor?",
            "options": ["30 minutes", "1-2 hours", "3-4 hours"],
            "answer": "1-2 hours",
            "correctReason": "The second stage (pushing) typically lasts 1-2 hours for first-time mothers.",
            "incorrectReason": "Other durations may indicate complications or different labor patterns."
        },
        {
            "question": "What position is generally recommended for pushing?",
            "options": ["Lying flat", "Semi-sitting or squatting", "Standing"],
            "answer": "Semi-sitting or squatting",
            "correctReason": "Semi-sitting or squatting positions help with effective pushing.",
            "incorrectReason": "Lying flat or standing may not be as effective for delivery."
        },
        {
            "question": "What is the purpose of the third stage of labor?",
            "options": ["Delivery of baby", "Delivery of placenta", "Recovery"],
            "answer": "Delivery of placenta",
            "correctReason": "The third stage involves delivery of the placenta after the baby is born.",
            "incorrectReason": "The baby is delivered in the second stage, not the third."
        },
        {
            "question": "What is the recommended duration for skin-to-skin contact after birth?",
            "options": ["5 minutes", "At least 1 hour", "Only after medical procedures"],
            "answer": "At least 1 hour",
            "correctReason": "At least 1 hour of skin-to-skin contact promotes bonding and breastfeeding.",
            "incorrectReason": "Shorter duration may not provide the full benefits of skin-to-skin contact."
        },
        {
            "question": "What should you do if your water breaks before contractions start?",
            "options": ["Wait at home", "Call your healthcare provider immediately", "Go to hospital immediately"],
            "answer": "Call your healthcare provider immediately",
            "correctReason": "You should call your provider when water breaks, even without contractions.",
            "incorrectReason": "Water breaking requires medical guidance, not just waiting or rushing to hospital."
        },
        {
            "question": "What is the purpose of an epidural during labor?",
            "options": ["Speed up labor", "Provide pain relief", "Prevent complications"],
            "answer": "Provide pain relief",
            "correctReason": "Epidurals are used primarily for pain relief during labor.",
            "incorrectReason": "Epidurals don't speed up labor or prevent all complications."
        }
    ],
    "postnatal": [
        {
            "question": "When should you start breastfeeding after delivery?",
            "options": ["Within 1 hour", "After 6 hours", "The next day"],
            "answer": "Within 1 hour",
            "correctReason": "Early breastfeeding helps establish milk supply and bonding.",
            "incorrectReason": "Delaying breastfeeding can affect milk production."
        },
        {
            "question": "How often should you feed a newborn?",
            "options": ["Every 2-3 hours", "Every 4-6 hours", "Only when crying"],
            "answer": "Every 2-3 hours",
            "correctReason": "Newborns should be fed every 2-3 hours, even if not crying.",
            "incorrectReason": "Other feeding schedules may not meet newborn nutritional needs."
        },
        {
            "question": "What is the recommended sleep position for newborns?",
            "options": ["On their back", "On their side", "On their stomach"],
            "answer": "On their back",
            "correctReason": "Back sleeping reduces the risk of SIDS (Sudden Infant Death Syndrome).",
            "incorrectReason": "Other positions increase the risk of SIDS."
        },
        {
            "question": "When should you call the doctor after delivery?",
            "options": ["If you have fever over 100.4°F", "If bleeding increases", "Both A and B"],
            "answer": "Both A and B",
            "correctReason": "Both fever and increased bleeding are signs that require medical attention.",
            "incorrectReason": "Only one symptom alone may not indicate a problem."
        },
        {
            "question": "How long should you wait before resuming normal activities?",
            "options": ["1-2 weeks", "4-6 weeks", "8-12 weeks"],
            "answer": "4-6 weeks",
            "correctReason": "Most women need 4-6 weeks to recover from vaginal delivery.",
            "incorrectReason": "Other timeframes may not allow adequate recovery."
        },
        {
            "question": "What is the recommended frequency for newborn check-ups?",
            "options": ["Once a month", "Every 2 weeks", "As recommended by pediatrician"],
            "answer": "As recommended by pediatrician",
            "correctReason": "Check-up frequency varies based on baby's health and individual needs.",
            "incorrectReason": "A fixed schedule doesn't account for individual health requirements."
        },
        {
            "question": "When should you introduce solid foods to your baby?",
            "options": ["2-3 months", "4-6 months", "8-10 months"],
            "answer": "4-6 months",
            "correctReason": "Most babies are ready for solid foods between 4-6 months of age.",
            "incorrectReason": "Starting too early or too late can affect baby's development."
        },
        {
            "question": "What is the recommended sleep duration for newborns?",
            "options": ["8-10 hours", "12-16 hours", "18-20 hours"],
            "answer": "12-16 hours",
            "correctReason": "Newborns typically sleep 12-16 hours per day in short intervals.",
            "incorrectReason": "Other durations may indicate sleep issues or health concerns."
        },
        {
            "question": "When should you start tummy time with your baby?",
            "options": ["From birth", "After 1 month", "After 3 months"],
            "answer": "From birth",
            "correctReason": "Tummy time can start from birth for short periods to strengthen muscles.",
            "incorrectReason": "Waiting too long may delay motor development."
        },
        {
            "question": "What is the recommended frequency for changing newborn diapers?",
            "options": ["Every 2-3 hours", "Every 4-6 hours", "Only when soiled"],
            "answer": "Every 2-3 hours",
            "correctReason": "Newborns need frequent diaper changes every 2-3 hours to prevent rashes.",
            "incorrectReason": "Waiting longer may cause skin irritation and discomfort."
        },
        {
            "question": "How often should you feed a newborn baby?",
            "options": ["Every 2-3 hours", "Every 4-6 hours", "Only when crying"],
            "answer": "Every 2-3 hours",
            "correctReason": "Newborns need to be fed every 2-3 hours for proper growth and development.",
            "incorrectReason": "Waiting longer may cause dehydration and poor weight gain."
        },
        {
            "question": "What is the safest sleeping position for a newborn?",
            "options": ["On their back", "On their stomach", "On their side"],
            "answer": "On their back",
            "correctReason": "Back sleeping reduces the risk of SIDS and is the safest position.",
            "incorrectReason": "Stomach or side sleeping increases SIDS risk."
        },
        {
            "question": "When should you introduce solid foods to your baby?",
            "options": ["4-6 months", "2-3 months", "8-10 months"],
            "answer": "4-6 months",
            "correctReason": "Most babies are ready for solid foods between 4-6 months of age.",
            "incorrectReason": "Starting too early or too late may cause feeding problems."
        }
    ]
}

def get_instant_questions(stage, count=10):
    """Get instant questions from predefined pool for immediate response"""
    # COMMENTED OUT: Game now depends entirely on AI model generation
    # If AI model fails, game should fail rather than use fallback questions
    # questions = PREDEFINED_QUESTIONS.get(stage, [])
    # return questions[:count] if questions else []
    return []  # Always return empty - force AI generation

def get_hybrid_questions(stage, user_id="guest_user", difficulty_level=1, force_new=False):
    """Get a mix of instant and generated questions for better UX - OPTIMIZED FOR SPEED"""
    
    # If force_new is True, reset the session for this stage
    if force_new:
        reset_stage_questions(stage, user_id)
    
    # PRIORITY 1: Get instant questions FIRST (instant return, no API call)
    instant_questions = get_instant_questions(stage, 20)  # Get more to have options
    unseen_instant = filter_unseen_questions(stage, user_id, instant_questions)
    print(f"Debug - Instant questions available: {len(instant_questions)}, Unseen: {len(unseen_instant)}")
    
    # If we have enough instant questions, return immediately (FAST PATH)
    if len(unseen_instant) >= 10:
        final_questions = unseen_instant[:10]
        # Track questions
        for q in final_questions:
            track_session_question(stage, user_id, q.get('question', ''))
        print(f"Debug - Returning {len(final_questions)} instant questions immediately")
        return final_questions
    
    # If we have some unseen instant questions but not enough, we'll combine with AI-generated
    # This ensures we get new questions when instant pool is exhausted
    if len(unseen_instant) > 0 and len(unseen_instant) < 10:
        print(f"Debug - Only {len(unseen_instant)} unseen instant questions available, will generate AI questions for Round 2")
    
    # PRIORITY 2: Try to get cached AI questions (only if they're unseen)
    # Skip cache if force_new or if all cached questions are already seen
    cached_questions = get_cached_questions(stage, user_id, difficulty_level) if not force_new else []
    if cached_questions:
        unseen_cached = filter_unseen_questions(stage, user_id, cached_questions)
        # Only use cache if there are unseen questions
        if len(unseen_cached) > 0:
            combined = unseen_instant + unseen_cached
            if len(combined) >= 10:
                final_questions = combined[:10]
                for q in final_questions:
                    track_session_question(stage, user_id, q.get('question', ''))
                print(f"Debug - Returning {len(final_questions)} questions from cache ({len(unseen_cached)} unseen) + instant")
                return final_questions
        else:
            print(f"Debug - Cache hit but all cached questions are already seen, clearing cache and generating new questions...")
            # Clear cache for this stage/user to force new generation
            cache_key = generate_cache_key(stage, user_id, difficulty_level)
            with cache_lock:
                if cache_key in question_cache:
                    del question_cache[cache_key]
                    print(f"Debug - Cleared cache for {stage} to force new question generation")
            # Skip cache when generating new questions since all cached questions are seen
            should_skip_cache = True
    else:
        # No cached questions, can use cache normally
        should_skip_cache = False
    
    # ADAPTIVE LEARNING: Get failed questions for user/stage (prioritize weak areas)
    failed_questions = get_failed_questions_from_database(user_id, stage, max_count=5)
    print(f"Debug - Found {len(failed_questions)} failed questions for adaptive learning")
    
    # PRIORITY 3: Generate AI questions (slower, but only if needed)
    # This is especially important when instant pool is exhausted (all questions seen)
    try:
        # Generate AI questions - skip cache if all cached questions were already seen
        generated_questions = generate_questions_optimized(stage, user_id, difficulty_level, skip_cache=should_skip_cache)
        if isinstance(generated_questions, list) and len(generated_questions) > 0:
            unseen_generated = filter_unseen_questions(stage, user_id, generated_questions)
            print(f"Debug - Generated {len(generated_questions)} AI questions, {len(unseen_generated)} unseen")
            
            # ADAPTIVE LEARNING: Mix failed questions + new questions
            # Requirement: At least 5 new questions per round, prioritize failed questions
            MIN_NEW_QUESTIONS = 5
            MAX_FAILED_QUESTIONS = 5
            TOTAL_QUESTIONS = 10
            
            # Calculate how many failed questions to include (up to 5)
            num_failed_available = len(failed_questions)
            num_failed_to_include = min(num_failed_available, MAX_FAILED_QUESTIONS)
            # Ensure we have at least MIN_NEW_QUESTIONS new questions (10 - failed)
            num_new_needed = max(MIN_NEW_QUESTIONS, TOTAL_QUESTIONS - num_failed_to_include)
            # Adjust failed count if we don't have enough new questions
            if len(unseen_generated) < num_new_needed:
                num_failed_to_include = min(num_failed_to_include, TOTAL_QUESTIONS - MIN_NEW_QUESTIONS)
                num_new_needed = max(MIN_NEW_QUESTIONS, TOTAL_QUESTIONS - num_failed_to_include)
            
            # Combine failed + new questions (prioritize failed, ensure at least 5 new)
            final_questions = []
            seen_questions = set()
            
            # Add failed questions first (prioritize weak areas - adaptive learning)
            for q in failed_questions[:num_failed_to_include]:
                question_text = q.get('question', '').strip().lower()
                if question_text and question_text not in seen_questions:
                    seen_questions.add(question_text)
                    q['unique_id'] = f"{stage}_{user_id}_failed_{len(final_questions)}"
                    q['is_review'] = True  # Mark as review question
                    final_questions.append(q)
            
            # Add new questions (unseen instant + AI-generated) to ensure at least 5 new
            new_questions = unseen_instant + unseen_generated
            new_count = 0
            for q in new_questions:
                if len(final_questions) >= TOTAL_QUESTIONS:
                    break
                question_text = q.get('question', '').strip().lower()
                if question_text and question_text not in seen_questions:
                    seen_questions.add(question_text)
                    q['unique_id'] = f"{stage}_{user_id}_new_{len(final_questions)}"
                    q['is_review'] = False  # Mark as new question
                    final_questions.append(q)
                    new_count += 1
            
            # BADGE REQUIREMENT: Must always return exactly 10 questions per round
            # If we have fewer than 10 questions, generate more until we reach 10
            num_new_final = len([q for q in final_questions if not q.get('is_review', False)])
            num_failed_final = len([q for q in final_questions if q.get('is_review', False)])
            
            print(f"Debug - Initial mix: {num_failed_final} failed (review) + {num_new_final} new questions = {len(final_questions)} total")
            
            # If we don't have 10 questions yet, generate more to meet badge requirement
            if len(final_questions) < TOTAL_QUESTIONS:
                remaining_needed = TOTAL_QUESTIONS - len(final_questions)
                print(f"Debug - Need {remaining_needed} more questions to reach 10. Generating additional questions...")
                
                # Try generating more AI questions to fill the gap
                try:
                    additional_questions = generate_questions_optimized(stage, user_id, difficulty_level, skip_cache=True)
                    if isinstance(additional_questions, list) and len(additional_questions) > 0:
                        unseen_additional = filter_unseen_questions(stage, user_id, additional_questions)
                        print(f"Debug - Generated {len(additional_questions)} additional AI questions, {len(unseen_additional)} unseen")
                        
                        # Add additional new questions until we reach 10 total
                        for q in unseen_additional:
                            if len(final_questions) >= TOTAL_QUESTIONS:
                                break
                            question_text = q.get('question', '').strip().lower()
                            if question_text and question_text not in seen_questions:
                                seen_questions.add(question_text)
                                q['unique_id'] = f"{stage}_{user_id}_new_{len(final_questions)}"
                                q['is_review'] = False
                                final_questions.append(q)
                except Exception as e:
                    print(f"Debug - Failed to generate additional questions: {e}")
            
            # Final count after attempting to fill to 10
            num_new_final = len([q for q in final_questions if not q.get('is_review', False)])
            num_failed_final = len([q for q in final_questions if q.get('is_review', False)])
            
            # Ensure we have at least MIN_NEW_QUESTIONS new questions
            if num_new_final < MIN_NEW_QUESTIONS:
                print(f"Debug - WARNING: Only {num_new_final} new questions, need {MIN_NEW_QUESTIONS}. May need more generation.")
            
            # CRITICAL: Badge system requires exactly 10 questions per round
            if len(final_questions) < TOTAL_QUESTIONS:
                print(f"Debug - ERROR: Only have {len(final_questions)} questions, need {TOTAL_QUESTIONS} for badge system!")
                # This should not happen in production, but log it for debugging
            elif len(final_questions) > TOTAL_QUESTIONS:
                # Trim to exactly 10 if we somehow got more
                final_questions = final_questions[:TOTAL_QUESTIONS]
            
            print(f"Debug - Final adaptive mix: {num_failed_final} failed (review) + {num_new_final} new questions = {len(final_questions)} total")
            
            # BADGE REQUIREMENT: Return exactly 10 questions (or as many as possible if generation fails)
            if len(final_questions) > 0:
                # Track all questions that will be shown
                for q in final_questions:
                    track_session_question(stage, user_id, q.get('question', ''))
                
                return final_questions
            else:
                print(f"Debug - WARNING: No unique questions after filtering! All AI-generated questions were already seen.")
        else:
            print(f"Debug - AI generation returned empty or invalid response: {generated_questions}")
    except Exception as e:
        print(f"AI generation failed: {e}, will try fallback")
        import traceback
        traceback.print_exc()
    
    # Fallback: Return whatever unseen instant questions we have
    # If no unseen instant questions, we should have gotten AI-generated questions above
    # This fallback is only for edge cases where AI generation failed
    all_questions = unseen_instant
    print(f"Debug - Fallback: Using {len(all_questions)} unseen instant questions")
    
    if len(all_questions) < 10:
        # Get more instant questions if needed and filter them too
        additional_questions = get_instant_questions(stage, 15)
        unseen_additional = filter_unseen_questions(stage, user_id, additional_questions)
        all_questions.extend(unseen_additional)
        print(f"Debug - Added {len(unseen_additional)} additional unseen questions (from {len(additional_questions)} total)")
    
    # If we still have no unseen questions after fallback, try one more AI generation attempt
    if len(all_questions) == 0:
        print(f"Debug - WARNING: No unseen instant questions available! All questions have been seen in database.")
        print(f"Debug - Attempting one more AI generation as last resort...")
        try:
            # Skip cache in last resort to force new generation
            generated_questions = generate_questions_optimized(stage, user_id, difficulty_level, skip_cache=True)
            if isinstance(generated_questions, list) and len(generated_questions) > 0:
                # Filter again (though they should all be new if AI generated properly)
                unseen_generated = filter_unseen_questions(stage, user_id, generated_questions)
                if len(unseen_generated) > 0:
                    print(f"Debug - Got {len(unseen_generated)} AI-generated questions as last resort")
                    for q in unseen_generated[:10]:
                        track_session_question(stage, user_id, q.get('question', ''))
                    return unseen_generated[:10]
        except Exception as e:
            print(f"Debug - Final AI generation attempt also failed: {e}")
        
        # If everything fails, return empty rather than repeating questions
        print(f"Debug - ERROR: Unable to generate new questions! Returning empty list to avoid repeats.")
        return []
    
    # Remove duplicates even in fallback
    unique_questions = []
    seen_questions = set()
    
    for q in all_questions:
        question_text = q.get('question', '').strip().lower()
        if question_text and question_text not in seen_questions:
            seen_questions.add(question_text)
            q['unique_id'] = f"{stage}_{user_id}_{len(unique_questions)}"
            unique_questions.append(q)
    
    final_questions = unique_questions[:10]
    print(f"Debug - Fallback final questions: {len(final_questions)}")
    
    # Track all questions that will be shown
    for q in final_questions:
        track_session_question(stage, user_id, q.get('question', ''))
    
    return final_questions

# Performance monitoring
def get_performance_stats():
    """Get performance statistics"""
    with cache_lock:
        cache_size = len(question_cache)
        cache_hit_rate = sum(1 for entry in question_cache.values() if is_cache_valid(entry)) / max(cache_size, 1)
    
    return {
        "cache_size": cache_size,
        "cache_hit_rate": round(cache_hit_rate * 100, 2),
        "max_cache_size": CACHE_SIZE
    }

def clear_cache():
    """Clear the question cache"""
    with cache_lock:
        question_cache.clear()
    print("Question cache cleared")
