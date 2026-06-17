"""Flashcards page."""
import streamlit as st

from core.llm_client import chat_completion, LLMError
from core.prompts import flashcards_prompt
from core.json_utils import extract_json, JSONParseError
from core.validators import validate_flashcards
from utils.ui import configure_page, render_hero, flip_card_html
from utils.export_utils import flashcards_to_csv, flashcards_to_anki_tsv
from config import MAX_INPUT_CHARS

configure_page("Flashcards")
render_hero("🃏 Flashcards", "Auto-generate flip flashcards from any topic or notes.")

seeded = st.session_state.pop("seed_content", None)
if seeded:
    st.info("Using content carried over from a previous page. Edit below if needed.")

content = st.text_area(
    "Topic or notes",
    value=seeded or "",
    height=160,
    max_chars=MAX_INPUT_CHARS,
    placeholder="e.g. Cell biology terms, or paste your notes...",
)

num_cards = st.slider("Number of flashcards", 5, 20, 10)

if st.button("🪄 Generate Flashcards"):
    if not content.strip():
        st.warning("Please provide a topic or notes first.")
    else:
        with st.spinner("🤖 Building your flashcards..."):
            try:
                raw = chat_completion(flashcards_prompt(content, num_cards), temperature=0.5)
                data = extract_json(raw)
                cards = validate_flashcards(data.get("flashcards", []))
                st.session_state["flashcards"] = cards
            except (LLMError, JSONParseError) as exc:
                st.error(f"Couldn't generate flashcards: {exc}")

cards = st.session_state.get("flashcards")
if cards:
    st.markdown(f"### 🗂️ {len(cards)} Flashcards — click a card to flip")
    cols = st.columns(2)
    for i, card in enumerate(cards):
        with cols[i % 2]:
            st.markdown(
                flip_card_html(
                    front=f"<b>{card.get('term', '')}</b>",
                    back=f"{card.get('definition', '')}<br><i>{card.get('hint', '')}</i>",
                ),
                unsafe_allow_html=True,
            )

    d1, d2 = st.columns(2)
    d1.download_button(
        "⬇️ Download CSV", flashcards_to_csv(cards), file_name="flashcards.csv", mime="text/csv"
    )
    d2.download_button(
        "⬇️ Download Anki (.tsv)",
        flashcards_to_anki_tsv(cards),
        file_name="flashcards_anki.tsv",
        mime="text/tab-separated-values",
    )
