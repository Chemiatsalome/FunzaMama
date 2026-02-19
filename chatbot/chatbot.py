# chatbot.py
import json
import os
from together import Together

# Optional imports for FAISS grounding (can be disabled to reduce image size)
try:
    import faiss
    import numpy as np
    from sentence_transformers import SentenceTransformer
    FAISS_AVAILABLE = True
    
    # Load Sentence Transformer model
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    
    # File paths
    FAISS_INDEX_PATH = "faiss_grounded_data.index"
    GROUNDED_OUTPUTS_PATH = "grounded_outputs.json"
    
    # Load FAISS index and grounded outputs
    try:
        faiss_index = faiss.read_index(FAISS_INDEX_PATH)
        with open(GROUNDED_OUTPUTS_PATH, "r", encoding="utf-8") as f:
            grounded_outputs = json.load(f)
    except (FileNotFoundError, Exception) as e:
        print(f"⚠️ FAISS index not found or error loading: {e}. Grounding disabled.")
        FAISS_AVAILABLE = False
        faiss_index = None
        grounded_outputs = None
except ImportError:
    print("⚠️ FAISS/sentence-transformers not available. Grounding disabled. Using Together AI only.")
    FAISS_AVAILABLE = False
    faiss_index = None
    grounded_outputs = None

# Initialize Together AI client - use environment variable
together_api_key = os.getenv('TOGETHER_API_KEY')
if not together_api_key:
    print("⚠️ WARNING: TOGETHER_API_KEY not set. Chatbot will use fallback responses only.")
    together_client = None
else:
    try:
        together_client = Together(api_key=together_api_key)
        print("✅ Together AI client initialized")
    except Exception as e:
        print(f"⚠️ WARNING: Failed to initialize Together AI client: {e}")
        together_client = None

# Function to retrieve relevant data using FAISS (optional)
def get_relevant_data_faiss(user_message):
    if not FAISS_AVAILABLE or faiss_index is None or grounded_outputs is None:
        return None
    
    try:
        user_embedding = embedding_model.encode([user_message], normalize_embeddings=True)
        D, I = faiss_index.search(np.array(user_embedding, dtype=np.float32), 1)
        
        if I[0][0] < len(grounded_outputs) and D[0][0] < 0.7:
            return grounded_outputs[I[0][0]]
        else:
            return None
    except Exception as e:
        print(f"⚠️ Error in FAISS search: {e}")
        return None

# Function to get or initialize chat history for a user/session
def get_chat_history(user_id="guest_user", session_id=None):
    """
    Get chat history for a specific user/session
    Note: In production, this should be stored in database or Redis for persistence
    For now, we'll use a simple dictionary keyed by user_id
    """
    if not hasattr(get_chat_history, 'history_store'):
        get_chat_history.history_store = {}
    
    key = f"{user_id}_{session_id}" if session_id else str(user_id)
    if key not in get_chat_history.history_store:
        get_chat_history.history_store[key] = []
    
    return get_chat_history.history_store[key]

def clear_chat_history(user_id="guest_user", session_id=None):
    """Clear chat history for a specific user/session"""
    if not hasattr(get_chat_history, 'history_store'):
        get_chat_history.history_store = {}
    
    key = f"{user_id}_{session_id}" if session_id else str(user_id)
    if key in get_chat_history.history_store:
        get_chat_history.history_store[key] = []

