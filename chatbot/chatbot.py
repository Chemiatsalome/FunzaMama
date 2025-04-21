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
GROUND_DATA_PATH = "maternal_health.jsonl"
FAISS_INDEX_PATH = "faiss_grounded_data.index"
GROUNDED_OUTPUTS_PATH = "grounded_outputs.json"

# Function to load JSONL file
def load_ground_data(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return [json.loads(line) for line in file]

# Load and process grounded data
ground_data = load_ground_data(GROUND_DATA_PATH)
grounded_texts = [entry["input"] for entry in ground_data]
grounded_outputs = [entry["output"] for entry in ground_data]

# Convert text inputs to embeddings
embeddings = embedding_model.encode(grounded_texts, normalize_embeddings=True)

# Create and save FAISS index
dimension = embeddings.shape[1]
faiss_index = faiss.IndexFlatL2(dimension)
faiss_index.add(np.array(embeddings, dtype=np.float32))
faiss.write_index(faiss_index, FAISS_INDEX_PATH)

# Save grounded responses for retrieval
with open(GROUNDED_OUTPUTS_PATH, "w", encoding="utf-8") as f:
    json.dump(grounded_outputs, f)

# Load FAISS index & outputs once (for efficiency)
faiss_index = faiss.read_index(FAISS_INDEX_PATH)
with open(GROUNDED_OUTPUTS_PATH, "r", encoding="utf-8") as f:
    grounded_outputs = json.load(f)

# Function to retrieve relevant data using FAISS
def get_relevant_data_faiss(user_message):
    user_embedding = embedding_model.encode([user_message], normalize_embeddings=True)
    D, I = faiss_index.search(np.array(user_embedding, dtype=np.float32), 1)
    return grounded_outputs[I[0][0]] if D[0][0] < 0.7 else None

# Initialize a chat history list
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
    
    chat_history.append({"role": "user", "content": user_message})
    
    total_tokens = sum(len(msg["content"].split()) for msg in chat_history)
    while total_tokens > 1500:
        chat_history.pop(0)
        total_tokens = sum(len(msg["content"].split()) for msg in chat_history)
    
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

# Function to evaluate FAISS retrieval accuracy
def evaluate_faiss_accuracy(test_queries, ground_truths):
    retrieved_results = [get_relevant_data_faiss(query) for query in test_queries]
    y_true = [1 if truth else 0 for truth in ground_truths]
    y_pred = [1 if res else 0 for res in retrieved_results]

    print("Retrieved Results:", retrieved_results)
    print("y_true:", y_true)
    print("y_pred:", y_pred)

    precision = precision_score(y_true, y_pred)
    recall = recall_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)

    return {"Precision": precision, "Recall": recall, "F1-Score": f1}

