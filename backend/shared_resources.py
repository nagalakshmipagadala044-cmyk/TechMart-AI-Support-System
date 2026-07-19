from sentence_transformers import SentenceTransformer

_model = None

def get_embedding_model():
    """Loads the embedding model once and reuses it everywhere -- prevents
    loading the same ~90MB model multiple times across agents/router."""
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model