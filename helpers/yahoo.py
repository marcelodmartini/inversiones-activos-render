import yfinance as yf
import pandas as pd
from datetime import datetime
import warnings

def analizar_con_yfinance(ticker, fecha_inicio, fecha_fin):
    try:
        # Asegurar formatos de fecha tipo string (ISO 8601)
        if isinstance(fecha_inicio, datetime):
            fecha_inicio = fecha_inicio.strftime('%Y-%m-%d')
        if isinstance(fecha_fin, datetime):
            fecha_fin = fecha_fin.strftime('%Y-%m-%d')

        # Obtener datos históricos
        data = yf.Ticker(ticker)
        hist = data.history(start=fecha_inicio, end=fecha_fin)

        if hist.empty or 'Close' not in hist.columns:
            warnings.warn(f"No hay datos históricos válidos para {ticker} en Yahoo Finance.")
            return None

        # Asegurar índice tipo datetime
        if not pd.api.types.is_datetime64_any_dtype(hist.index):
            hist.index = pd.to_datetime(hist.index)

        min_price = hist['Close'].min()
        max_price = hist['Close'].max()
        current_price = hist['Close'].iloc[-1]

        # Validación de precio actual para evitar división por cero
        if not isinstance(current_price, (int, float)) or current_price <= 0:
            subida = None
        else:
            subida = (max_price - current_price) / current_price * 100

        return {
            "Ticker": ticker,
            "Fuente": "Yahoo Finance",
            "Mínimo": round(min_price, 2) if pd.notna(min_price) else None,
            "Máximo": round(max_price, 2) if pd.notna(max_price) else None,
            "Actual": round(current_price, 2) if pd.notna(current_price) else None,
            "% Subida a Máx": round(subida, 2) if subida is not None else None,
            "Hist": hist
        }

    except Exception as e:
        print(f"[Yahoo Finance] {ticker}: {e}")
        warnings.warn(f"Yahoo Finance falló para {ticker} - {e}")
        return None
