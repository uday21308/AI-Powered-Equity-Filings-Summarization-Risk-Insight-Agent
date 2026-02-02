def find_chunk(chunks, section: str, chunk_index: int):
    section = section.strip().lower()

    for c in chunks:
        if (
            c["metadata"].get("section", "").lower() == section and
            c["metadata"].get("chunk_index") == chunk_index
        ):
            return c["page_content"]

    return None
