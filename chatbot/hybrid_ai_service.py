"""
Hybrid AI Service for Funza Mama
Supports both Together API and Hugging Face local models with automatic fallback
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from enum import Enum

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIProvider(Enum):
    TOGETHER = "together"
    HUGGINGFACE = "huggingface"
    FALLBACK = "fallback"

class HybridAIService:
    def __init__(self, preferred_provider: str = "huggingface"):
        """
        Initialize hybrid AI service
        
        Args:
            preferred_provider: "together", "huggingface", or "auto"
        """
        self.preferred_provider = preferred_provider
        self.together_available = False
        self.hf_available = False
        self.hf_model = None  # Lazy-loaded, not initialized here
        
        # Initialize providers (only Together, HF is lazy-loaded)
        self._setup_together()
        # NOTE: Hugging Face is NOT initialized here to avoid 3-minute delay
        # It will be loaded only when needed (when Together API fails)
        
        logger.info(f"Hybrid AI Service initialized. Together: {self.together_available}, HF: Lazy-loaded")
    
    def _setup_together(self):
        """Setup Together API client"""
        try:
            from together import Together
            together_key = os.getenv('TOGETHER_API_KEY', 'e3ab4476326269947afb85e9c0b0ed5fe9ae2949e27ed3a38ee4913d8f807b3e')
            self.together_client = Together(api_key=together_key)
            self.together_available = True
            logger.info("✅ Together API configured")
        except Exception as e:
            logger.warning(f"❌ Together API not available: {e}")
            self.together_available = False
    
    def _setup_huggingface(self):
        """Lazy-load Hugging Face local model (only when needed)"""
        # Skip if already loaded or marked as unavailable
        if self.hf_model is not None:
            return True
        if hasattr(self, '_hf_load_failed') and self._hf_load_failed:
            return False
        
        try:
            logger.info("Loading Hugging Face model (this may take a few minutes on first use)...")
            from .huggingface_integration import get_hf_model
            self.hf_model = get_hf_model()
            self.hf_available = True
            logger.info("✅ Hugging Face local model loaded")
            return True
        except Exception as e:
            logger.warning(f"❌ Hugging Face model not available: {e}")
            self.hf_available = False
            self._hf_load_failed = True
            return False
    
    def _get_provider_priority(self) -> List[AIProvider]:
        """Get provider priority based on preference"""
        # CORRECT ORDER: Together API (main) -> Hugging Face (fallback) -> Fallback responses (last resort)
        if self.preferred_provider == "together":
            return [AIProvider.TOGETHER, AIProvider.HUGGINGFACE, AIProvider.FALLBACK]
        elif self.preferred_provider == "huggingface":
            return [AIProvider.TOGETHER, AIProvider.HUGGINGFACE, AIProvider.FALLBACK]  # Still Together first for reliability
        else:  # auto
            # Together API first (most reliable), then HF for cost savings, then fallback
            return [AIProvider.TOGETHER, AIProvider.HUGGINGFACE, AIProvider.FALLBACK]
    
    def generate_quiz_questions(self, stage: str, user_id: str = None) -> Dict[str, Any]:
        """
        Generate quiz questions with automatic provider fallback
        
        Args:
            stage: Maternal health stage
            user_id: Optional user ID
            
        Returns:
            Generated questions or error
        """
        providers = self._get_provider_priority()
        
        for provider in providers:
            try:
                if provider == AIProvider.TOGETHER and self.together_available:
                    return self._generate_with_together(stage, user_id)
                elif provider == AIProvider.HUGGINGFACE:
                    # Lazy-load Hugging Face only when Together API fails
                    if self._setup_huggingface() and self.hf_available:
                    return self._generate_with_huggingface(stage, user_id)
                    else:
                        # Skip to next provider if HF load failed
                        continue
                elif provider == AIProvider.FALLBACK:
                    return self._generate_fallback_questions(stage)
            except Exception as e:
                logger.warning(f"Provider {provider.value} failed: {e}")
                continue
        
        return {"error": "All AI providers failed"}
    
    def _generate_with_together(self, stage: str, user_id: str) -> Dict[str, Any]:
        """Generate questions using Together API"""
        try:
            # Import the existing Together integration
            from .modelintergration import (
                get_chatbot_response_preconception,
                get_chatbot_response_prenatal,
                get_chatbot_response_birth,
                get_chatbot_response_postnatal
            )
            
            stage_functions = {
                "preconception": get_chatbot_response_preconception,
                "prenatal": get_chatbot_response_prenatal,
                "birth": get_chatbot_response_birth,
                "postnatal": get_chatbot_response_postnatal
            }
            
            if stage not in stage_functions:
                return {"error": f"Unknown stage: {stage}"}
            
            return stage_functions[stage](user_id)
            
        except Exception as e:
            logger.error(f"Together API error: {e}")
            raise
    
    def _generate_with_huggingface(self, stage: str, user_id: str) -> Dict[str, Any]:
        """Generate questions using Hugging Face local model"""
        try:
            return self.hf_model.generate_quiz_questions(stage, user_id)
        except Exception as e:
            logger.error(f"Hugging Face error: {e}")
            raise
    
    def _generate_fallback_questions(self, stage: str) -> Dict[str, Any]:
        """Generate fallback questions when AI providers fail"""
        fallback_questions = {
            "preconception": [
                {
                    "question": "What is the recommended daily intake of folic acid before pregnancy?",
                    "options": ["400 mcg", "200 mcg", "600 mcg"],
                    "answer": "400 mcg",
                    "correctReason": "400 mcg of folic acid daily helps prevent neural tube defects.",
                    "incorrectReason": "Other amounts are not the recommended daily intake."
                }
            ],
            "prenatal": [
                {
                    "question": "How often should pregnant women have prenatal checkups?",
                    "options": ["Monthly", "Every 2 weeks", "Weekly"],
                    "answer": "Monthly",
                    "correctReason": "Monthly checkups are standard for healthy pregnancies.",
                    "incorrectReason": "More frequent visits are only needed for high-risk pregnancies."
                }
            ],
            "birth": [
                {
                    "question": "What is the first stage of labor?",
                    "options": ["Pushing", "Contractions", "Delivery"],
                    "answer": "Contractions",
                    "correctReason": "Contractions mark the beginning of labor.",
                    "incorrectReason": "Pushing and delivery come later in the process."
                }
            ],
            "postnatal": [
                {
                    "question": "When should breastfeeding typically begin?",
                    "options": ["Within 1 hour", "After 24 hours", "When baby is ready"],
                    "answer": "Within 1 hour",
                    "correctReason": "Early breastfeeding helps establish milk supply and bonding.",
                    "incorrectReason": "Delaying breastfeeding can affect milk production."
                }
            ]
        }
        
        return fallback_questions.get(stage, [{"error": "No fallback questions available"}])
    
    def generate_teaching_facts(self, stage: str) -> List[str]:
        """
        Generate teaching facts with automatic provider fallback
        
        Args:
            stage: Maternal health stage
            
        Returns:
            List of teaching facts
        """
        providers = self._get_provider_priority()
        
        for provider in providers:
            try:
                if provider == AIProvider.TOGETHER and self.together_available:
                    from .modelintergration import get_teaching_facts_by_stage
                    return get_teaching_facts_by_stage(stage)
                elif provider == AIProvider.HUGGINGFACE:
                    # Lazy-load Hugging Face only when Together API fails
                    if self._setup_huggingface() and self.hf_available:
                    return self.hf_model.generate_teaching_facts(stage)
                    else:
                        continue
                elif provider == AIProvider.FALLBACK:
                    return self._get_fallback_facts(stage)
            except Exception as e:
                logger.warning(f"Provider {provider.value} failed for teaching facts: {e}")
                continue
        
        return [f"Error generating teaching facts for {stage}"]
    
    def generate_chat_response(self, message: str, stage: str = "general", context: Dict[str, Any] = None) -> str:
        """
        Generate chat response with automatic provider fallback
        
        Args:
            message: User's message
            stage: Maternal health stage
            context: Additional context (current question, options, etc.)
            
        Returns:
            Chat response string
        """
        providers = self._get_provider_priority()
        
        for provider in providers:
            try:
                if provider == AIProvider.TOGETHER and self.together_available:
                    return self._generate_chat_with_together(message, stage, context)
                elif provider == AIProvider.HUGGINGFACE:
                    # Lazy-load Hugging Face only when Together API fails
                    if self._setup_huggingface() and self.hf_available:
                    return self._generate_chat_with_huggingface(message, stage, context)
                    else:
                        continue
                elif provider == AIProvider.FALLBACK:
                    return self._generate_fallback_chat_response(message, stage, context)
            except Exception as e:
                logger.warning(f"Provider {provider.value} failed for chat: {e}")
                continue
        
        return f"Sorry, I'm having trouble responding right now. Please try again later."
    
    def _generate_chat_with_together(self, message: str, stage: str, context: Dict[str, Any]) -> str:
        """Generate chat response using Together API"""
        try:
            from .chatbot import get_chatbot_response
            
            # Use existing Together API chatbot
            current_question = context.get('current_question', '') if context else ''
            current_options = context.get('current_options', []) if context else []
            current_answer = context.get('current_answer', '') if context else ''
            
            return get_chatbot_response(message, 'English', 'Curious Learner', current_question, current_options, current_answer)
            
        except Exception as e:
            logger.error(f"Together API chat error: {e}")
            raise
    
    def _generate_chat_with_huggingface(self, message: str, stage: str, context: Dict[str, Any]) -> str:
        """Generate chat response using Hugging Face local model"""
        try:
            # Create a simple prompt for chat
            prompt = f"""You are Funza Mama, a helpful AI assistant for maternal health education. 
            
