"""Shared UI components & styling for Study Buddy pages."""
import streamlit as st

from config import THEME, APP_NAME, APP_ICON


def configure_page(title: str) -> None:
    """Must be the first Streamlit call on every page."""
    st.set_page_config(page_title=f"{title} · {APP_NAME}", page_icon=APP_ICON, layout="centered")
    _inject_base_css()


def _inject_base_css() -> None:
    st.markdown(
        f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
            html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
            .stApp {{ background: {THEME['bg']}; }}

            .hero {{
                background: linear-gradient(135deg, {THEME['primary_dark']}, {THEME['primary']});
                padding: 2rem; border-radius: 16px; text-align: center;
                color: white; margin-bottom: 1.5rem;
            }}
            .hero h1 {{ font-size: 2rem; font-weight: 700; margin-bottom: .25rem; }}
            .hero p {{ opacity: .9; margin: 0; }}

            .card {{
                background: white; border-radius: 14px; padding: 1.5rem;
                box-shadow: 0 4px 20px rgba(0,0,0,0.08);
                border-top: 4px solid {THEME['primary']};
                line-height: 1.7; color: {THEME['text']};
                margin-bottom: 1rem;
            }}

            .stButton > button {{
                background: linear-gradient(135deg, {THEME['primary']}, {THEME['primary_dark']}) !important;
                color: white !important; border: none !important; border-radius: 10px !important;
                padding: 0.6rem 1.6rem !important; font-weight: 600 !important; width: 100%;
            }}
            .stButton > button:hover {{
                transform: translateY(-1px) !important;
                box-shadow: 0 4px 14px rgba(37,99,235,0.4) !important;
            }}

            /* Pure-CSS flip flashcards — no JS, no Streamlit rerun on flip */
            .flip-card {{ background: transparent; width: 100%; height: 180px; perspective: 1000px; margin-bottom: 1rem; display: block; }}
            .flip-card-inner {{ position: relative; width: 100%; height: 100%; transition: transform .5s; transform-style: preserve-3d; }}
            .flip-card input {{ display: none; }}
            .flip-card input:checked ~ .flip-card-inner {{ transform: rotateY(180deg); }}
            .flip-card-front, .flip-card-back {{
                position: absolute; width: 100%; height: 100%; backface-visibility: hidden;
                border-radius: 14px; display: flex; align-items: center; justify-content: center;
                padding: 1rem; text-align: center; box-shadow: 0 4px 14px rgba(0,0,0,.08); cursor: pointer;
            }}
            .flip-card-front {{ background: white; border-top: 4px solid {THEME['primary']}; font-weight: 600; }}
            .flip-card-back {{
                background: linear-gradient(135deg, {THEME['primary_dark']}, {THEME['primary']});
                color: white; transform: rotateY(180deg); font-size: .9rem;
            }}

            #MainMenu, footer {{ visibility: hidden; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero(title: str, subtitle: str) -> None:
    st.markdown(f'<div class="hero"><h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)


def render_card(html: str) -> None:
    st.markdown(f'<div class="card">{html}</div>', unsafe_allow_html=True)


def flip_card_html(front: str, back: str) -> str:
    """Scoped via CSS sibling selectors — no unique ID needed per card."""
    return f"""
    <label class="flip-card">
        <input type="checkbox">
        <div class="flip-card-inner">
            <div class="flip-card-front">{front}</div>
            <div class="flip-card-back">{back}</div>
        </div>
    </label>
    """
