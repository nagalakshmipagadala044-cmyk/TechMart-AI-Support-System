import os
import sys
import pickle
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

sys.path.append(os.path.dirname(__file__))
from chunker import process_knowledge_base

def build_document_index():
    print("Chunking knowledge base documents...")
    chunks = process_knowledge_base()

    print(f"\nGenerating embeddings for {len(chunks)} chunks...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    texts = [c["text"] for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=True).astype("float32")

    print("\nBuilding FAISS index...")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    # Save the FAISS index itself
    output_dir = os.path.join(os.path.dirname(__file__), "..", "vectorstore")
    os.makedirs(output_dir, exist_ok=True)
    faiss.write_index(index, os.path.join(output_dir, "doc_index.faiss"))

    # Save the chunk metadata (text + source) separately, same order as the index
    with open(os.path.join(output_dir, "doc_chunks.pkl"), "wb") as f:
        pickle.dump(chunks, f)

    print(f"\nSaved doc_index.faiss and doc_chunks.pkl to {output_dir}")
    print(f"Index contains {index.ntotal} vectors")

    return index, chunks


if __name__ == "__main__":
    build_document_index()