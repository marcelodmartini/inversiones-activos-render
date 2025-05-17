import streamlit as st
import os

# Función para obtener secretos desde st.secrets o variables de entorno (Render)
def get_secret(name, default=""):
    if name in st.secrets:
        return st.secrets[name]
    return os.getenv(name, default)

ES_CLOUD = os.environ.get("STREAMLIT_SERVER_HEADLESS", "") == "1"

ALPHA_VANTAGE_API_KEY = get_secret("ALPHA_VANTAGE_API_KEY")
FINNHUB_API_KEY = get_secret("FINNHUB_API_KEY")
FMP_API_KEY = get_secret("FMP_API_KEY")