"""Prompt construction for each Study Buddy feature.

Keeping prompts here (separate from UI code) makes them easy to tune/version
without touching page logic, and easy to unit test in isolation.
"""
from typing import List, Dict

SYSTEM_TUTOR = (
    "You are an expert, patient tutor who explains things clearly and "
    "accurately for students. Never fabricate facts. If you are unsure "
    "about something, say so explicitly instead of guessing."
)

SYSTEM_JSON_GENERATOR = (
    "You are a precise content generator for a study app. You ALWAYS "
    "respond with strict, valid JSON only — no markdown code fences, "
    "no commentary, no trailing text before or after the JSON."
)


def explain_prompt(topic: str, level: str, style: str) -> List[Dict[str, str]]:
    return [
        {"role": "system", "content": SYSTEM_TUTOR},
        {
            "role": "user",
            "content": f"""Explain the following topic to a {level} student.
Explanation style: {style}.

Topic / Question:
{topic}

Rules:
- Be accurate; avoid jargon unless you immediately define it.
- Use short paragraphs and, where useful, a numbered or bulleted breakdown.
- End with a single line starting with "Key takeaway:".""",
        },
    ]


def summarize_prompt(text: str, length: str, fmt: str, highlight_terms: bool) -> List[Dict[str, str]]:
    terms_instruction = (
        "\nAlso list 5-10 key terms with a one-line definition each, under a 'KEY TERMS' heading."
        if highlight_terms
        else ""
    )
    return [
        {"role": "system", "content": SYSTEM_TUTOR},
        {
            "role": "user",
            "content": f"""Summarize the following study notes.
Summary length: {length}.
Output format: {fmt}.{terms_instruction}

Notes:
\"\"\"{text}\"\"\"

Do not add information that isn't present in the notes.""",
        },
    ]


def map_chunk_prompt(chunk: str) -> List[Dict[str, str]]:
    """Stage 1 of map-reduce summarization for long documents."""
    return [
        {"role": "system", "content": SYSTEM_TUTOR},
        {
            "role": "user",
            "content": (
                "Summarize the key points of this section in 4-6 concise bullet points, "
                "preserving facts and numbers exactly:\n\n" + chunk
            ),
        },
    ]


def reduce_summaries_prompt(combined: str, length: str, fmt: str) -> List[Dict[str, str]]:
    """Stage 2 of map-reduce summarization: merge partial summaries."""
    return [
        {"role": "system", "content": SYSTEM_TUTOR},
        {
            "role": "user",
            "content": f"""These are bullet-point summaries of consecutive sections of a long document:

{combined}

Combine them into a single coherent summary.
Length: {length}. Format: {fmt}.
Remove redundancy, keep it strictly factual.""",
        },
    ]


QUIZ_JSON_SCHEMA_HINT = """Respond with ONLY valid JSON matching this exact shape:
{
  "questions": [
    {
      "question": "string",
      "options": ["string", "string", "string", "string"],
      "correct_index": 0,
      "explanation": "string"
    }
  ]
}"""


def quiz_prompt(content: str, num_questions: int, difficulty: str) -> List[Dict[str, str]]:
    return [
        {"role": "system", "content": SYSTEM_JSON_GENERATOR},
        {
            "role": "user",
            "content": f"""Create {num_questions} multiple-choice questions ({difficulty} difficulty)
based on the content below. Each question must have exactly 4 options and exactly
one correct answer. correct_index is 0-based and must point to the correct option.

Content:
\"\"\"{content}\"\"\"

{QUIZ_JSON_SCHEMA_HINT}""",
        },
    ]


FLASHCARD_JSON_SCHEMA_HINT = """Respond with ONLY valid JSON matching this exact shape:
{
  "flashcards": [
    {"term": "string", "definition": "string", "hint": "string"}
  ]
}"""


def flashcards_prompt(content: str, num_cards: int) -> List[Dict[str, str]]:
    return [
        {"role": "system", "content": SYSTEM_JSON_GENERATOR},
        {
            "role": "user",
            "content": f"""Create {num_cards} flashcards (term + concise definition + a short hint)
based on the content below. Prioritize the most exam-relevant terms/concepts.

Content:
\"\"\"{content}\"\"\"

{FLASHCARD_JSON_SCHEMA_HINT}""",
        },
    ]
