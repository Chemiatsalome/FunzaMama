# chatbot.py
import json
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

# Initialize Together AI client
together_client = Together(api_key="e3ab4476326269947afb85e9c0b0ed5fe9ae2949e27ed3a38ee4913d8f807b3e")

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
    
    try:
        grounded_info = get_relevant_data_faiss(user_message)

        system_prompt = f"""
        User Role: {user_role}
        Language: {language}
        
        You are FunzaMama, an AI chatbot specializing in maternal health education across all pregnancy stages. 
        
        IMPORTANT: 
        - ALWAYS respond to the user's CURRENT message/question, not previous questions
        - Maintain conversation context from previous messages in the chat history
        - Be conversational and engaging, allowing for follow-up questions
        - If the user asks a NEW question, answer that NEW question, not a previous one
        - End responses by asking if the user has more questions or wants to explore related topics
        - Format responses in structured HTML with clear sections
        - Keep responses informative but not overwhelming (300-500 words)
        - Use friendly, supportive, and encouraging tone
        """
        
        # Add current_question context if provided (user is asking about a failed question)
        # When current_question is provided, it means the user wants help with that specific question
        if current_question and current_answer:
            system_prompt += f"\n\nIMPORTANT CONTEXT: The user is asking about a question they just encountered:\n"
            system_prompt += f"Question: {current_question}\n"
            if current_options:
                system_prompt += f"Options: {', '.join(current_options) if isinstance(current_options, list) else current_options}\n"
            system_prompt += f"Correct Answer: {current_answer}\n"
            system_prompt += f"\nProvide a helpful, encouraging explanation of why '{current_answer}' is correct. Be supportive and educational. "
            system_prompt += f"However, if the user asks a NEW question (not about this question), answer their NEW question instead."
        
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
            max_tokens=699,
            temperature=0.7,  # Increased from 0.11 for more varied responses
            top_p=0.9,  # Adjusted for better response quality
            top_k=50,
            repetition_penalty=1.1,  # Slight increase to reduce repetition
            stop=["<|eot_id|>"]
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


