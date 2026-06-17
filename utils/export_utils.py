"""Export utilities for quizzes and flashcards."""
import csv
import io
import json
from typing import List, Dict, Any


def quiz_to_json_bytes(quiz_data: Dict[str, Any]) -> bytes:
    """Converts quiz data to JSON bytes for download."""
    return json.dumps(quiz_data, indent=2).encode("utf-8")


def flashcards_to_csv(cards: List[Dict[str, str]]) -> bytes:
    """Converts flashcard data to CSV format."""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["term", "definition", "hint"])
    writer.writeheader()
    writer.writerows(cards)
    return output.getvalue().encode("utf-8")


def flashcards_to_anki_tsv(cards: List[Dict[str, str]]) -> bytes:
    """Converts flashcard data to Anki TSV format (term<tab>definition)."""
    output = io.StringIO()
    writer = csv.writer(output, delimiter="\t")
    for card in cards:
        writer.writerow([card.get("term", ""), card.get("definition", "")])
    return output.getvalue().encode("utf-8")
