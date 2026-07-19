import os
import sys
import pickle
import numpy as np
import faiss

sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from chunker import process_knowledge_base
from shared_resources import embed_text

def build_document_index():
    print("Chunking knowledge base documents...")
    chunks = process_knowledge_base()

    print(f"\nGenerating embeddings for {len(chunks)} chunks...")
    texts = [c["text"] for c in chunks]
    embeddings = np.array(embed_text(texts)).astype("float32")

    print("\nBuilding FAISS index...")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    output_dir = os.path.join(os.path.dirname(__file__), "..", "vectorstore")
    os.makedirs(output_dir, exist_ok=True)
    faiss.write_index(index, os.path.join(output_dir, "doc_index.faiss"))

    with open(os.path.join(output_dir, "doc_chunks.pkl"), "wb") as f:
        pickle.dump(chunks, f)

    print(f"\nSaved doc_index.faiss and doc_chunks.pkl to {output_dir}")
    print(f"Index contains {index.ntotal} vectors")

    return index, chunks


if __name__ == "__main__":
    build_document_index()