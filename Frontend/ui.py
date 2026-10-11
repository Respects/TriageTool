import streamlit as st
from config import PRIORITY_STYLE, STATUS_STYLE, DEFAULT_STYLE

def pill(text, fg, bg, size="0.8rem"):
    return (f"<span style='background:{bg};color:{fg};padding:2px 10px;"
            f"border-radius:12px;font-size:{size};font-weight:600'>{text}</span>")

def priority_pill(priority, size="0.8rem"):
    fg, bg = PRIORITY_STYLE.get(priority, DEFAULT_STYLE)
    return pill(priority or "Review", fg, bg, size)

def status_pill(status):
    fg, bg = STATUS_STYLE.get(status, DEFAULT_STYLE)
    return pill(status or "—", fg, bg)

def field(label, value):
    st.markdown(
        f"<div style='opacity:0.6;font-size:0.75rem;text-transform:uppercase;"
        f"letter-spacing:0.04em'>{label}</div>"
        f"<div style='font-size:0.95rem;margin-bottom:0.6rem'>"
        f"{value if value not in (None, '') else '—'}</div>",
        unsafe_allow_html=True,
    )