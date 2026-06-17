# 🎓 AI Study Buddy

An AI-powered study companion that explains complex concepts in simple
terms, summarizes long notes, and generates quizzes & flashcards on demand —
solving the "long/irrelevant search results, teacher not available" problem
for students.

## 🚀 Features

| Feature | What it does |
|---|---|
| 📘 Explain a Concept | Level-aware explanations (Beginner → Exam Cram) with analogy / step-by-step / real-world styles |
| 📝 Summarize Notes | Paste text or upload `.txt`/`.pdf`; map-reduce summarization handles long documents without truncation |
| 🧩 Generate Quiz | On-demand MCQ quiz from any topic or your notes, with instant scoring + explanations |
| 🃏 Flashcards | Auto-generated flip flashcards; export to CSV or Anki-importable TSV |

Each tool can feed its output directly into the next ("Quiz me on this" /
"Make flashcards from this") so a student can go explanation → quiz → cards
without retyping anything.

## 🛠️ Tech Stack

- **Python 3.10+**
- **Streamlit** — UI + native multipage routing
- **Groq API** (Llama 3.3 70B) — LLM inference
- **pypdf** — PDF text extraction
- **python-dotenv** — environment configuration

## 📂 Project Structure

```
study-buddy-ai/
├── app.py                      # Home dashboard
├── config.py                   # Centralized env/config (single source of truth)
├── core/
│   ├── llm_client.py           # Groq client: retries, backoff, error handling
│   ├── prompts.py               # All prompt templates
│   └── json_utils.py           # Defensive JSON extraction from LLM output
├── utils/
│   ├── ui.py                    # Shared CSS/theme + components (hero, cards, flip-cards)
│   ├── file_utils.py           # PDF/TXT extraction + chunking for long docs
│   └── export_utils.py         # CSV / Anki TSV / JSON export
├── pages/
│   ├── 1_Explain_Concept.py
│   ├── 2_Summarize_Notes.py
│   ├── 3_Generate_Quiz.py
│   └── 4_Flashcards.py
├── requirements.txt
├── .env.example
└── .gitignore
```

## 📦 Installation & Run

```bash
git clone <your-repo-url>
cd study-buddy-ai

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env            # then add your GROQ_API_KEY

streamlit run app.py
```

## ⚙️ Configuration

All tunables live in `.env` (see `.env.example`): model name, max tokens,
request timeout, and input-size guardrails (`MAX_INPUT_CHARS`,
`CHUNK_SIZE_CHARS`) that cap token cost and prevent abuse.

## 🧠 Engineering Notes

- **Long-document summarization** uses a map-reduce strategy (`utils/file_utils.chunk_text`
  + `core/prompts.map_chunk_prompt`/`reduce_summaries_prompt`) instead of
  naive truncation, so nothing past the model's context window is silently dropped.
- **Quiz/flashcard generation** requests strict JSON and parses it defensively
  (`core/json_utils.extract_json`) — tolerates markdown fences or stray text,
  which is the most common failure mode in LLM-wrapper apps.
- **Resilience**: `core/llm_client.py` retries transient API/network failures
  with exponential backoff and surfaces only user-safe error messages.
- **Cost guardrails**: input length is capped via `MAX_INPUT_CHARS`/`max_chars`
  on every text area to bound token spend per request.

## 🔮 Possible Extensions

- Swap Streamlit session state for a database (Postgres/SQLite) to persist
  quiz history and flashcard decks across sessions.
- Add a FastAPI backend + React frontend if you need a non-Streamlit UI or
  multi-user auth.
- Add spaced-repetition scheduling (SM-2 algorithm) for flashcard review.
- Support `.docx` notes via `python-docx`.

## 👩‍💻 Built by

Guru Rengarajan — AI/ML Internship Project, 2026
