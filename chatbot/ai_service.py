"""
AI Service with multiple provider fallbacks
"""

import os
import json
from typing import Optional, Dict, Any

class AIService:
    def __init__(self):
        self.providers = []
        self._setup_providers()
    
    def _setup_providers(self):
        """Setup available AI providers in order of preference"""
        
        # Provider 1: Together AI (current provider - most reliable)
        try:
            from together import Together
            together_key = os.getenv('TOGETHER_API_KEY', 'e3ab4476326269947afb85e9c0b0ed5fe9ae2949e27ed3a38ee4913d8f807b3e')
            self.providers.append({
                'name': 'together',
                'client': Together(api_key=together_key),
                'model': 'meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo',
                'max_tokens': 500
            })
            print("✅ Together AI provider configured")
        except ImportError:
            print("❌ Together AI not available")
        
        # Provider 2: OpenAI (if available)
        if os.getenv('OPENAI_API_KEY'):
            try:
                import openai
                self.providers.append({
                    'name': 'openai',
                    'client': openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY')),
                    'model': 'gpt-3.5-turbo',
                    'max_tokens': 500
                })
                print("✅ OpenAI provider configured")
            except ImportError:
                print("❌ OpenAI not available")
        
        if not self.providers:
            print("⚠️ No AI providers configured. Using fallback responses only.")
    
    def generate_response(self, messages: list, max_tokens: int = 500) -> Optional[str]:
        """Generate response using available providers"""
        
        for provider in self.providers:
            try:
                print(f"Trying {provider['name']} provider...")
                
                if provider['name'] == 'together':
                    response = provider['client'].chat.completions.create(
                        model=provider['model'],
                        messages=messages,
                        max_tokens=min(max_tokens, provider['max_tokens']),
                        temperature=0.7
                    )
                    return response.choices[0].message.content
                
                elif provider['name'] == 'openai':
                    response = provider['client'].chat.completions.create(
                        model=provider['model'],
                        messages=messages,
                        max_tokens=min(max_tokens, provider['max_tokens']),
                        temperature=0.7
                    )
                    return response.choices[0].message.content
                    
            except Exception as e:
                print(f"❌ {provider['name']} failed: {e}")
                continue
        
        return None
    
    def get_fallback_response(self, user_message: str) -> str:
        """Get fallback response when all providers fail"""
        message_lower = user_message.lower()
        
        if any(word in message_lower for word in ['pregnancy', 'pregnant', 'prenatal']):
            return "I'm here to help with pregnancy questions! During pregnancy, it's important to maintain regular prenatal care, eat a balanced diet, and stay active with your healthcare provider's approval. Is there something specific about pregnancy you'd like to know more about?"
        
        elif any(word in message_lower for word in ['birth', 'labor', 'delivery', 'contractions']):
            return "I can help with birth and delivery questions! Signs of labor include regular contractions, water breaking, and cervical dilation. It's important to contact your healthcare provider when you think labor has started. Do you have specific questions about the birthing process?"
        
        elif any(word in message_lower for word in ['baby', 'newborn', 'postnatal', 'postpartum']):
            return "I'm here to help with newborn and postnatal care questions! Newborns need frequent feeding, proper sleep positioning (on their back), and regular check-ups. Postpartum care for mothers includes rest, proper nutrition, and emotional support. What specific aspect of newborn or postnatal care would you like to know about?"
        
        elif any(word in message_lower for word in ['nutrition', 'diet', 'food', 'eating']):
            return "Nutrition is crucial for maternal health! During pregnancy, focus on a balanced diet with folic acid, iron, calcium, and protein. Avoid raw fish, unpasteurized foods, and excessive caffeine. Are you looking for specific nutritional advice for a particular stage?"
        
        elif any(word in message_lower for word in ['exercise', 'activity', 'fitness', 'workout']):
            return "Exercise during pregnancy can be beneficial with your healthcare provider's approval! Low-impact activities like walking, swimming, and prenatal yoga are generally safe. Always consult your healthcare provider before starting any exercise routine during pregnancy."
        
        else:
            return f"Thank you for your question: '{user_message}'. I'm Funza Mama, your AI assistant for maternal health education. I can help with questions about pregnancy, childbirth, newborn care, nutrition, exercise, and more. What specific maternal health topic would you like to learn about?"

# Global instance
ai_service = AIService()
