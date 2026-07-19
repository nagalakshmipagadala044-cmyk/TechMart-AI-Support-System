from fastembed import TextEmbedding

_model = None

def get_embedding_model():
    global _model
    if _model is None:
        _model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
    return _model

def embed_text(texts):
    """Takes a list of strings, returns a list of embedding vectors."""
    model = get_embedding_model()
    return list(model.embed(texts))