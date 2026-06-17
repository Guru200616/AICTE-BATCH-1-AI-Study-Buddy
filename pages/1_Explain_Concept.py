"""Explain Concept page."""
import streamlit as st

from core.llm_client import chat_completion, LLMError
from core.prompts import explain_prompt
from utils.ui import configure_page, render_hero, render_card
from config import MAX_INPUT_CHARS

configure_page("Explain Concept")
render_hero("📘 Explain a Concept", "Get a clear, level-appropriate explanation — instantly.")

topic = st.text_area(
    "What do you want explained?",
    height=140,
    placeholder="e.g. Explain how TCP handshakes work, or 'What is Newton's Third Law?'",
    max_chars=MAX_INPUT_CHARS,
)

c1, c2 = st.columns(2)
level = c1.selectbox("Explain for level", ["Beginner", "Intermediate", "Advanced", "Exam Cram"])
style = c2.selectbox(
    "Explanation style",
    ["Simple analogy", "Step-by-step breakdown", "Real-world example", "Exam-focused (key points)"],
)

if st.button("✨ Explain This"):
    if not topic.strip():
        st.warning("Please enter a topic or question first.")
    else:
        with st.spinner("🤖 Thinking through the explanation..."):
            try:
                result = chat_completion(explain_prompt(topic, level, style))
                st.session_state["last_explanation"] = result
                st.session_state["last_topic"] = topic
            except LLMError as exc:
                st.error(str(exc))

if st.session_state.get("last_explanation"):
    st.markdown("### 📖 Explanation")
    render_card(st.session_state["last_explanation"].replace("\n", "<br>"))

    b1, b2 = st.columns(2)
    with b1:
        if st.button("🧩 Quiz me on this"):
            st.session_state["seed_content"] = st.session_state["last_explanation"]
            st.switch_page("pages/3_Generate_Quiz.py")
    with b2:
        if st.button("🃏 Make flashcards from this"):
            st.session_state["seed_content"] = st.session_state["last_explanation"]
            st.switch_page("pages/4_Flashcards.py")
