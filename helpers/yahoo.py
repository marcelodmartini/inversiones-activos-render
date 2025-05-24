import yfinance as yf
import pandas as pd
from datetime import datetime
import warnings

def analizar_con_yfinance(ticker, fecha_inicio, fecha_fin):
    try:
        if isinstance(fecha_inicio, datetime):
            fecha_inicio = fecha_inicio.strftime('%Y-%m-%d')
        if isinstance(fecha_fin, datetime):
            fecha_fin = fecha_fin.strftime('%Y-%m-%d')

        data = yf.Ticker(ticker)
        hist = data.history(start=fecha_inicio, end=fecha_fin)

        if hist.empty or 'Close' not in hist.columns:
            return None

        min_price = hist['Close'].min()
        max_price = hist['Close'].max()
        current_price = hist['Close'].iloc[-1]

        if current_price == 0:
            subida = 0
        else:
            subida = (max_price - current_price) / current_price * 100

        return {
            "Ticker": ticker,
            "Fuente": "Yahoo Finance",
            "Mínimo": round(min_price, 2),
            "Máximo": round(max_price, 2),
            "Actual": round(current_price, 2),
            "% Subida a Máx": round(subida, 2),
            "Hist": hist
        }

    except Exception as e:
        print(f"[Yahoo Finance] {ticker}: {e}")
        warnings.warn(f"Yahoo Finance falló para {ticker} - {e}")
        return None
