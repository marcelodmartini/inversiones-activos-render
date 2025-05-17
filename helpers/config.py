import streamlit as st
import os

ES_CLOUD = os.environ.get("STREAMLIT_SERVER_HEADLESS", "") == "1"
ALPHA_VANTAGE_API_KEY = st.secrets.get("ALPHA_VANTAGE_API_KEY", "")
FINNHUB_API_KEY = st.secrets.get("FINNHUB_API_KEY", "")
FMP_API_KEY = st.secrets.get("FMP_API_KEY", "")
