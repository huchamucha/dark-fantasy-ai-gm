from pathlib import Path
import os

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env", override=True)

# LM Studio OpenAI-compatible server. Override in the project-root .env.
LLM_URL = os.getenv("LLM_URL", "http://localhost:1235/v1/chat/completions")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen2.5-7b-instruct")
