import re
from app.text_utils import normalize_text

RISK_TERMS = [
    "risk", "may", "could", "uncertain", "adverse", "pressure", 
    "volatility", "regulatory", "competition", "impact", 
    "material", "fail", "loss", "dispute", "litigation", "breach",
]

def risk_score(text: str) -> int:
    text_lower = text.lower()
    return sum(term in text_lower for term in RISK_TERMS)


def extract_risk_snippets(chunks, top_k=3):
    risk_chunks = []

    for c in chunks:
        if c["metadata"]["section"] == "Risk Factors":
            score = risk_score(c["page_content"])
            if score > 0:
                risk_chunks.append((
                    score,
                    c["page_content"],
                    c["metadata"]   # preserve metadata
                ))

    risk_chunks.sort(key=lambda x: x[0], reverse=True)
    return risk_chunks[:top_k]


def split_into_sentences(text: str):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if len(s.strip()) > 20]


def extract_grounding_phrase(sentence: str) -> str:
    """
    Extracts a short risk-heavy substring from a sentence.
    """
    words = sentence.split()
    risky_words = [w for w in words if any(term in w.lower() for term in RISK_TERMS)]

    if not risky_words:
        return " ".join(words[:12])  # fallback

    # Take window around first risky word
    idx = words.index(risky_words[0])
    start = max(idx - 4, 0)
    end = min(idx + 6, len(words))

    return " ".join(words[start:end])

def truncate_sentence(text: str, max_words: int = 35) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]) + "..."


def build_risk_bullets(risk_snippets):
    bullets = []

    for score, text, metadata in risk_snippets:
        sentences = split_into_sentences(text)
        if not sentences:
            continue

        # FIX 1: Handle Chunk Boundaries (The "nal liabilities" fix)
        # If this isn't the very first chunk, the first "sentence" is likely 
        # a fragment cut off from the previous chunk. Skip it.
        if metadata.get("chunk_index", 0) > 0 and len(sentences) > 1:
            sentences = sentences[1:]

        # FIX 2: Filter for Sentence-Level Relevance (The "Boilerplate" fix)
        # Only consider sentences that actually contain a risk term
        risky_sentences = [
            s for s in sentences 
            if sum(term in s.lower() for term in RISK_TERMS) > 0
        ]

        # If no specific sentence has a risk term, skip this chunk
        if not risky_sentences:
            continue

        # Find the single most "risky" sentence
        best_sentence = max(
            risky_sentences,
            key=lambda s: sum(term in s.lower() for term in RISK_TERMS)
        )

        # Normalize and Clean
        cleaned_sentence = normalize_text(best_sentence)
        
        # FIX 3: Clean up truncation (Don't cut off in the middle of a word)
        # Use your truncate function, but maybe bump max_words to 40 for context
        final_bullet = truncate_sentence(cleaned_sentence, max_words=40)
        
        grounding_phrase = extract_grounding_phrase(final_bullet)

        bullets.append({
            "bullet": final_bullet,
            "grounding_phrase": grounding_phrase,
            "section": "Risk Factors",
            "metadata": {
                "filing_id": metadata.get("filing_id"),
                "chunk_index": metadata.get("chunk_index")
            }
        })

    return bullets