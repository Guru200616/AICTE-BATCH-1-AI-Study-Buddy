"""Groq LLM client wrapper.

Centralizes every call to the AI provider so retry policy, timeouts, and
error handling live in one place instead of being duplicated per page.
"""
import time
from typing import List, Dict

import streamlit as st
from groq import Groq

from config import GROQ_API_KEY, MODEL_NAME, MAX_TOKENS, REQUEST_TIMEOUT

MAX_RETRIES = 3
BASE_BACKOFF_SECONDS = 1.5

# The Groq SDK is generated with the same tooling as the OpenAI SDK, so it
# exposes equivalent exception classes. We resolve them defensively so this
# module doesn't break across Groq SDK versions that may rename internals.
#
# IMPORTANT: only genuinely transient errors are retried. AuthenticationError,
# BadRequestError, etc. are subclasses of APIStatusError but will fail
# identically on every retry — bucketing them as retryable wastes ~9s+ of
# backoff before showing the user a generic error instead of "bad API key".
try:
    from groq import (
        APIError,
        APIConnectionError,
        APIStatusError,
        APITimeoutError,
        RateLimitError,
        InternalServerError,
    )

    _RETRYABLE_EXCEPTIONS: tuple = (RateLimitError, APIConnectionError, APITimeoutError, InternalServerError)
    # Catches everything else from the SDK (AuthenticationError, BadRequestError,
    # PermissionDeniedError, NotFoundError, ConflictError, UnprocessableEntityError,
    # or any future subclass) — all client-side / non-transient, so: fail fast.
    _KNOWN_API_EXCEPTIONS: tuple = (APIStatusError, APIError)
except ImportError:  # pragma: no cover - fallback for older/newer SDK layouts
    _RETRYABLE_EXCEPTIONS = ()
    _KNOWN_API_EXCEPTIONS = (Exception,)


class LLMError(Exception):
    """Raised when the LLM call fails after all retries (safe to show to users)."""


@st.cache_resource(show_spinner=False)
def get_client() -> Groq:
    if not GROQ_API_KEY:
        raise LLMError(
            "GROQ_API_KEY is not set. Add it to a .env file (see .env.example) "
            "and restart the app."
        )
    return Groq(api_key=GROQ_API_KEY, timeout=REQUEST_TIMEOUT)


def chat_completion(
    messages: List[Dict[str, str]],
    temperature: float = 0.4,
    max_tokens: int = MAX_TOKENS,
    model: str = MODEL_NAME,
) -> str:
    """
    Calls the Groq chat completion endpoint. Transient errors (rate limits,
    connection drops, 5xx) are retried with exponential backoff. Permanent
    errors (bad API key, malformed request, etc.) fail immediately with a
    specific, user-safe message instead of being retried pointlessly.
    """
    client = get_client()
    last_error: Exception | None = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            content = response.choices[0].message.content
            if not content or not content.strip():
                raise LLMError("The model returned an empty response.")
            return content.strip()

        except LLMError:
            raise  # already a clean, user-safe message — pass through unchanged

        except _RETRYABLE_EXCEPTIONS as exc:
            last_error = exc
            if attempt < MAX_RETRIES:
                time.sleep(BASE_BACKOFF_SECONDS * attempt)
            continue

        except _KNOWN_API_EXCEPTIONS as exc:
            # Reaching here means it's a known API error that isn't one of the
            # transient types above — i.e. a client-side / permanent failure.
            if type(exc).__name__ == "AuthenticationError":
                raise LLMError(
                    "Invalid or expired GROQ_API_KEY. Check your .env file and "
                    "get a valid key at https://console.groq.com/keys."
                ) from exc
            raise LLMError(f"Request rejected by the AI provider: {exc}") from exc

        except Exception as exc:  # noqa: BLE001 - unexpected error, fail fast
            raise LLMError(f"Unexpected error while calling the AI provider: {exc}") from exc

    raise LLMError(
        f"AI request failed after {MAX_RETRIES} attempt(s) due to a transient error. "
        f"Check your internet connection and try again. "
        f"(Internal: {type(last_error).__name__}: {last_error})"
    )
