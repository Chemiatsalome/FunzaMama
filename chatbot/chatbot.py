# chatbot.py
import faiss
import json
import numpy as np
from together import Together
from sentence_transformers import SentenceTransformer
from sklearn.metrics import precision_score, recall_score, f1_score

# Initialize Together AI client
together_client = Together(api_key="e3ab4476326269947afb85e9c0b0ed5fe9ae2949e27ed3a38ee4913d8f807b3e")

# Load Sentence Transformer model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# File paths
FAISS_INDEX_PATH = "faiss_grounded_data.index"
GROUNDED_OUTPUTS_PATH = "grounded_outputs.json"

# Load FAISS index and grounded outputs
faiss_index = faiss.read_index(FAISS_INDEX_PATH)
with open(GROUNDED_OUTPUTS_PATH, "r", encoding="utf-8") as f:
    grounded_outputs = json.load(f)

# Function to retrieve relevant data using FAISS
def get_relevant_data_faiss(user_message):
    user_embedding = embedding_model.encode([user_message], normalize_embeddings=True)
    D, I = faiss_index.search(np.array(user_embedding, dtype=np.float32), 1)
    
    if I[0][0] < len(grounded_outputs) and D[0][0] < 0.7:
        return grounded_outputs[I[0][0]]
    else:
        return None

# Chat history for conversation memory
chat_history = []

# Function to generate chatbot response
def get_chatbot_response(user_message, language, user_role):
    grounded_info = get_relevant_data_faiss(user_message)

    system_prompt = f"""
    User Role: {user_role}
    Language: {language}
    
    You are FunzaMama, an AI chatbot specializing in maternal health education across all pregnancy stages. Format responses in structured HTML.
    """
    if grounded_info:
        system_prompt += f"\nUse this verified data:\n{grounded_info}"
    
    # Append user message
    chat_history.append({"role": "user", "content": user_message})
    
    # Trim chat history to stay under token limit
    total_tokens = sum(len(msg["content"].split()) for msg in chat_history)
    while total_tokens > 1500:
        chat_history.pop(0)
        total_tokens = sum(len(msg["content"].split()) for msg in chat_history)
    
    # Generate response
    response = together_client.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
        messages=[{"role": "system", "content": system_prompt}] + chat_history,
        max_tokens=699,
        temperature=0.11,
        top_p=1,
        top_k=50,
        repetition_penalty=1,
        stop=["<|eot_id|>"]
    )

    bot_response = response.choices[0].message.content
    chat_history.append({"role": "assistant", "content": bot_response})
    
    return bot_response

# Optional: Function to test accuracy
def evaluate_faiss_accuracy(test_queries, ground_truths):
    retrieved_results = [get_relevant_data_faiss(query) for query in test_queries]
    y_true = [1 if truth else 0 for truth in ground_truths]
    y_pred = [1 if res else 0 for res in retrieved_results]

    return {
        "Precision": precision_score(y_true, y_pred),
        "Recall": recall_score(y_true, y_pred),
        "F1-Score": f1_score(y_true, y_pred)
    }