# Function to generate chatbot response
def get_chatbot_response(user_message, language, user_role, current_question=None, current_options=None, current_answer=None, user_id="guest_user", session_id=None, clear_history=False):
    import logging
    logger = logging.getLogger(__name__)
    
    # Check if Together AI is available
    if together_client is None:
        raise ValueError("Together AI not configured - TOGETHER_API_KEY not set")
    
    try:
        grounded_info = get_relevant_data_faiss(user_message)

        system_prompt = f"""You are FunzaMama, a compassionate and knowledgeable AI health companion specializing in maternal and neonatal health education.

Your primary audience is women and families in **Kenya and East Africa** using a mobile-friendly educational game.

Your role: Provide accurate, supportive, and personalized guidance about pregnancy, childbirth, newborn care, nutrition, and maternal health.

CONTEXT & LOCALIZATION (KENYA-FOCUSED):
- Assume the user is in **Kenya** unless they clearly say otherwise.
- Use **metric units** by default:
  - Weight: use **kilograms (kg)**, not pounds. If a source uses pounds, convert and clearly state both (e.g., "3.5 kg (about 7.7 lb)").
  - Height/length: use **centimetres (cm)** or **metres (m)**, not inches/feet.
  - Temperature: use **degrees Celsius (°C)**, not Fahrenheit.
- If you must mention non-metric units (like pounds), ALWAYS also give the Kenyan-friendly metric value.
- When giving examples, you may refer to typical Kenyan settings (county hospitals, clinics, maternity wards), but do NOT invent specific hospital names or fake phone numbers.
- For emergencies in Kenya you may mention that people can call **999 or 112** for urgent help.

CRITICAL RULES:
1. ALWAYS respond directly to the user's CURRENT message - never repeat previous responses
2. Be conversational, natural, and context-aware - remember the conversation history
3. For urgent medical concerns (bleeding, severe pain, emergency symptoms):
   - Acknowledge the concern with empathy
   - Provide immediate guidance
   - STRONGLY emphasize seeking immediate medical care
   - Do NOT provide diagnosis or delay seeking help
4. Format responses with clean HTML structure:
   - Use <p> tags for paragraphs
   - Use <strong> or <b> for emphasis
   - Use <ul><li> for lists
   - Use <div> with style for important callouts
   - Keep HTML simple and readable
5. Be specific and helpful - avoid generic responses
6. If user says "hey" or casual greetings, respond warmly and ask how you can help
7. Keep responses concise (200-400 words) but informative
8. End with a helpful follow-up question when appropriate

        User Role: {user_role}
        Language: {language}
        
Remember: You are having a real conversation. Each response should be unique and tailored to what the user just said."""
        
        # Add current_question context if provided (user is asking about a failed question)
        # When current_question is provided, it means the user wants help with that specific question
        if current_question and current_answer:
            system_prompt += f"\n\nIMPORTANT CONTEXT: The user is asking about a question they just encountered:\n"
            system_prompt += f"Question: {current_question}\n"
            if current_options:
                system_prompt += f"Options: {', '.join(current_options) if isinstance(current_options, list) else current_options}\n"
            system_prompt += f"Correct Answer: {current_answer}\n"
            system_prompt += f"\nCRITICAL: The user's current message is asking about this question. "
            system_prompt += f"Provide a helpful, encouraging explanation of why '{current_answer}' is correct. "
            system_prompt += f"Be specific, educational, and supportive. Explain the reasoning behind the answer. "
            system_prompt += f"DO NOT repeat the question or answer verbatim - explain WHY it's correct and provide helpful context."
        
        if grounded_info:
            system_prompt += f"\nUse this verified data:\n{grounded_info}"
        
        # Get or initialize chat history for this user/session
        chat_history = get_chat_history(user_id, session_id)
        
        # Clear history if requested (e.g., starting a new conversation)
        if clear_history:
            chat_history.clear()
        
        # Append user message
        chat_history.append({"role": "user", "content": user_message})
        
        # Trim chat history to stay under token limit (keep last ~10 messages for context)
        total_tokens = sum(len(msg["content"].split()) for msg in chat_history)
        while total_tokens > 1500 or len(chat_history) > 20:  # Limit to 20 messages max
            if len(chat_history) > 2:  # Keep at least user and assistant messages
                chat_history.pop(0)  # Remove oldest message
            else:
                break
            total_tokens = sum(len(msg["content"].split()) for msg in chat_history)
        
        # Generate response
        logger.info(f"Calling Together AI for user message: {user_message[:50]}...")
        response = together_client.chat.completions.create(
            model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",  # Faster model for chat
            messages=[{"role": "system", "content": system_prompt}] + chat_history,
            max_tokens=800,  # Increased for better responses
            temperature=0.8,  # Higher for more varied, natural responses
            top_p=0.95,  # Higher for better creativity
            top_k=50,
            repetition_penalty=1.2,  # Increased to prevent repetition
            stop=["<|eot_id|>", "\n\n\n"]  # Stop on multiple newlines
        )

        bot_response = response.choices[0].message.content
        if not bot_response or len(bot_response.strip()) == 0:
            raise ValueError("Empty response from Together AI")
        
        chat_history.append({"role": "assistant", "content": bot_response})
        logger.info(f"Successfully generated response: {bot_response[:50]}...")
        
        return bot_response
    
    except Exception as e:
        logger.error(f"Error in get_chatbot_response: {e}", exc_info=True)
        # Re-raise the exception so the route can handle it properly
        raise


