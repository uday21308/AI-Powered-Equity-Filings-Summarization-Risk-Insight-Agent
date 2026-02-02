import json
from typing import List, Dict

def load_synthetic_filing(path: str) -> List[Dict]:
    """
    Loads a synthetic filing JSON and returns section-labeled documents.
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    documents = []

    filing_id = data["filing_id"]
    sections = data["sections"]

    for section_name, text in sections.items():
        documents.append({
            "page_content": text.strip(),
            "metadata": {
                "filing_id": filing_id,
                "section": section_name
            }
        })

    return documents

import os

def list_available_filings(path="corpus"):
    if not os.path.exists(path):
        return []
    return [
        f for f in os.listdir(path)
        if f.endswith(".json")
    ]
