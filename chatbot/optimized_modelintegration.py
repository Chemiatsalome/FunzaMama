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
from models import db
from models.models import UserResponse, QuizQuestion

# Initialize Together AI client
together_client = Together(api_key="e3ab4476326269947afb85e9c0b0ed5fe9ae2949e27ed3a38ee4913d8f807b3e")

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
    "preconception": """Generate 10 completely unique and diverse maternal health quiz questions for preconception care. Each question must be different from the others. Cover: folic acid timing/dosage, pre-pregnancy checkups, lifestyle changes, genetic counseling, fertility awareness, vaccinations, chronic disease management. Each question should have 3 specific, realistic options (NOT generic A, B, C), correct answer, and explanations. Return ONLY valid JSON array format:
[{"question": "...", "options": ["...", "...", "..."], "answer": "...", "correctReason": "...", "incorrectReason": "..."}]""",
    
    "prenatal": """Generate exactly 10 completely unique and diverse maternal health quiz questions for prenatal care. Each question must be different from the others. Cover: trimester-specific nutrition, safe exercise, prenatal visits, warning signs, weight gain, discomforts, screening tests, complications. Each question must have 3 specific, realistic options (NOT generic A, B, C), correct answer, and explanations. Return ONLY valid JSON array:
[{"question": "What is the recommended daily calorie increase during pregnancy?", "options": ["300-500 extra calories", "500-700 extra calories", "No increase needed"], "answer": "300-500 extra calories", "correctReason": "Most women need 300-500 extra calories per day during pregnancy.", "incorrectReason": "Other amounts are not typically recommended for healthy pregnancies."}]""",
    
    "birth": """Generate 10 completely unique and diverse maternal health quiz questions for birth and delivery. Each question must be different from the others. Cover: labor stages, pain management, delivery positions, medical interventions, emergencies, postpartum recovery, newborn care, breastfeeding initiation. Each question should have 3 specific, realistic options (NOT generic A, B, C), correct answer, and explanations. Return ONLY valid JSON array format:
[{"question": "...", "options": ["...", "...", "..."], "answer": "...", "correctReason": "...", "incorrectReason": "..."}]""",
    
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

def filter_unseen_questions(stage, user_id, questions):
    """Filter out questions that have been seen in the current session"""
    unseen_questions = []
    for q in questions:
        question_text = q.get('question', '').strip()
        if question_text and not is_question_seen_in_session(stage, user_id, question_text):
            unseen_questions.append(q)
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

def generate_questions_optimized(stage, user_id="guest_user", difficulty_level=1):
    """Optimized question generation with caching and faster AI parameters"""
    
    # Check cache first
    cached_questions = get_cached_questions(stage, user_id, difficulty_level)
    if cached_questions:
        return cached_questions
    
    print(f"Generating new questions for {stage}...")
    start_time = time.time()
    
    try:
        # Use optimized AI parameters for speed
        response = together_client.chat.completions.create(
            model="meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
            messages=[
                {"role": "system", "content": OPTIMIZED_PROMPTS[stage]},
                {"role": "user", "content": f"Generate 10 {stage} quiz questions."}
            ],
            max_tokens=1000,  # Further reduced for speed
            temperature=0.1,  # Lower for more focused responses
            top_p=0.7,        # Further reduced for faster generation
            top_k=15,         # Further reduced for speed
            repetition_penalty=1.02,  # Further reduced
            stop=["\n\n", "```"],  # Better stopping conditions
        )
        
        # Parse response
        response_text = response.choices[0].message.content.strip()
        
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
            # Look for JSON objects in the text
            json_objects = re.findall(r'\{[^{}]*"question"[^{}]*\}', response_text)
            if json_objects:
                response_text = '[' + ','.join(json_objects) + ']'
            else:
                # If no JSON found, return empty list
                print("No valid JSON found in response")
                questions = []
                return questions
        
        try:
            questions = json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Response text: {response_text[:200]}...")
            # Return empty list if JSON parsing fails
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
    questions = PREDEFINED_QUESTIONS.get(stage, [])
    return questions[:count] if questions else []

def get_hybrid_questions(stage, user_id="guest_user", difficulty_level=1, force_new=False):
    """Get a mix of instant and generated questions for better UX"""
    
    # If force_new is True, reset the session for this stage
    if force_new:
        reset_stage_questions(stage, user_id)
    
    # Get instant questions and filter out seen ones
    instant_questions = get_instant_questions(stage, 15)  # Get more to have options
    unseen_instant = filter_unseen_questions(stage, user_id, instant_questions)
    print(f"Debug - Instant questions available: {len(instant_questions)}, Unseen: {len(unseen_instant)}")
    
    # Generate AI questions and filter out seen ones
    try:
        generated_questions = generate_questions_optimized(stage, user_id, difficulty_level)
        if isinstance(generated_questions, list) and len(generated_questions) > 0:
            unseen_generated = filter_unseen_questions(stage, user_id, generated_questions)
            
            # Combine and remove duplicates by question text
            all_questions = unseen_instant + unseen_generated
            unique_questions = []
            seen_questions = set()
            
            for q in all_questions:
                question_text = q.get('question', '').strip().lower()
                if question_text and question_text not in seen_questions:
                    seen_questions.add(question_text)
                    # Add unique ID for better tracking
                    q['unique_id'] = f"{stage}_{user_id}_{len(unique_questions)}"
                    unique_questions.append(q)
            
            # Return up to 10 unique questions
            final_questions = unique_questions[:10]
            print(f"Debug - Final questions generated: {len(final_questions)}")
            
            # Track all questions that will be shown
            for q in final_questions:
                track_session_question(stage, user_id, q.get('question', ''))
            
            return final_questions
    except Exception as e:
        print(f"Background generation failed: {e}")
    
    # Fallback to instant questions if generation fails
    all_questions = unseen_instant
    print(f"Debug - Fallback: Using {len(all_questions)} unseen instant questions")
    if len(all_questions) < 10:
        # If we don't have enough unseen instant questions, get more
        additional_questions = get_instant_questions(stage, 15)
        all_questions.extend(additional_questions)
        print(f"Debug - Added {len(additional_questions)} additional questions")
    
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
