import requests
import json
import os
import time
import pandas as pd
import streamlit as st

CACHE_PATH = "/tmp/byma_cache"
CACHE_TTL = 600  # segundos (10 minutos)

os.makedirs(CACHE_PATH, exist_ok=True)

def log_debug(msg):
    print(msg)
    try:
        if "debug_logs" in st.session_state:
            st.session_state.debug_logs.append(msg)
    except:
        pass

def obtener_cache(symbol):
    path = os.path.join(CACHE_PATH, f"{symbol.upper()}.json")
    if os.path.exists(path):
        mtime = os.path.getmtime(path)
        if time.time() - mtime < CACHE_TTL:
            with open(path, "r") as f:
                return json.load(f)
    return None

def guardar_cache(symbol, data):
    path = os.path.join(CACHE_PATH, f"{symbol.upper()}.json")
    with open(path, "w") as f:
        json.dump(data, f)

def obtener_token_byma():
    try:
        log_debug("[BYMA Auth] Obteniendo token de acceso...")
        url = "https://api.byma.com.ar/token"
        client_id = st.secrets["byma"]["client_id"]
        client_secret = st.secrets["byma"]["client_secret"]

        payload = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        r = requests.post(url, data=payload, headers=headers, timeout=10)
        r.raise_for_status()
        token_data = r.json()
        return token_data.get("access_token")
    except Exception as e:
        log_debug(f"[BYMA Auth] Error al obtener token: {e}")
        return None

def obtener_precio_bono_byma(symbol):
    log_debug(f"[BYMA] 🔍 Buscando datos para {symbol} desde API privada BYMA")
    try:
        cached = obtener_cache(symbol)
        if cached:
            log_debug(f"[BYMA] Usando cache local para {symbol}")
            return cached

        token = obtener_token_byma()
        if not token:
            raise Exception("Token no disponible")

        # 🔄 Endpoint correcto validado en la documentación oficial
        url = f"https://api.byma.com.ar/v1/marketdata/instruments/detail?symbol={symbol.upper()}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }

        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()

        precios = data.get("price") or {}
        last_price = float(precios.get("last") or 0)
        min_price = float(precios.get("low") or 0)
        max_price = float(precios.get("high") or 0)
        subida = round((max_price - last_price) / last_price * 100, 2) if last_price > 0 else None

        result = {
            "Ticker": symbol.upper(),
            "Actual": round(last_price, 2),
            "Mínimo": round(min_price, 2),
            "Máximo": round(max_price, 2),
            "% Subida a Máx": subida,
            "Fuente": "BYMA API privada",
            "Hist": hist  # 👉 agregado para el gráfico histórico
        }

        guardar_cache(symbol, result)
        return result

    except requests.exceptions.RequestException as e:
        log_debug(f"[BYMA] Error de red para {symbol}: {e}")
        if hasattr(e, "response") and e.response is not None:
            log_debug(f"[BYMA] Status: {e.response.status_code} - Cuerpo: {e.response.text}")
        return None
    except Exception as e:
        log_debug(f"[BYMA] Error inesperado para {symbol}: {e}")
        return None