Stage: {stage}
User message: {message}

Please provide a helpful, supportive response about maternal health. Keep it concise and encouraging."""

            response = self.hf_model.pipeline(
                prompt,
                max_new_tokens=200,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=self.hf_model.tokenizer.eos_token_id
            )
            
            generated_text = response[0]['generated_text']
            
            # Extract only the new generated content
            if prompt in generated_text:
                new_content = generated_text[len(prompt):].strip()
            else:
                new_content = generated_text.strip()
            
            return new_content if new_content else "I'm here to help with your maternal health questions. What would you like to know?"
            
        except Exception as e:
            logger.error(f"Hugging Face chat error: {e}")
            raise
    
    def _generate_fallback_chat_response(self, message: str, stage: str, context: Dict[str, Any]) -> str:
        """Generate fallback chat response with context support for failed questions"""
        
        # Check if this is about a failed question (has context)
        current_question = context.get('current_question', '') if context else ''
        current_answer = context.get('current_answer', '') if context else ''
        current_options = context.get('current_options', []) if context else []
        
        # If user is asking about a failed question, provide helpful explanation
        if current_question and current_answer:
            response = f"I can help you understand '{current_question}'!\n\n"
            response += f"**The correct answer is: {current_answer}**\n\n"
            
            # Provide context-specific help
            question_lower = current_question.lower()
            if any(word in question_lower for word in ['nutrition', 'diet', 'food', 'vitamin', 'supplement']):
                response += "**Key points about nutrition:**\n"
                response += "• Eat a balanced diet with fruits, vegetables, whole grains, and lean proteins\n"
                response += "• Take prenatal vitamins as recommended by your healthcare provider\n"
                response += "• Stay hydrated by drinking plenty of water\n"
                response += "• Avoid certain foods like raw fish, unpasteurized dairy, and excessive caffeine\n\n"
            elif any(word in question_lower for word in ['exercise', 'activity', 'workout', 'fitness']):
                response += "**Key points about exercise:**\n"
                response += "• Regular moderate exercise is generally safe and beneficial during pregnancy\n"
                response += "• Activities like walking, swimming, and prenatal yoga are excellent choices\n"
                response += "• Listen to your body and stop if you feel pain or discomfort\n"
                response += "• Consult your healthcare provider before starting any new exercise routine\n\n"
            elif any(word in question_lower for word in ['prenatal', 'visit', 'checkup', 'appointment']):
                response += "**Key points about prenatal care:**\n"
                response += "• Regular prenatal visits are essential for monitoring your health and baby's development\n"
                response += "• These visits allow your healthcare provider to detect and address any issues early\n"
                response += "• Bring questions and concerns to each appointment\n"
                response += "• Follow your healthcare provider's recommendations for tests and screenings\n\n"
            elif any(word in question_lower for word in ['labor', 'birth', 'delivery', 'contraction']):
                response += "**Key points about labor and birth:**\n"
                response += "• Know the signs of labor: regular contractions, water breaking, or bloody show\n"
                response += "• Create a birth plan but remain flexible\n"
                response += "• Have a support person ready to accompany you\n"
                response += "• Trust your healthcare team during delivery\n\n"
            else:
                response += "**General guidance:**\n"
                response += "• Always consult your healthcare provider for personalized medical advice\n"
                response += "• Trust reliable sources for maternal health information\n"
                response += "• Every pregnancy is unique - what works for others may not work for you\n"
                response += "• Don't hesitate to ask questions - knowledge empowers you\n\n"
            
            response += "Would you like me to explain any specific aspect of this topic in more detail?"
            return response
        
        # Default stage-specific responses
        stage_responses = {
            "preconception": "I can help with preconception planning, nutrition, and preparing for a healthy pregnancy.",
            "prenatal": "I can assist with prenatal care, nutrition, exercise, and monitoring your pregnancy.",
            "birth": "I can provide guidance on labor signs, delivery options, and pain management.",
            "postnatal": "I can help with postpartum recovery, newborn care, and breastfeeding support.",
            "general": "I'm here to help with all aspects of maternal health. What would you like to know?"
        }
        
        base_response = stage_responses.get(stage, stage_responses["general"])
        
        return f"{base_response} For specific medical concerns, always consult your healthcare provider."
    
    def _get_fallback_facts(self, stage: str) -> List[str]:
        """Get fallback teaching facts"""
        fallback_facts = {
            "preconception": [
                "Start taking folic acid supplements before pregnancy",
                "Maintain a healthy weight and lifestyle",
                "Schedule a preconception checkup with your doctor"
            ],
            "prenatal": [
                "Attend all scheduled prenatal appointments",
                "Eat a balanced diet with prenatal vitamins",
                "Avoid alcohol, smoking, and harmful substances"
            ],
            "birth": [
                "Learn about different labor positions and breathing techniques",
                "Create a birth plan and discuss it with your healthcare provider",
                "Pack a hospital bag with essentials for you and baby"
            ],
            "postnatal": [
                "Focus on recovery and getting adequate rest",
                "Establish a breastfeeding routine if you choose to breastfeed",
                "Watch for signs of postpartum depression and seek help if needed"
            ]
        }
        
        return fallback_facts.get(stage, [f"No teaching facts available for {stage}"])
    
    def get_provider_status(self) -> Dict[str, bool]:
        """Get status of all providers"""
        return {
            "together": self.together_available,
            "huggingface": self.hf_available,
            "preferred": self.preferred_provider
        }

# Global service instance
_hybrid_service = None

def get_hybrid_service(preferred_provider: str = "huggingface") -> HybridAIService:
    """Get or create the global hybrid AI service"""
    global _hybrid_service
    if _hybrid_service is None:
        _hybrid_service = HybridAIService(preferred_provider)
    return _hybrid_service

# Convenience functions that match your existing API
def get_chatbot_response_preconception(user_id):
    """Fetch AI-generated quiz questions for the preconception stage"""
    service = get_hybrid_service()
    return service.generate_quiz_questions("preconception", user_id)

def get_chatbot_response_prenatal(user_id):
    """Fetch AI-generated quiz questions for the prenatal stage"""
    service = get_hybrid_service()
    return service.generate_quiz_questions("prenatal", user_id)

def get_chatbot_response_birth(user_id):
    """Fetch AI-generated quiz questions for the birth stage"""
    service = get_hybrid_service()
    return service.generate_quiz_questions("birth", user_id)

def get_chatbot_response_postnatal(user_id):
    """Fetch AI-generated quiz questions for the postnatal stage"""
    service = get_hybrid_service()
    return service.generate_quiz_questions("postnatal", user_id)

def get_teaching_facts_by_stage(stage_name):
    """Generate teaching content for a given maternal health stage"""
    service = get_hybrid_service()
    return service.generate_teaching_facts(stage_name)
