import streamlit as st
import os

def get_secret(name, default=""):
    try:
        return st.secrets[name]
    except Exception:
        return os.getenv(name, default)

ES_CLOUD = os.environ.get("STREAMLIT_SERVER_HEADLESS", "") == "1"

ALPHA_VANTAGE_API_KEY = get_secret("ALPHA_VANTAGE_API_KEY")
FINNHUB_API_KEY = get_secret("FINNHUB_API_KEY")
FMP_API_KEY = get_secret("FMP_API_KEY")
OPENAI_API_KEY = get_secret("OPENAI_API_KEY")
