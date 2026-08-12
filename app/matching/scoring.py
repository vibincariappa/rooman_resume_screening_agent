def calculate_score(skills_match: float, experience_match: float, semantic_similarity: float) -> float:
    """
    Computes a deterministic, explainable ranking score.
    Placeholder implementation.
    """
    return (skills_match * 0.4) + (experience_match * 0.3) + (semantic_similarity * 0.3)
