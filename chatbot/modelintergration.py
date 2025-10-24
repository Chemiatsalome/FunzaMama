from together import Together
import json
from models import db
from models.models import UserResponse, QuizQuestion

# Initialize Together AI client
together_client = Together(api_key="e3ab4476326269947afb85e9c0b0ed5fe9ae2949e27ed3a38ee4913d8f807b3e")

maternal_health_prompt_preconception_stage = """
You are an AI that generates **maternal health quizzes focused on the preconception stage (When preparing to get pregnant - Plan for a healthy pregnancy with proper nutrition, lifestyle changes, and early symptom awareness)** in JSON format.

### **Instructions:**
1. **Generate 10 multiple-choice questions** on maternal health.
2. **Each question should have three answer options** (A, B, C).
3. **Specify the correct answer** for each question.
4. **Include an explanation** for both correct and incorrect responses.
5. **Respond ONLY with a JSON array** (list of 10 questions). No extra text.

### **Expected JSON Format:**
[
    {
        "question": "Which nutrient is essential for preventing neural tube defects during pregnancy?",
        "options": ["Vitamin C", "Iron", "Folic Acid"],
        "answer": "Folic Acid",
        "correctReason": "Folic acid helps prevent birth defects in the baby's brain and spine.",
        "incorrectReason": "Other vitamins are important but do not prevent neural tube defects."
    },
    {...},  # 1 more questions in the same format
]

**IMPORTANT:**  
- **DO NOT** include explanations outside the JSON.  
- **DO NOT** add any introductory text.  
- **DO NOT** wrap JSON in markdown.  
- **Only return raw JSON output (an array of 10 questions).**
"""

maternal_health_prompt_prenatal_stage = """
You are an AI that generates **maternal health quizzes focused on the prenatal stage (Track your baby's growth with regular checkups, fetal monitoring, and birth preparation)** in JSON format.

### **Instructions:**
1. **Generate 10 multiple-choice questions** on maternal health.
2. **Each question should have three answer options** (A, B, C).
3. **Specify the correct answer** for each question.
4. **Include an explanation** for both correct and incorrect responses.
5. **Respond ONLY with a JSON array** (list of 10 questions). No extra text.

### **Expected JSON Format:**
[
    {
        "question": "Which nutrient is essential for preventing neural tube defects during pregnancy?",
        "options": ["Vitamin C", "Iron", "Folic Acid"],
        "answer": "Folic Acid",
        "correctReason": "Folic acid helps prevent birth defects in the baby's brain and spine.",
        "incorrectReason": "Other vitamins are important but do not prevent neural tube defects."
    },
    {...},  # 1 more questions in the same format
]

**IMPORTANT:**  
- **DO NOT** include explanations outside the JSON.  
- **DO NOT** add any introductory text.  
- **DO NOT** wrap JSON in markdown.  
- **Only return raw JSON output (an array of 10 questions).**
"""

maternal_health_prompt_birth_stage = """
You are an AI that generates **maternal health quizzes focused on the birth stage (Understanding labor signs, delivery options, and pain management.)** in JSON format.

### **Instructions:**
1. **Generate 10 multiple-choice questions** on maternal health.
2. **Each question should have three answer options** (A, B, C).
3. **Specify the correct answer** for each question.
4. **Include an explanation** for both correct and incorrect responses.
5. **Respond ONLY with a JSON array** (list of 10 questions). No extra text.

### **Expected JSON Format:**
[
    {
        "question": "Which nutrient is essential for preventing neural tube defects during pregnancy?",
        "options": ["Vitamin C", "Iron", "Folic Acid"],
        "answer": "Folic Acid",
        "correctReason": "Folic acid helps prevent birth defects in the baby's brain and spine.",
        "incorrectReason": "Other vitamins are important but do not prevent neural tube defects."
    },
    {...},  # 1 more questions in the same format
]

**IMPORTANT:**  
- **DO NOT** include explanations outside the JSON.  
- **DO NOT** add any introductory text.  
- **DO NOT** wrap JSON in markdown.  
- **Only return raw JSON output (an array of 10 questions).**
"""

