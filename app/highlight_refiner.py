from pathlib import Path
from app.text_utils import normalize_text

PROMPT_PATH = Path("prompts/highlight_prompt.txt")

def refine_highlight(llm, section_text: str) -> str:
    section_text = normalize_text(section_text)

    prompt_template = PROMPT_PATH.read_text(encoding="utf-8")
    prompt = prompt_template.format(section_text=section_text)

    response = llm.invoke(prompt)
    return response.content.strip()
