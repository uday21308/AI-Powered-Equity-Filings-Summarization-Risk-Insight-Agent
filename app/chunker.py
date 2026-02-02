from typing import List, Dict

def chunk_documents(docs: List[Dict], max_chars: int = 1500, overlap: int = 100) -> List[Dict]:
    chunks = []

    for doc in docs:
        text = doc["page_content"]
        metadata = doc["metadata"]

        if len(text) <= max_chars:
            chunks.append({
                "page_content": text,
                "metadata": {**metadata, "chunk_index": 0, "overlap": 0}
            })
            continue

        start = 0
        idx = 0
        while start < len(text):
            end = min(start + max_chars, len(text))
            chunk_text = text[start:end]

            chunks.append({
                "page_content": chunk_text,
                "metadata": {
                    **metadata,
                    "chunk_index": idx,
                    "overlap": overlap
                }
            })

            start += (max_chars - overlap)
            idx += 1

    return chunks
