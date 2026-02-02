from app.chunker import chunk_documents
from app.summarizer import summarize_filing
from app.evaluator import groundedness_proxy, coherence_proxy, save_summary, check_failures
from app.loader_pdf import load_pdf_filing

# ---- Configuration ----
PDF_PATH = "data/raw_pdfs/cococola_10K.pdf"
FILING_ID = "cococola_10K_2025"

# ---- Load filing (PDF → internal docs) ----
docs = load_pdf_filing(
    pdf_path=PDF_PATH,
    filing_id=FILING_ID
)

# ---- Chunk documents ----
chunks = chunk_documents(docs, max_chars=1500, overlap=100)

# ---- Summarize ----
summary = summarize_filing(
    filing_id=FILING_ID,
    chunks=chunks
)

# ---- Evaluation ----
source_texts = [c["page_content"] for c in chunks]

summary["metrics"]["groundedness_proxy"] = groundedness_proxy(summary, source_texts)
summary["metrics"]["coherence_proxy"] = coherence_proxy(summary)

# ---- Save & log ----
output_path = save_summary(summary)
check_failures(summary)

print(f"Summary saved to: {output_path}")
print(summary)
