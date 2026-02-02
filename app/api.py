from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from app.pipeline import run_pipeline
from app.loader import list_available_filings
from app.loader import load_synthetic_filing
from app.chunker import chunk_documents
from app.debug_utils import find_chunk
from fastapi import Query
from fastapi import UploadFile, File
from app.loader_pdf import load_pdf_filing
from app.pipeline import run_pipeline_from_docs

app = FastAPI(title="Equity Filing Summarizer")

class SummarizeRequest(BaseModel):
    filing_name: str

@app.get("/filings")
def get_filings():
    return {"available_filings": list_available_filings()}

@app.post("/summarize")
def summarize(req: SummarizeRequest):
    filing_path = os.path.join("corpus", req.filing_name)

    if not os.path.exists(filing_path):
        raise HTTPException(status_code=404, detail="Filing not found")

    summary = run_pipeline(filing_path)
    return summary


@app.get("/chunk")
def get_chunk(
    filing_name: str = Query(..., description="Synthetic filing filename eg. nvidea_synthetic.json"),
    section: str = Query(..., description="Section name, e.g. Risk Factors"),
    chunk_index: int = Query(..., description="Chunk index")
):
    filing_path = os.path.join("corpus", filing_name)

    if not os.path.exists(filing_path):
        raise HTTPException(status_code=404, detail="Filing not found")

    # Re-load and re-chunk deterministically
    docs = load_synthetic_filing(filing_path)
    chunks = chunk_documents(docs, max_chars=1500, overlap=100)

    text = find_chunk(chunks, section, chunk_index)

    if text is None:
        raise HTTPException(status_code=404, detail="Chunk not found")

    return {
        "filing_name": filing_name,
        "section": section,
        "chunk_index": chunk_index,
        "text": text
    }

@app.post("/summarize/pdf")
async def summarize_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files supported")

    # Save temp PDF
    temp_path = f"data/tmp/{file.filename}"
    os.makedirs("data/tmp", exist_ok=True)

    with open(temp_path, "wb") as f:
        f.write(await file.read())

    docs = load_pdf_filing(
        pdf_path=temp_path,
        filing_id=file.filename.replace(".pdf", "")
    )

    summary = run_pipeline_from_docs(
        docs,
        filing_id=file.filename.replace(".pdf", "")
    )

    return summary