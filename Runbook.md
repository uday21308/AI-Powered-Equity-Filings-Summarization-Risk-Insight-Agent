## RUNBOOK.md

```markdown
# RUNBOOK: Operating and Extending the Filing Summarization Pipeline

This runbook describes how to operate the system and how to switch between different input sources without modifying the core pipeline.

---

## 1. Running the System (Baseline)

The pipeline is executed via:
- `main.py` for local runs
- `FastAPI` for interactive use

No code changes are required for standard execution.

---

## 2. Switching Between JSON and PDF Inputs

### JSON Input (Synthetic Filings)

Used during development and evaluation.

Loader:
```python
from app.loader import load_synthetic_filing
```
Entry point:
run_pipeline("corpus/example_filing.json")


PDF Input (Real Filings)
Used for real-world validation.

Loader:
from app.loader_pdf import load_pdf_filing


PDFs are:
Loaded using PyPDFLoade
Converted into section-labeled internal documents
Trimmed per section for controlled evaluation
The downstream pipeline remains unchanged.



### 3. Loader Swap Contract (Important)

All loaders must output documents in the following internal format:

{
  "page_content": "<text>",
  "metadata": {
    "section": "Risk Factors",
    "filing_id": "...",
    "chunk_index": 0
  }
}


As long as this contract is respected:

Chunking
Summarization
Risk extraction
Evaluation

will continue to work without modification.


How to Swap
In main.py:

### To use JSON:

Python

from app.loader import load_synthetic_filing as loader_fn
docs = loader_fn("corpus/apple.json")

### To use PDF

Python

from app.loader_pdf import load_pdf_filing as loader_fn
docs = loader_fn("uploads/nvidia.pdf")


### 4. Adding a New Input Source

To add a new data source (e.g., retrieval gateway, database, API):
Implement a new loader (e.g., loader_db.py)
Map raw input into the internal document schema
Call run_pipeline_from_docs(docs, filing_id)
No other changes are required.


### 5. Failure Inspection

Failure cases are logged in:

evaluation/errors.log

Each entry includes:
Filing ID
Failure category
This supports manual auditing and debugging.

### 6. Chunk Inspection 

Each risk bullet contains:

"metadata": { "chunk_index": 6 }
This allows tracing the risk back to the exact chunk in the source corpus.

### Summary

The system is designed so that:
Loaders are swappable
The pipeline is stable
Evaluation is consistent
Outputs are auditable
This enables safe experimentation with real filings while preserving reproducibility.
