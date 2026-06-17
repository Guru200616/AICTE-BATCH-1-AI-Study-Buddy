"""Centralized environment & app configuration.

All env vars are read once here. Nothing else in the codebase should call
os.getenv directly — keeps configuration auditable and easy to change.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# --- AI provider ---
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
MODEL_NAME: str = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")
MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "2048"))
REQUEST_TIMEOUT: float = float(os.getenv("REQUEST_TIMEOUT", "30"))

# --- Guardrails (control token cost / abuse) ---
MAX_INPUT_CHARS: int = int(os.getenv("MAX_INPUT_CHARS", "12000"))
CHUNK_SIZE_CHARS: int = int(os.getenv("CHUNK_SIZE_CHARS", "4000"))
DIRECT_SUMMARY_THRESHOLD: int = int(os.getenv("DIRECT_SUMMARY_THRESHOLD", "4000"))

# --- App identity / theme ---
APP_NAME = "AI Study Buddy"
APP_ICON = "🎓"

THEME = {
    "primary": "#2563eb",
    "primary_dark": "#1d4ed8",
    "bg": "#f8fafc",
    "text": "#1f2937",
    "muted": "#9ca3af",
}
