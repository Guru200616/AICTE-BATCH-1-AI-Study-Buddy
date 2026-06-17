"""Summarize Notes page."""
import streamlit as st

from core.llm_client import chat_completion, LLMError
from core.prompts import summarize_prompt, map_chunk_prompt, reduce_summaries_prompt
from utils.ui import configure_page, render_hero, render_card
from utils.file_utils import extract_text_from_upload, chunk_text
from config import MAX_INPUT_CHARS, DIRECT_SUMMARY_THRESHOLD

configure_page("Summarize Notes")
render_hero("📝 Summarize Notes", "Paste your notes or upload a file — get a clean summary in seconds.")

source = st.radio("Input method", ["Paste text", "Upload file (.txt / .pdf)"], horizontal=True)

text = ""
if source == "Paste text":
    text = st.text_area("Paste your notes", height=220, max_chars=MAX_INPUT_CHARS)
else:
    uploaded = st.file_uploader("Upload notes", type=["txt", "pdf"])
    if uploaded:
        try:
            text = extract_text_from_upload(uploaded)
            st.success(f"Extracted {len(text):,} characters from {uploaded.name}.")
        except ValueError as exc:
            st.error(str(exc))

c1, c2, c3 = st.columns(3)
length = c1.selectbox("Length", ["Short", "Medium", "Detailed"])
fmt = c2.selectbox("Format", ["Bullet points", "Paragraph", "Cornell notes"])
highlight = c3.checkbox("Highlight key terms", value=True)

if st.button("📋 Summarize"):
    if not text.strip():
        st.warning("Please provide some text to summarize.")
    else:
        try:
            with st.spinner("🤖 Reading through your notes..."):
                if len(text) <= DIRECT_SUMMARY_THRESHOLD:
                    summary = chat_completion(summarize_prompt(text, length, fmt, highlight))
                else:
                    # Long-document path: map (summarize each chunk) -> reduce (merge).
                    chunks = chunk_text(text)
                    partials = [chat_completion(map_chunk_prompt(c)) for c in chunks]
                    combined = "\n\n".join(partials)
                    summary = chat_completion(reduce_summaries_prompt(combined, length, fmt))

            st.session_state["last_summary"] = summary
        except LLMError as exc:
            st.error(str(exc))

if st.session_state.get("last_summary"):
    st.markdown("### 🧾 Summary")
    render_card(st.session_state["last_summary"].replace("\n", "<br>"))

    st.download_button(
        "⬇️ Download summary (.txt)",
        st.session_state["last_summary"],
        file_name="summary.txt",
    )

    b1, b2 = st.columns(2)
    with b1:
        if st.button("🧩 Quiz me on this", key="quiz_from_summary"):
            st.session_state["seed_content"] = st.session_state["last_summary"]
            st.switch_page("pages/3_Generate_Quiz.py")
    with b2:
        if st.button("🃏 Make flashcards", key="cards_from_summary"):
            st.session_state["seed_content"] = st.session_state["last_summary"]
            st.switch_page("pages/4_Flashcards.py")
