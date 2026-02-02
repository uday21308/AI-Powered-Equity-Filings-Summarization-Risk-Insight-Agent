from typing import Dict, List
from app.risk_agent import extract_risk_snippets, build_risk_bullets
from app.sentiment import lm_uncertainty_score, lm_positive_score
from app.llm_provider import get_llm
from app.highlight_refiner import refine_highlight

def group_chunks_by_section(chunks):
    grouped = {}
    for c in chunks:
        section = c["metadata"]["section"]
        grouped.setdefault(section, []).append(c["page_content"])
    return grouped

llm = get_llm()

def summarize_filing(
    filing_id: str,
    chunks: List[Dict]
) -> Dict:
    grouped = group_chunks_by_section(chunks)

    highlights = []

    # Highlight 1: Results
    if "Results" in grouped:
        raw_text = " ".join(grouped["Results"])
        text = refine_highlight(llm, raw_text)
        highlights.append({
            "bullet": text,
            "section": "Results"
        })

    # Highlight 2: Liquidity or Outlook fallback
    if "Liquidity" in grouped:
        raw_text = " ".join(grouped["Liquidity"])
        text = refine_highlight(llm, raw_text)
        highlights.append({
            "bullet": text,
            "section": "Liquidity"
        })
    elif "Outlook" in grouped:
        raw_text = " ".join(grouped["Outlook"])
        text = refine_highlight(llm, raw_text)
        highlights.append({
            "bullet": text,
            "section": "Outlook"
        })

    # --- Risk Extraction ---
    risk_snippets = extract_risk_snippets(chunks, top_k=3)
    risks = build_risk_bullets(risk_snippets)

    # --- Tone (Loughran–McDonald inspired heuristic) ---
    risk_texts = [r["bullet"] for r in risks]
    risk_uncertainty = lm_uncertainty_score(risk_texts)

    highlight_texts = [h["bullet"] for h in highlights]
    positive_signal = lm_positive_score(highlight_texts)

    if risk_uncertainty > 5:
        tone = "cautious"
    elif positive_signal > 3:
        tone = "positive"
    else:
        tone = "neutral"

    summary = {
        "filing_id": filing_id,
        "highlights": highlights[:2],
        "risks": risks,
        "tone": tone,
        "metrics": {}
    }

    return summary
