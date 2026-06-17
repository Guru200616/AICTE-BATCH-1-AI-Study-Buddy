"""Generate Quiz page."""
import streamlit as st

from core.llm_client import chat_completion, LLMError
from core.prompts import quiz_prompt
from core.json_utils import extract_json, JSONParseError
from core.validators import validate_quiz_questions
from utils.ui import configure_page, render_hero, render_card
from utils.export_utils import quiz_to_json_bytes
from config import MAX_INPUT_CHARS

configure_page("Generate Quiz")
render_hero("🧩 Generate a Quiz", "Turn any topic or your notes into an interactive multiple-choice quiz.")

seeded = st.session_state.pop("seed_content", None)
if seeded:
    st.info("Using content carried over from a previous page. Edit below if needed.")

content = st.text_area(
    "Topic or notes to quiz on",
    value=seeded or "",
    height=180,
    max_chars=MAX_INPUT_CHARS,
    placeholder="e.g. Photosynthesis, or paste your notes...",
)

c1, c2 = st.columns(2)
num_questions = c1.slider("Number of questions", 3, 15, 5)
difficulty = c2.selectbox("Difficulty", ["Easy", "Medium", "Hard"])

if st.button("🎲 Generate Quiz"):
    if not content.strip():
        st.warning("Please provide a topic or notes first.")
    else:
        with st.spinner("🤖 Writing your quiz..."):
            try:
                raw = chat_completion(quiz_prompt(content, num_questions, difficulty), temperature=0.5)
                data = extract_json(raw)
                questions = validate_quiz_questions(data.get("questions", []))

                st.session_state["quiz_data"] = questions
                st.session_state["quiz_submitted"] = False
                st.session_state["quiz_answers"] = {}
            except (LLMError, JSONParseError) as exc:
                st.error(f"Couldn't generate the quiz: {exc}")

quiz = st.session_state.get("quiz_data")
if quiz:
    st.markdown("### 📝 Your Quiz")
    with st.form("quiz_form"):
        for i, q in enumerate(quiz):
            st.markdown(f"**Q{i + 1}. {q['question']}**")
            st.session_state["quiz_answers"][i] = st.radio(
                "Select one:", q["options"], key=f"q_{i}", label_visibility="collapsed"
            )
            st.write("")
        submitted = st.form_submit_button("✅ Submit Answers")

    if submitted:
        st.session_state["quiz_submitted"] = True

    if st.session_state.get("quiz_submitted"):
        score = 0
        for i, q in enumerate(quiz):
            selected = st.session_state["quiz_answers"].get(i)
            correct = q["options"][q["correct_index"]]
            is_correct = selected == correct
            score += int(is_correct)

            icon = "✅" if is_correct else "❌"
            render_card(
                f"{icon} <b>Q{i + 1}.</b> {q['question']}<br>"
                f"Your answer: {selected}<br>"
                f"Correct answer: <b>{correct}</b><br>"
                f"<i>{q.get('explanation', '')}</i>"
            )

        pct = round(100 * score / len(quiz))
        st.success(f"🏆 Score: {score}/{len(quiz)} ({pct}%)")

        st.session_state["quizzes_taken"] = st.session_state.get("quizzes_taken", 0) + 1
        st.session_state["best_score"] = max(st.session_state.get("best_score", 0), pct)

        st.download_button(
            "⬇️ Download quiz (.json)",
            quiz_to_json_bytes({"questions": quiz}),
            file_name="quiz.json",
        )
