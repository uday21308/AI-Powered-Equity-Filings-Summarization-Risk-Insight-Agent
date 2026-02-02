from app.loader import load_synthetic_filing
from app.chunker import chunk_documents
from app.summarizer import summarize_filing
from app.evaluator import groundedness_proxy, coherence_proxy

def run_pipeline(filing_path: str):
    docs = load_synthetic_filing(filing_path)
    chunks = chunk_documents(docs, max_chars=1500, overlap=100)

    filing_id = filing_path.split("/")[-1]
    summary = summarize_filing(filing_id, chunks)

    source_texts = [c["page_content"] for c in chunks]
    summary["metrics"]["groundedness_proxy"] = groundedness_proxy(summary, source_texts)
    summary["metrics"]["coherence_proxy"] = coherence_proxy(summary)
    
    return summary


def run_pipeline_from_docs(docs, filing_id: str):
    chunks = chunk_documents(docs, max_chars=1500, overlap=100)

    summary = summarize_filing(filing_id, chunks)

    source_texts = [c["page_content"] for c in chunks]
    summary["metrics"]["groundedness_proxy"] = groundedness_proxy(summary, source_texts)
    summary["metrics"]["coherence_proxy"] = coherence_proxy(summary)

    return summary