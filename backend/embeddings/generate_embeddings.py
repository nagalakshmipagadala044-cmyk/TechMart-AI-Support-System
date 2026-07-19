from sentence_transformers import SentenceTransformer
import pandas as pd
import os
import pickle

# Load the embedding model (same family used for Plastic Pulse-style local ML work)
model = SentenceTransformer("all-MiniLM-L6-v2")

# Load Banking77-derived intent examples
banking_df = pd.read_csv("datasets/processed/banking77_techmart_clean.csv")

# Generate embeddings for each example query
print("Generating embeddings for intent examples...")
embeddings = model.encode(banking_df["query"].tolist(), show_progress_bar=True)

# Save embeddings + metadata together
os.makedirs("vectorstore", exist_ok=True)
with open("vectorstore/intent_embeddings.pkl", "wb") as f:
    pickle.dump({
        "embeddings": embeddings,
        "queries": banking_df["query"].tolist(),
        "categories": banking_df["category"].tolist()
    }, f)

print(f"Saved {len(embeddings)} embeddings to vectorstore/intent_embeddings.pkl")