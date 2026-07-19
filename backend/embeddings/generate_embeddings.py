import sys
import os
import pandas as pd
import pickle
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from shared_resources import embed_text

# Load Banking77-derived intent examples
banking_df = pd.read_csv("datasets/processed/banking77_techmart_clean.csv")

# Generate embeddings for each example query
print("Generating embeddings for intent examples...")
embeddings = np.array(embed_text(banking_df["query"].tolist()))

# Save embeddings + metadata together
os.makedirs("vectorstore", exist_ok=True)
with open("vectorstore/intent_embeddings.pkl", "wb") as f:
    pickle.dump({
        "embeddings": embeddings,
        "queries": banking_df["query"].tolist(),
        "categories": banking_df["category"].tolist()
    }, f)

print(f"Saved {len(embeddings)} embeddings to vectorstore/intent_embeddings.pkl")