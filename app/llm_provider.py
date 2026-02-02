import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Load .env file
load_dotenv()

def get_llm():
    provider = os.getenv("LLM_PROVIDER", "groq")

    if provider == "groq":
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment")

        return ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0.4,
            api_key=api_key
        )

    raise ValueError("Unsupported LLM provider")