maternal_health_prompt_postnatal_stage = """
You are an AI that generates **maternal health quizzes focused on the postnatal stage (Support recovery with newborn care, breastfeeding guidance, and maternal well-being.)** in JSON format.

### **Instructions:**
1. **Generate 10 multiple-choice questions** on maternal health.
2. **Each question should have three answer options** (A, B, C).
3. **Specify the correct answer** for each question.
4. **Include an explanation** for both correct and incorrect responses.
5. **Respond ONLY with a JSON array** (list of 10 questions). No extra text.

### **Expected JSON Format:**
[
    {
        "question": "Which nutrient is essential for preventing neural tube defects during pregnancy?",
        "options": ["Vitamin C", "Iron", "Folic Acid"],
        "answer": "Folic Acid",
        "correctReason": "Folic acid helps prevent birth defects in the baby's brain and spine.",
        "incorrectReason": "Other vitamins are important but do not prevent neural tube defects."
    },
    {...},  # 1 more questions in the same format
]

**IMPORTANT:**  
- **DO NOT** include explanations outside the JSON.  
- **DO NOT** add any introductory text.  
- **DO NOT** wrap JSON in markdown.  
- **Only return raw JSON output (an array of 10 questions).**
"""

def get_chatbot_response_preconception(user_id):
    """Fetch AI-generated quiz questions for the prenatal stage (Plan for a healthy pregnancy with proper nutrition, lifestyle changes, and early symptom awareness.) """
    try:
        # Step 1: Generate new quiz questions using the AI model
        response = together_client.chat.completions.create(
            model="meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
            messages=[
                {"role": "system", "content": maternal_health_prompt_preconception_stage},
                {"role": "user", "content": "Generate 10 quiz questions on maternal health."}
            ],
            max_tokens=2000,
            temperature=0.3,
            top_p=0.9,
            top_k=40,
            repetition_penalty=1.1,
            stop=["\n\n"],
        )

        # Step 2: Parse the response
        response_text = response.choices[0].message.content.strip()
        # print("Raw AI Response:", response_text)  # For debugging

        # Try to parse the response as JSON
        if response_text.startswith("[") and response_text.endswith("]"):
            new_questions = json.loads(response_text)
        elif response_text.startswith("[") and not response_text.endswith("]"):
            response_text += "]"
            new_questions = json.loads(response_text)
        else:
            return {"error": "Response is not a valid JSON array"}

        return new_questions

    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}


def get_chatbot_response_prenatal(user_id):
    """Fetch AI-generated quiz questions for the prenatal stage (Track your baby's growth with regular checkups, fetal monitoring, and birth preparation.) """
    try:
        # Step 1: Generate new quiz questions using the AI model
        response = together_client.chat.completions.create(
            model="meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
            messages=[
                {"role": "system", "content": maternal_health_prompt_prenatal_stage},
                {"role": "user", "content": "Generate 10 quiz questions on maternal health."}
            ],
            max_tokens=2000,
            temperature=0.3,
            top_p=0.9,
            top_k=40,
            repetition_penalty=1.1,
            stop=["\n\n"],
        )

        # Step 2: Parse the response
        response_text = response.choices[0].message.content.strip()
        # print("Raw AI Response:", response_text)  # For debugging

        # Try to parse the response as JSON
        if response_text.startswith("[") and response_text.endswith("]"):
            new_questions = json.loads(response_text)
        elif response_text.startswith("[") and not response_text.endswith("]"):
            response_text += "]"
            new_questions = json.loads(response_text)
        else:
            return {"error": "Response is not a valid JSON array"}

        return new_questions

    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}

