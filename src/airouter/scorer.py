
from .models import ModelSpec

def score_request(features, model: ModelSpec):
    score = 0

    for cap in features.get("capabilities", []):
        if cap in model.capabilities:
            score += 30

    if features.get("repo_aware"):
        if "repository" in model.capabilities:
            score += 25

    ctx = features.get("context_tokens", 0)
    if ctx > model.max_context * 0.5:
        score += 20

    score += model.priority
    return score
