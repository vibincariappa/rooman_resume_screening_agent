from typing import List, Dict
from sentence_transformers import SentenceTransformer

# Singleton cache for loaded models
_MODEL_CACHE: Dict[str, SentenceTransformer] = {}

def get_embedding_model(model_name: str = "all-MiniLM-L6-v2") -> SentenceTransformer:
    """
    Returns a cached SentenceTransformer model instance or loads a new one.
    """
    if model_name not in _MODEL_CACHE:
        _MODEL_CACHE[model_name] = SentenceTransformer(model_name)
    return _MODEL_CACHE[model_name]

def generate_embedding(text: str, model_name: str = "all-MiniLM-L6-v2") -> List[float]:
    """
    Generates a semantic embedding vector for a block of text.
    """
    # If text is empty, return an empty embedding or raise an error
    if not text.strip():
        raise ValueError("Cannot embed empty text.")
        
    model = get_embedding_model(model_name)
    vector = model.encode(text)
    return vector.tolist()
