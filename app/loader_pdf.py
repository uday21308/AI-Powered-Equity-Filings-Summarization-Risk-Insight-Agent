import json
import re
from langchain_community.document_loaders import PyPDFLoader

from app.text_utils import split_sentences

ITEM_PATTERN = re.compile(
    r"(ITEM\s+1A\.|ITEM\s+1\.|ITEM\s+7\.)",
    re.IGNORECASE
)

MDNA_KEYWORDS = {
    "Results": ["results of operations", "net revenue", "net income"],
    "Liquidity": ["liquidity and capital resources", "funding and liquidity", "cash flows"],
    "Outlook": ["outlook", "forward-looking", "future expectations"]
}

RISK_KEYWORDS = [
    "risk", "may", "could", "adverse", "uncertain",
    "impact", "regulatory", "competition", "supply"
]

LIQUIDITY_KEYWORDS = [
    "cash", "liquidity", "capital", "debt", "credit"
]

OUTLOOK_KEYWORDS = [
    "expect", "anticipate", "forecast", "trend", "future"
]

def keyword_score(sentence, keywords):
    s = sentence.lower()
    return sum(k in s for k in keywords)


def select_by_keywords(text, keywords, max_chars=10000):
    sentences = split_sentences(text)
    ranked = sorted(
        sentences,
        key=lambda s: keyword_score(s, keywords),
        reverse=True
    )

    selected, total = [], 0
    for s in ranked:
        if total + len(s) <= max_chars:
            selected.append(s)
            total += len(s)
        if total >= max_chars:
            break

    return " ".join(selected)


def extract_mdna(mdna_text):
    mdna_text_lower = mdna_text.lower()
    extracted = {}

    for name, keys in MDNA_KEYWORDS.items():
        for k in keys:
            if k in mdna_text_lower:
                start = mdna_text_lower.find(k)
                extracted[name] = mdna_text[start:start+10000]
                break

    return extracted

def load_pdf_filing(pdf_path: str, filing_id: str):
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()
    full_text = "\n".join(d.page_content for d in docs)

    parts = ITEM_PATTERN.split(full_text)
    sections = {}
    current_item = None

    for part in parts:
        part = part.strip()
        if re.match(ITEM_PATTERN, part):
            current_item = part.upper()
            sections[current_item] = ""
        elif current_item:
            sections[current_item] += part

    mdna_sections = extract_mdna(sections.get("ITEM 7.", ""))

    synthetic_sections = {
        "Business": sections.get("ITEM 1.", "")[:10000],
        "Risk Factors": select_by_keywords(
            sections.get("ITEM 1A.", ""), RISK_KEYWORDS
        ),
        "Results": mdna_sections.get("Results", ""),
        "Liquidity": select_by_keywords(
            mdna_sections.get("Liquidity", ""), LIQUIDITY_KEYWORDS
        ),
        "Outlook": select_by_keywords(
            mdna_sections.get("Outlook", ""), OUTLOOK_KEYWORDS
        )
    }

    # Convert to internal document format
    documents = []
    for section, text in synthetic_sections.items():
        documents.append({
            "page_content": text,
            "metadata": {
                "section": section,
                "filing_id": filing_id
            }
        })

    return documents
