import streamlit as st
import os

try:
    FINNHUB_API_KEY = st.secrets["FINNHUB_API_KEY"]
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")