import json
from chatbot import evaluate_faiss_accuracy  # Import the function from your existing script

# Sample test queries
test_queries = [
    "What are the signs of maternal complications?",
    "How can I ensure a healthy pregnancy?",
    "What foods should a pregnant woman eat?",
    "When should I visit a doctor during pregnancy?"
]

# Expected ground truth (1 if relevant data exists, 0 otherwise)
ground_truths = [1, 1, 1, 1]  # Modify based on actual data availability

# Run FAISS accuracy evaluation
results = evaluate_faiss_accuracy(test_queries, ground_truths)

# Print results
print("FAISS Retrieval Evaluation:")
print(json.dumps(results, indent=4))
