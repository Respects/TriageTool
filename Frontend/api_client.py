import streamlit as st
import httpx
from config import API_BASE


@st.cache_data(ttl=60, show_spinner=False)
def load_cases():
    r = httpx.get(f"{API_BASE}/cases", timeout=10.0)
    r.raise_for_status()
    return r.json()


def update_status(case_id, status):
    r = httpx.patch(f"{API_BASE}/cases/{case_id}/status", json={"status": status}, timeout=10.0)
    r.raise_for_status()
    load_cases.clear()
    return r.json()