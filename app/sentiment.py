LM_UNCERTAINTY = {
    "may", "might", "could", "uncertain", "risk", "adverse",
    "volatility", "exposure", "impact"
}
LM_POSITIVE = {
    "increase", "growth", "improved", "strong", "record",
    "higher", "profit", "profitability", "solid", "stable"
}

def lm_uncertainty_score(texts):
    score = 0
    for t in texts:
        words = t.lower().split()
        score += sum(w in LM_UNCERTAINTY for w in words)
    return score

def lm_positive_score(texts):
    score = 0
    for t in texts:
        words = t.lower().split()
        score += sum(w in LM_POSITIVE for w in words)
    return score
