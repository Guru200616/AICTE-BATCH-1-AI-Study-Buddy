"""Domain-level validation for LLM-generated structured content.

LLMs can return syntactically valid JSON that's still semantically broken —
wrong option count, an out-of-range correct_index, missing fields. Every
field that gets indexed downstream (pages/3_Generate_Quiz.py,
pages/4_Flashcards.py) is validated here first, so one malformed item can't
crash the page with an uncaught IndexError/KeyError mid-render. Bad items
are silently dropped rather than raising.
"""
from typing import Any, Dict, List

from core.json_utils import JSONParseError


def validate_quiz_questions(questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    valid: List[Dict[str, Any]] = []

    for q in questions:
        if not isinstance(q, dict):
            continue
        question = q.get("question")
        options = q.get("options")
        correct_index = q.get("correct_index")

        if not isinstance(question, str) or not question.strip():
            continue
        if not isinstance(options, list) or len(options) < 2:
            continue
        if not all(isinstance(opt, str) and opt.strip() for opt in options):
            continue
        if not isinstance(correct_index, int) or not (0 <= correct_index < len(options)):
            continue

        explanation = q.get("explanation")
        valid.append(
            {
                "question": question,
                "options": options,
                "correct_index": correct_index,
                "explanation": explanation if isinstance(explanation, str) else "",
            }
        )

    if not valid:
        raise JSONParseError("The model produced no usable questions. Please try again.")
    return valid


def validate_flashcards(cards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    valid: List[Dict[str, Any]] = []

    for card in cards:
        if not isinstance(card, dict):
            continue
        term = card.get("term")
        definition = card.get("definition")

        if not isinstance(term, str) or not term.strip():
            continue
        if not isinstance(definition, str) or not definition.strip():
            continue

        hint = card.get("hint")
        valid.append(
            {
                "term": term,
                "definition": definition,
                "hint": hint if isinstance(hint, str) else "",
            }
        )

    if not valid:
        raise JSONParseError("The model produced no usable flashcards. Please try again.")
    return valid
