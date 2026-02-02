def groundedness_proxy(summary: dict, source_texts: list) -> float:
    """
    Measures how much of the summary text appears in the source.
    """
    STOP_WORDS = {"the", "and", "is", "of", "to", "in", "a", "for"}
    summary_text = ""

    for h in summary["highlights"]:
        summary_text += h["bullet"] + " "

    for r in summary["risks"]:
        summary_text += r["grounding_phrase"] + " "

    source_blob = " ".join(source_texts)
    
    matched = sum(1 for w in summary_text.split() if w not in STOP_WORDS and w in source_blob)
    total = sum(1 for w in summary_text.split() if w not in STOP_WORDS)
    return round(matched / total, 2)


def coherence_proxy(summary: dict) -> bool:
    return (
        len(summary["highlights"]) == 2 and
        2 <= len(summary["risks"]) <= 3 and
        summary["tone"] in {"positive", "neutral", "cautious"}
    )

def log_error(filing_id: str, reason: str):
    with open("evaluation/errors.log", "a") as f:
        f.write(f"{filing_id}: {reason}\n")

import json
import os

def save_summary(summary: dict):
    os.makedirs("evaluation", exist_ok=True)

    filing_id = summary["filing_id"].replace(".json", "")
    filename = f"{filing_id}_summary.json"

    path = os.path.join("evaluation", filename)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    return path


def log_failure(filing_id: str, issue_type: str, reason: str):
    with open("evaluation/errors.log", "a", encoding="utf-8") as f:
        f.write(f"{filing_id} | {issue_type} | {reason}\n")


def check_failures(summary: dict):
    filing_id = summary["filing_id"]

    # 1. Low groundedness
    if summary["metrics"].get("groundedness_proxy", 1.0) < 0.4:
        log_failure(
            filing_id,
            "LOW_GROUNDEDNESS",
            "High proportion of abstractive text relative to source"
        )

    # 2. Tone mismatch (heuristic check)
    risk_text = " ".join(r["bullet"].lower() for r in summary["risks"])
    has_uncertainty = any(w in risk_text for w in ["may", "could", "uncertain", "adverse"])

    if has_uncertainty and summary["tone"] == "positive":
        log_failure(
            filing_id,
            "TONE_MISMATCH",
            "Risk language indicates uncertainty but tone classified as positive"
        )

    # 3. Empty bullets
    for r in summary["risks"]:
        if not r["bullet"].strip():
            log_failure(
                filing_id,
                "EMPTY_RISK_BULLET",
                "Extracted risk bullet was empty"
            )

    # 4. Overlong bullets
    for r in summary["risks"]:
        if len(r["bullet"].split()) > 40:
            log_failure(
                filing_id,
                "OVERLONG_RISK_BULLET",
                "Risk sentence exceeds recommended word limit"
            )

    # 5. Metadata issues
    for r in summary["risks"]:
        meta = r.get("metadata", {})
        if meta.get("chunk_index") is None:
            log_failure(
                filing_id,
                "MISSING_CHUNK_INDEX",
                "Risk bullet missing chunk index metadata"
            )
