# build_index.py
import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer

# File paths
GROUND_DATA_PATH = "maternal_health.jsonl"
FAISS_INDEX_PATH = "faiss_grounded_data.index"
GROUNDED_OUTPUTS_PATH = "grounded_outputs.json"

# Load Sentence Transformer model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Load JSONL data
def load_ground_data(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return [json.loads(line) for line in file]

# Load and process grounded data
ground_data = load_ground_data(GROUND_DATA_PATH)
grounded_texts = [entry["input"] for entry in ground_data]
grounded_outputs = [entry["output"] for entry in ground_data]

# Generate embeddings
embeddings = embedding_model.encode(grounded_texts, normalize_embeddings=True)

# Create and save FAISS index
dimension = embeddings.shape[1]
faiss_index = faiss.IndexFlatL2(dimension)
faiss_index.add(np.array(embeddings, dtype=np.float32))
faiss.write_index(faiss_index, FAISS_INDEX_PATH)

# Save grounded responses for retrieval
with open(GROUNDED_OUTPUTS_PATH, "w", encoding="utf-8") as f:
    json.dump(grounded_outputs, f)

print("✅ Index and outputs successfully built and saved.")
