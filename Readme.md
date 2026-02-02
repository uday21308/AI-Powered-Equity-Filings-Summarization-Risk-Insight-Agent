# Equity Filing Summarization Pipeline

This project implements a modular, section-aware pipeline for summarizing equity filings (10-K style documents) with a strong emphasis on grounding, traceability, and evaluation.

The system produces concise analyst-style summaries consisting of:
- Highlights (2 bullets)
- Risks (3 grounded bullets)
- Tone (positive / neutral / cautious)

The pipeline is designed to work with both synthetic JSON filings and real PDF filings through a swappable loader architecture.

---

## Project Structure
```text
.
├── app/
│   ├── api.py               # FastAPI application & endpoints
│   ├── chunker.py           # Sliding window chunking logic
│   ├── debug_utils.py       # Finding the chunk helper function
│   ├── evaluator.py         # Groundedness & coherence metrics calculation
│   ├── highlight_refiner.py # LLM orchestration for "Highlights" section
│   ├── llm_provider.py      # LLM client setup (Groq/OpenAI)
│   ├── loader.py            # Standard loader for JSON corpus
│   ├── loader_pdf.py        # PDF loader with Regex section mapping
│   ├── pipeline.py          # Shared orchestration logic
│   ├── risk_agent.py        # Deterministic extraction logic for "Risk Factors"
│   ├── sentiment.py         # Loughran–McDonald lexicon scorer
│   ├── summarizer.py        # Main agent entry point
│   |── text_utils.py        # Text normalization & cleaning helpers
|   └── main.py              # CLI entry point
corpus/
├── apple_synthetic.json        # Reference stable filing
├── tesla_synthetic.json        # High-volatility reference
└── goldmansachs_synthetic.json # Banking domain reference
|
evaluation/
├── sample_summary.json  # Output artifacts
└── errors.log           # detailed failure audit log
|
prompts/
└── highlight_prompt.txt # Prompt template for abstraction

```
---


## Setup Instructions


### 1. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```


### 2. Install Dependencies
pip install -r requirements.txt



### 3. Configure Environment Variables

Create a .env file:

GROQ_API_KEY=your_groq_key_here
LLM_PROVIDER=groq



### 4. Running the Pipeline (JSON Input)
python main.py
This loads a synthetic filing from corpus/, runs the full pipeline, and saves the output to evaluation/.



### 5. Running the API
uvicorn app.api:app --reload

Open:
http://127.0.0.1:8000/docs

Available endpoints:

GET	/filings	Lists all available JSON filings in the corpus/ directory.

POST /summarize → summarize a synthetic JSON filing

POST /summarize/pdf → upload and summarize a PDF filing

POST	/chunk  retrives the chunk with the chunk index we give

Output Format

All summaries follow this schema:
```
{
  "filing_id": "...",
  "highlights": [{ "bullet": "...", "section": "Results" }],
  "risks": [{
    "bullet": "...",
    "grounding_phrase": "...",
    "section": "Risk Factors",
    "metadata": { "filing_id": "...", "chunk_index": 3 }
  }],
  "tone": "cautious",
  "metrics": {
    "groundedness_proxy": 0.92,
    "coherence_proxy": true
  }
}
```


### 6. Design Principles

Risks are strictly extractive and grounded
LLM usage is limited to highlight abstraction
Tone is lexicon-based and interpretable
Evaluation is deterministic and auditable
Loader is the only component that changes across input formats


