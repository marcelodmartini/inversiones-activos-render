import yfinance as yf
import requests
from deep_translator import GoogleTranslator
from config import FINNHUB_API_KEY, FMP_API_KEY
from helpers.score import es_bono_argentino, obtener_riesgo_pais, obtener_pais_ticker

def obtener_info_fundamental(ticker):
    es_bono = es_bono_argentino(ticker)
    resultado = {
        "Ticker": ticker, "Tipo": "Bono" if es_bono else "Acción",
        "País": None, "PEG Ratio": None, "P/E Ratio": None, "P/B Ratio": None,
        "ROE": None, "ROIC": None, "FCF Yield": None, "Debt/Equity": None,
        "EV/EBITDA": None, "Dividend Yield": None, "Beta": None,
        "Revenue Growth YoY": None, "% Subida a Máx": None,
        "Contexto": None, "Semáforo Riesgo": "ROJO",
        "VIX": None, "Riesgo País": None
    }

    # --- YFINANCE ---
    try:
        info = yf.Ticker(ticker).info
        resultado.update({
            "País": info.get("country"),
            "PEG Ratio": info.get("pegRatio"),
            "P/E Ratio": info.get("trailingPE"),
            "P/B Ratio": info.get("priceToBook"),
            "ROE": info.get("returnOnEquity"),
            "ROIC": info.get("returnOnAssets"),
            "Debt/Equity": info.get("debtToEquity"),
            "EV/EBITDA": info.get("enterpriseToEbitda"),
            "Dividend Yield": info.get("dividendYield"),
            "Beta": info.get("beta"),
            "Revenue Growth YoY": info.get("revenueGrowth"),
            "Contexto": info.get("longBusinessSummary")
        })

        # Calcular PEG si falta y growth > 0
        if resultado["PEG Ratio"] is None:
            pe = info.get("trailingPE")
            growth = info.get("earningsQuarterlyGrowth") or info.get("earningsGrowth")
            if isinstance(pe, (int, float)) and isinstance(growth, (int, float)) and growth > 0:
                resultado["PEG Ratio"] = round(pe / (growth * 100), 2)

        # Calcular FCF Yield si falta
        if resultado["FCF Yield"] is None:
            fcf = info.get("freeCashflow")
            mc = info.get("marketCap")
            if isinstance(fcf, (int, float)) and isinstance(mc, (int, float)) and mc > 0:
                resultado["FCF Yield"] = round(fcf / mc * 100, 2)

        # Subida a máximo
        price = info.get("currentPrice")
        high = info.get("fiftyTwoWeekHigh")
        if isinstance(price, (int, float)) and isinstance(high, (int, float)) and price > 0:
            resultado["% Subida a Máx"] = round((high - price) / price * 100, 2)

        # Semáforo por beta
        beta = resultado.get("Beta")
        if isinstance(beta, (int, float)):
            resultado["Semáforo Riesgo"] = (
                "VERDE" if beta <= 1 else
                "AMARILLO" if beta <= 1.5 else "ROJO"
            )

    except Exception as e:
        print(f"[yfinance] {ticker} -> {e}")

    # --- FINNHUB ---
    try:
        if FINNHUB_API_KEY:
            url = f"https://finnhub.io/api/v1/stock/metric?symbol={ticker}&metric=all&token={FINNHUB_API_KEY}"
            r = requests.get(url)
            if r.ok:
                data = r.json().get("metric", {})
                fcf_yield = data.get("freeCashFlowYieldAnnual")
                if isinstance(fcf_yield, (int, float)):
                    resultado["FCF Yield"] = fcf_yield
    except Exception as e:
        print(f"[finnhub] {ticker} -> {e}")

    # --- FMP ---
    try:
        if FMP_API_KEY:
            url = f"https://financialmodelingprep.com/api/v3/key-metrics-ttm/{ticker}?apikey={FMP_API_KEY}"
            r = requests.get(url)
            if r.ok and isinstance(r.json(), list) and r.json():
                data = r.json()[0]
                resultado.update({
                    "EV/EBITDA": data.get("evToEbitda") or resultado["EV/EBITDA"],
                    "Debt/Equity": data.get("debtEquityRatio") or resultado["Debt/Equity"],
                    "ROE": data.get("roe") or resultado["ROE"],
                    "ROIC": data.get("roic") or resultado["ROIC"],
                    "FCF Yield": data.get("freeCashFlowYield") or resultado["FCF Yield"],
                    "Revenue Growth YoY": data.get("revenueGrowth") or resultado["Revenue Growth YoY"]
                })
    except Exception as e:
        print(f"[fmp] {ticker} -> {e}")

    # --- TRADUCCIÓN ---
    try:
        if resultado.get("Contexto"):
            resultado["Contexto"] = GoogleTranslator(source='auto', target='es').translate(resultado["Contexto"])
    except Exception as e:
        print(f"[traducción] {ticker} -> {e}")

    # --- VIX ---
    try:
        vix = yf.Ticker("^VIX").history("1d")["Close"].iloc[-1]
        resultado["VIX"] = round(vix, 2)
    except Exception as e:
        print(f"[VIX] {ticker} -> {e}")

    # --- RIESGO PAÍS ---
    try:
        pais = obtener_pais_ticker(ticker)
        resultado["País"] = pais
        resultado["Riesgo País"] = obtener_riesgo_pais(pais)
    except Exception as e:
        print(f"[Riesgo País] {ticker} -> {e}")

    # --- COBERTURA ---
    claves = ["Dividend Yield", "Beta", "P/B Ratio"] if es_bono else [
        "PEG Ratio", "P/E Ratio", "P/B Ratio", "ROE", "FCF Yield",
        "Beta", "Revenue Growth YoY", "% Subida a Máx"
    ]
    completos = sum(1 for k in claves if resultado.get(k) is not None)
    resultado["Cobertura"] = f"{completos}/{len(claves)}"
    if completos == 0:
        resultado["Advertencia"] = "⚠️ Solo precio disponible, sin métricas fundamentales"

    return resultado