def get_chatbot_response_birth(user_id):
    """Fetch AI-generated quiz questions for the birth (Understanding labor signs, delivery options, and pain management.) stage without repeating already answered questions. """
    try:
        # Step 1: Generate new quiz questions using the AI model
        response = together_client.chat.completions.create(
            model="meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
            messages=[
                {"role": "system", "content": maternal_health_prompt_birth_stage},
                {"role": "user", "content": "Generate 10 quiz questions on maternal health."}
            ],
            max_tokens=2000,
            temperature=0.3,
            top_p=0.9,
            top_k=40,
            repetition_penalty=1.1,
            stop=["\n\n"],
        )

        # Step 2: Parse the response
        response_text = response.choices[0].message.content.strip()
        # print("Raw AI Response:", response_text)  # For debugging

        # Try to parse the response as JSON
        if response_text.startswith("[") and response_text.endswith("]"):
            new_questions = json.loads(response_text)
        elif response_text.startswith("[") and not response_text.endswith("]"):
            response_text += "]"
            new_questions = json.loads(response_text)
        else:
            return {"error": "Response is not a valid JSON array"}

        return new_questions

    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}

def get_chatbot_response_postnatal(user_id):
    """Fetch AI-generated quiz questions for the postnatal stage (Support recovery with newborn care, breastfeeding guidance, and maternal well-being.) """
    try:
        # Step 1: Generate new quiz questions using the AI model
        response = together_client.chat.completions.create(
            model="meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
            messages=[
                {"role": "system", "content": maternal_health_prompt_postnatal_stage},
                {"role": "user", "content": "Generate 10 quiz questions on maternal health."}
            ],
            max_tokens=2000,
            temperature=0.3,
            top_p=0.9,
            top_k=40,
            repetition_penalty=1.1,
            stop=["\n\n"],
        )

        # Step 2: Parse the response
        response_text = response.choices[0].message.content.strip()
        # print("Raw AI Response:", response_text)  # For debugging

        # Try to parse the response as JSON
        if response_text.startswith("[") and response_text.endswith("]"):
            new_questions = json.loads(response_text)
        elif response_text.startswith("[") and not response_text.endswith("]"):
            response_text += "]"
            new_questions = json.loads(response_text)
        else:
            return {"error": "Response is not a valid JSON array"}

        return new_questions

    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}  



def get_teaching_facts_by_stage(stage_name):
    """Uses the Together AI LLaMA model to generate teaching content for a given maternal health stage."""
    try:
        # Define prompts per stage
        prompts = {
    "prenatal": (
        "You're an expert in maternal health. Provide exactly 3 numbered teaching concepts "
        "about the importance of prenatal care. Make them short, clear, and suitable for a quiz-based educational game. "
        "Respond only with the list."
    ),
    "preconception": (
        "You're a maternal health educator. Provide exactly 3 numbered teaching concepts "
        "on preconception care. Focus on the importance of planning for pregnancy. Respond only with the list."
    ),
    "birth": (
        "You're a maternal health expert. Provide exactly 3 numbered teaching points about labor and delivery. "
        "Make them simple and clear for game-based education. Respond only with the list."
    ),
    "postnatal": (
        "You're a maternal health advisor. Provide exactly 3 numbered learning suggestions for the postnatal stage. "
        "Focus on maternal recovery, breastfeeding, and newborn care. Respond only with the list."
    )
}


        # Normalize stage key
        stage_key = stage_name.lower()
        if stage_key not in prompts:
            return ["No educational content available for this stage."]

        # Call Together API
        response = together_client.chat.completions.create(
            model="meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
            messages=[
                {"role": "system", "content": prompts[stage_key]},
                {"role": "user", "content": f"Teach me about {stage_key} care."}
            ],
            max_tokens=400,
            temperature=0.3,
            top_p=1,
            top_k=50,
            repetition_penalty=1.1,
            stop=["\n\n"],
        )

        # Parse response
        response_text = response.choices[0].message.content.strip()
        facts = response_text.split("\n")
        facts = [fact.strip("1234567890.:- ") for fact in facts if fact.strip()]
        return facts

    except Exception as e:
        return [f"Error generating content: {str(e)}"]
