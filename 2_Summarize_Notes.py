"""Robust JSON extraction from LLM text output.

LLMs occasionally wrap JSON in markdown fences or add stray text even when
explicitly told not to. This module parses defensively instead of trusting
the model's formatting, which is the actual root cause of most "quiz failed
to generate" bugs in LLM-wrapper apps.
"""
import json
import re
from typing import Any


class JSONParseError(Exception):
    """Raised when no valid JSON object/array can be extracted from model output."""


def extract_json(raw: str) -> Any:
    """Extracts and parses a JSON object/array from raw LLM text."""
    cleaned = raw.strip()
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned, flags=re.MULTILINE).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Fallback: grab the largest {...} or [...] block in the text.
    match = re.search(r"(\{.*\}|\[.*\])", cleaned, flags=re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError as exc:
            raise JSONParseError(f"Model output looked like JSON but failed to parse: {exc}") from exc

    raise JSONParseError("No JSON object found in the model's output.")
