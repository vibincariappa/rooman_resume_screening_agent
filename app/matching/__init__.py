# Matching package for text embedding generation and similarity calculations
from app.matching.embeddings import generate_embedding
from app.matching.similarity import calculate_similarity
from app.matching.scoring import calculate_score

__all__ = ["generate_embedding", "calculate_similarity", "calculate_score"]
