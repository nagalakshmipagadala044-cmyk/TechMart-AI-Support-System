import faiss
import pickle
import numpy as np
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from shared_resources import get_embedding_model

class IntentVectorStore:
    def __init__(self, embeddings_path="vectorstore/intent_embeddings.pkl"):
        with open(embeddings_path, "rb") as f:
            data = pickle.load(f)

        self.embeddings = np.array(data["embeddings"]).astype("float32")
        self.queries = data["queries"]
        self.categories = data["categories"]

        dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(self.embeddings)

        self.model = get_embedding_model()

        print(f"FAISS index built with {self.index.ntotal} vectors")

    def search(self, query_text, top_k=5):
        query_vector = self.model.encode([query_text]).astype("float32")
        distances, indices = self.index.search(query_vector, top_k)

        results = []
        for i, idx in enumerate(indices[0]):
            results.append({
                "query": self.queries[idx],
                "category": self.categories[idx],
                "distance": float(distances[0][i])
            })
        return results

    def get_top_category(self, query_text, top_k=5):
        results = self.search(query_text, top_k=top_k)
        categories = [r["category"] for r in results]
        top_category = max(set(categories), key=categories.count)
        return top_category, results


if __name__ == "__main__":
    store = IntentVectorStore()
    test_message = "I paid yesterday but Premium is still locked"
    category, results = store.get_top_category(test_message)
    print(f"\nTest message: '{test_message}'")
    print(f"Predicted category: {category}\n")
    print("Top matches:")
    for r in results:
        print(f"  [{r['category']}] {r['query']} (distance: {r['distance']:.3f})")