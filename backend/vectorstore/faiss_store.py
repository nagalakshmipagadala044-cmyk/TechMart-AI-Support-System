import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer

class IntentVectorStore:
    def __init__(self, embeddings_path="vectorstore/intent_embeddings.pkl"):
        # Load the pre-computed embeddings + metadata
        with open(embeddings_path, "rb") as f:
            data = pickle.load(f)

        self.embeddings = np.array(data["embeddings"]).astype("float32")
        self.queries = data["queries"]
        self.categories = data["categories"]

        # Build the FAISS index
        dimension = self.embeddings.shape[1]  # 384 for all-MiniLM-L6-v2
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(self.embeddings)

        # Load the same model used to generate embeddings, so queries
        # get embedded the same way at search time
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        print(f"FAISS index built with {self.index.ntotal} vectors")

    def search(self, query_text, top_k=5):
        """
        Given a customer's message, find the most similar past examples
        and return their categories (used for intent detection).
        """
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
        """
        Returns the single most likely intent category for a message,
        based on majority vote among the top_k nearest examples.
        """
        results = self.search(query_text, top_k=top_k)
        categories = [r["category"] for r in results]
        # Most common category among nearest neighbors
        top_category = max(set(categories), key=categories.count)
        return top_category, results


# Quick manual test — only runs if this file is executed directly
if __name__ == "__main__":
    store = IntentVectorStore()

    test_message = "I paid yesterday but Premium is still locked"
    category, results = store.get_top_category(test_message)

    print(f"\nTest message: '{test_message}'")
    print(f"Predicted category: {category}\n")
    print("Top matches:")
    for r in results:
        print(f"  [{r['category']}] {r['query']} (distance: {r['distance']:.3f})")