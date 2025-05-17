import yfinance as yf
import pandas as pd
from datetime import datetime, time
import warnings

def analizar_con_yfinance(ticker, fecha_inicio, fecha_fin):
    global errores_conexion
    try:
        data = yf.Ticker(ticker)
        hist = data.history(start=fecha_inicio, end=fecha_fin)
        if hist.empty:
            return None
        min_price = hist['Close'].min()
        max_price = hist['Close'].max()
        current_price = hist['Close'].iloc[-1]
        subida = (max_price - current_price) / current_price * 100
        return {
            "Ticker": ticker,
            "Fuente": "Yahoo Finance",
            "Mínimo": round(min_price, 2),
            "Máximo": round(max_price, 2),
            "Actual": round(current_price, 2),
            "% Subida a Máx": round(subida, 2),
            "Hist": hist  # 👉 agregado para el gráfico histórico
        }
    except Exception as e:
        print(f"[Yahoo Finance] {ticker}: {e}")
        print(f"[ERROR] Yahoo Finance falló para {ticker} - {e}")
        warnings.warn(f"DEBUG: Yahoo Finance falló para {ticker} - {e}")
        return None
