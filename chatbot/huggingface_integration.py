"""
Hugging Face Local Model Integration for Funza Mama
Free alternative to Together API using local Llama 3.2-1B model
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import json
import os
from typing import List, Dict, Any, Optional
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HuggingFaceLocalModel:
    def __init__(self, model_name: str = "meta-llama/Llama-3.2-1B"):
        """
        Initialize Hugging Face local model
        
        Args:
            model_name: Hugging Face model identifier
        """
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        
        logger.info(f"Using device: {self.device}")
        self._load_model()
    
    def _load_model(self):
        """Load the model and tokenizer"""
        try:
            logger.info(f"Loading model: {self.model_name}")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True
            )
            
            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None,
                trust_remote_code=True
            )
            
            # Create pipeline for easier text generation
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if self.device == "cuda" else -1,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            )
            
            logger.info("Model loaded successfully!")
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    def generate_quiz_questions(self, stage: str, user_id: str = None) -> Dict[str, Any]:
        """
        Generate quiz questions for a specific maternal health stage
        
        Args:
            stage: The maternal health stage (preconception, prenatal, birth, postnatal)
            user_id: Optional user ID for tracking
            
        Returns:
            Dictionary containing generated questions or error
        """
        try:
            # Define stage-specific prompts
            prompts = {
                "preconception": """
You are an AI that generates maternal health quizzes focused on the preconception stage (When preparing to get pregnant - Plan for a healthy pregnancy with proper nutrition, lifestyle changes, and early symptom awareness) in JSON format.

Generate 10 multiple-choice questions on maternal health. Each question should have three answer options (A, B, C). Specify the correct answer and include explanations.

Respond ONLY with a JSON array of 10 questions in this format:
[
    {
        "question": "Which nutrient is essential for preventing neural tube defects during pregnancy?",
        "options": ["Vitamin C", "Iron", "Folic Acid"],
        "answer": "Folic Acid",
        "correctReason": "Folic acid helps prevent birth defects in the baby's brain and spine.",
        "incorrectReason": "Other vitamins are important but do not prevent neural tube defects."
    }
]

Respond ONLY with raw JSON array.
""",
                "prenatal": """
