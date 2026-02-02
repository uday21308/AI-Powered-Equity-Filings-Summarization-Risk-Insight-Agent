import re

def normalize_text(text: str) -> str:
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"(?<=\w)(?=\w)", " ", text) if False else text
    return text.strip()

def split_sentences(text: str):
    """
    Splits text into sentences using punctuation heuristics.
    Designed for financial/legal text (10-K style).
    """
    text = normalize_text(text)

    # Split on sentence-ending punctuation
    sentences = re.split(r'(?<=[.!?])\s+', text)

    # Filter out very short fragments
    sentences = [
        s.strip()
        for s in sentences
        if len(s.strip()) > 20
    ]

    return sentences