"""AI Study Buddy — home / dashboard."""
import streamlit as st

from config import APP_NAME, GROQ_API_KEY
from utils.ui import configure_page, render_hero, render_card

configure_page("Home")
render_hero(
    f"🎓 {APP_NAME}",
    "Explain concepts, summarize notes, and generate quizzes & flashcards — instantly.",
)

if not GROQ_API_KEY:
    st.error(
        "**GROQ_API_KEY is not configured.**\n\n"
        "1. Copy `.env.example` to `.env`\n"
        "2. Add your key: `GROQ_API_KEY=your_key_here`\n"
        "3. Get a free key at https://console.groq.com/keys\n"
        "4. Restart the app: `streamlit run app.py`"
    )
    st.stop()

st.session_state.setdefault("quizzes_taken", 0)
st.session_state.setdefault("best_score", 0)

col1, col2 = st.columns(2)
with col1:
    render_card(
        "<h3>📘 Explain a Concept</h3>"
        "<p>Stuck on a topic? Get a clear, level-appropriate explanation with analogies.</p>"
    )
with col2:
    render_card(
        "<h3>📝 Summarize Notes</h3>"
        "<p>Paste or upload long notes (.txt / .pdf) and get a concise, structured summary.</p>"
    )

col3, col4 = st.columns(2)
with col3:
    render_card(
        "<h3>🧩 Generate a Quiz</h3>"
        "<p>Turn any topic or your notes into an interactive multiple-choice quiz.</p>"
    )
with col4:
    render_card(
        "<h3>🃏 Flashcards</h3>"
        "<p>Auto-generate flip flashcards and export them to CSV or Anki.</p>"
    )

st.info("👈 Use the sidebar to open a tool.")

m1, m2 = st.columns(2)
m1.metric("Quizzes taken this session", st.session_state["quizzes_taken"])
m2.metric("Best score this session", f"{st.session_state['best_score']}%")