You are an AI that generates maternal health quizzes focused on the prenatal stage (Track your baby's growth with regular checkups, fetal monitoring, and birth preparation) in JSON format.

Generate 10 multiple-choice questions on maternal health. Each question should have three answer options (A, B, C). Specify the correct answer and include explanations.

Respond ONLY with a JSON array of 10 questions in this format:
[
    {
        "question": "Which nutrient is essential for preventing neural tube defects during pregnancy?",
        "options": ["Vitamin C", "Iron", "Folic Acid"],
        "answer": "Folic Acid",
        "correctReason": "Folic acid helps prevent birth defects in the baby's brain and spine.",
        "incorrectReason": "Other vitamins are important but do not prevent neural tube defects."
    }
]

Respond ONLY with raw JSON array.
""",
                "birth": """
You are an AI that generates maternal health quizzes focused on the birth stage (Understanding labor signs, delivery options, and pain management) in JSON format.

Generate 10 multiple-choice questions on maternal health. Each question should have three answer options (A, B, C). Specify the correct answer and include explanations.

Respond ONLY with a JSON array of 10 questions in this format:
[
    {
        "question": "Which nutrient is essential for preventing neural tube defects during pregnancy?",
        "options": ["Vitamin C", "Iron", "Folic Acid"],
        "answer": "Folic Acid",
        "correctReason": "Folic acid helps prevent birth defects in the baby's brain and spine.",
        "incorrectReason": "Other vitamins are important but do not prevent neural tube defects."
    }
]

Respond ONLY with raw JSON array.
""",
                "postnatal": """
You are an AI that generates maternal health quizzes focused on the postnatal stage (Support recovery with newborn care, breastfeeding guidance, and maternal well-being) in JSON format.

Generate 10 multiple-choice questions on maternal health. Each question should have three answer options (A, B, C). Specify the correct answer and include explanations.

Respond ONLY with a JSON array of 10 questions in this format:
[
    {
        "question": "Which nutrient is essential for preventing neural tube defects during pregnancy?",
        "options": ["Vitamin C", "Iron", "Folic Acid"],
        "answer": "Folic Acid",
        "correctReason": "Folic acid helps prevent birth defects in the baby's brain and spine.",
        "incorrectReason": "Other vitamins are important but do not prevent neural tube defects."
    }
]

Respond ONLY with raw JSON array.
"""
            }
            
            if stage not in prompts:
                return {"error": f"Unknown stage: {stage}"}
            
            # Generate response using the pipeline
            prompt = prompts[stage]
            
            response = self.pipeline(
                prompt,
                max_new_tokens=2000,
                temperature=0.3,
                top_p=0.9,
                top_k=40,
                repetition_penalty=1.1,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            # Extract generated text
            generated_text = response[0]['generated_text']
            
            # Extract only the new generated content (after the prompt)
            if prompt in generated_text:
                new_content = generated_text[len(prompt):].strip()
            else:
                new_content = generated_text.strip()
            
            # Try to parse as JSON
            try:
                # Clean up the response to extract JSON
                if new_content.startswith('[') and new_content.endswith(']'):
                    questions = json.loads(new_content)
                elif '[' in new_content and ']' in new_content:
                    # Extract JSON from the response
                    start_idx = new_content.find('[')
                    end_idx = new_content.rfind(']') + 1
                    json_str = new_content[start_idx:end_idx]
                    questions = json.loads(json_str)
                else:
                    return {"error": "Response is not a valid JSON array"}
                
                return questions
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                logger.error(f"Generated content: {new_content}")
                return {"error": f"Failed to parse JSON response: {str(e)}"}
                
        except Exception as e:
            logger.error(f"Error generating questions: {e}")
            return {"error": f"An error occurred: {str(e)}"}
    
    def generate_teaching_facts(self, stage: str) -> List[str]:
        """
        Generate teaching facts for a specific stage
        
        Args:
            stage: The maternal health stage
            
        Returns:
            List of teaching facts
        """
        try:
            stage_prompts = {
                "prenatal": "You're an expert in maternal health. Provide exactly 3 numbered teaching concepts about the importance of prenatal care. Make them short, clear, and suitable for a quiz-based educational game. Respond only with the list.",
                "preconception": "You're a maternal health educator. Provide exactly 3 numbered teaching concepts on preconception care. Focus on the importance of planning for pregnancy. Respond only with the list.",
                "birth": "You're a maternal health expert. Provide exactly 3 numbered teaching points about labor and delivery. Make them simple and clear for game-based education. Respond only with the list.",
                "postnatal": "You're a maternal health advisor. Provide exactly 3 numbered learning suggestions for the postnatal stage. Focus on maternal recovery, breastfeeding, and newborn care. Respond only with the list."
            }
            
            if stage not in stage_prompts:
                return [f"No educational content available for stage: {stage}"]
            
            prompt = stage_prompts[stage]
            
            response = self.pipeline(
                prompt,
                max_new_tokens=400,
                temperature=0.3,
                top_p=1.0,
                top_k=50,
                repetition_penalty=1.1,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            generated_text = response[0]['generated_text']
            
            # Extract new content
            if prompt in generated_text:
                new_content = generated_text[len(prompt):].strip()
            else:
                new_content = generated_text.strip()
            
            # Parse facts
            facts = new_content.split('\n')
            facts = [fact.strip('1234567890.:- ') for fact in facts if fact.strip()]
            
            return facts if facts else [f"Error generating content for {stage}"]
            
        except Exception as e:
            logger.error(f"Error generating teaching facts: {e}")
            return [f"Error generating content: {str(e)}"]

# Global model instance
_hf_model = None

def get_hf_model() -> HuggingFaceLocalModel:
    """Get or create the global Hugging Face model instance"""
    global _hf_model
    if _hf_model is None:
        _hf_model = HuggingFaceLocalModel()
    return _hf_model

# Convenience functions that match your existing API
def get_chatbot_response_preconception(user_id):
    """Fetch AI-generated quiz questions for the preconception stage using Hugging Face"""
    model = get_hf_model()
    return model.generate_quiz_questions("preconception", user_id)

def get_chatbot_response_prenatal(user_id):
    """Fetch AI-generated quiz questions for the prenatal stage using Hugging Face"""
    model = get_hf_model()
    return model.generate_quiz_questions("prenatal", user_id)

def get_chatbot_response_birth(user_id):
    """Fetch AI-generated quiz questions for the birth stage using Hugging Face"""
    model = get_hf_model()
    return model.generate_quiz_questions("birth", user_id)

def get_chatbot_response_postnatal(user_id):
    """Fetch AI-generated quiz questions for the postnatal stage using Hugging Face"""
    model = get_hf_model()
    return model.generate_quiz_questions("postnatal", user_id)

def get_teaching_facts_by_stage(stage_name):
    """Generate teaching content for a given maternal health stage using Hugging Face"""
    model = get_hf_model()
    return model.generate_teaching_facts(stage_name)

