import os
import pickle
import faiss
from sentence_transformers import SentenceTransformer

class DocumentRetriever:
    def __init__(self):
        base_dir = os.path.join(os.path.dirname(__file__), "..", "vectorstore")
        self.index = faiss.read_index(os.path.join(base_dir, "doc_index.faiss"))
        with open(os.path.join(base_dir, "doc_chunks.pkl"), "rb") as f:
            self.chunks = pickle.load(f)
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def retrieve(self, query, top_k=3):
        query_vector = self.model.encode([query]).astype("float32")
        distances, indices = self.index.search(query_vector, top_k)
        results = []
        for idx in indices[0]:
            results.append(self.chunks[idx])
        return results

    def get_context_string(self, query, top_k=3):
        """Returns retrieved chunks formatted as a single string to inject into a prompt"""
        results = self.retrieve(query, top_k=top_k)
        context = "\n\n".join([f"[From {r['source']}]: {r['text']}" for r in results])
        return context


if __name__ == "__main__":
    retriever = DocumentRetriever()
    test_query = "What is your refund window?"
    context = retriever.get_context_string(test_query)
    print(f"Query: {test_query}\n")
    print(f"Retrieved context:\n{context}")