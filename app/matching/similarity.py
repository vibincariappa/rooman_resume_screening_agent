from typing import List
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def calculate_similarity(vector_a: List[float], vector_b: List[float]) -> float:
    """
    Computes cosine similarity between two vector embeddings.
    Normalizes the score to a 0-100 percentage scale, rounded to 1 decimal place.
    """
    if not vector_a or not vector_b:
        raise ValueError("Vectors cannot be empty.")
        
    arr_a = np.array(vector_a).reshape(1, -1)
    arr_b = np.array(vector_b).reshape(1, -1)
    
    sim = cosine_similarity(arr_a, arr_b)[0][0]
    
    # Normalize score from [-1, 1] range to [0, 100]
    score = max(0.0, min(1.0, float(sim))) * 100.0
    return round(score, 1)
