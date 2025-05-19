import yfinance as yf
import requests
from deep_translator import GoogleTranslator
from config import FINNHUB_API_KEY, FMP_API_KEY
from helpers.score import es_bono_argentino, obtener_riesgo_pais, pais_por_ticker

def obtener_info_fundamental(ticker):
    es_bono = es_bono_argentino(ticker)
    resultado = {
        "Ticker": ticker,
        "País": None, "PEG Ratio": None, "P/E Ratio": None, "P/B Ratio": None,
        "ROE": None, "ROIC": None, "FCF Yield": None, "Debt/Equity": None,
        "EV/EBITDA": None, "Dividend Yield": None, "Beta": None,
        "Revenue Growth YoY": None, "% Subida a Máx": None,
        "Contexto": None, "Semáforo Riesgo": "ROJO", "Tipo": "Bono" if es_bono else "Acción",
        "VIX": None, "Riesgo País": None
    }

    try:
        tkr = yf.Ticker(ticker)
        if hasattr(tkr, "info") and isinstance(tkr.info, dict):
            info = tkr.info
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

            if resultado.get("PEG Ratio") is None:
                pe = info.get("trailingPE")
                growth = info.get("earningsQuarterlyGrowth") or info.get("earningsGrowth")
                if pe and growth and growth != 0:
                    resultado["PEG Ratio"] = round(pe / (growth * 100), 2)

            if resultado.get("FCF Yield") is None:
                fcf = info.get("freeCashflow")
                market_cap = info.get("marketCap")
                if fcf and market_cap and market_cap > 0:
                    resultado["FCF Yield"] = round(fcf / market_cap * 100, 2)

            price = info.get("currentPrice")
            high = info.get("fiftyTwoWeekHigh")
            if price and high and high > price:
                resultado["% Subida a Máx"] = round((high - price) / price * 100, 2)

            beta = resultado["Beta"] or 0
            resultado["Semáforo Riesgo"] = "ROJO" if beta > 1.5 else ("AMARILLO" if beta > 1 else "VERDE")

    except Exception as e:
        print(f"[yfinance] {ticker} -> {e}")

    try:
        if FINNHUB_API_KEY:
            r = requests.get(f"https://finnhub.io/api/v1/stock/metric?symbol={ticker}&metric=all&token={FINNHUB_API_KEY}")
            data = r.json().get("metric", {})
            resultado["FCF Yield"] = data.get("freeCashFlowYieldAnnual") or resultado["FCF Yield"]
    except Exception as e:
        print(f"[finnhub] {ticker} -> {e}")

    try:
        if FMP_API_KEY:
            r = requests.get(f"https://financialmodelingprep.com/api/v3/key-metrics-ttm/{ticker}?apikey={FMP_API_KEY}")
            if r.status_code == 200:
                data = r.json()[0] if isinstance(r.json(), list) and r.json() else {}
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

    if resultado.get("Contexto"):
        try:
            resultado["Contexto"] = GoogleTranslator(source='auto', target='es').translate(resultado["Contexto"])
        except Exception as e:
            print(f"[traducción] {ticker} -> {e}")

    try:
        vix = yf.Ticker("^VIX").history(period="1d")["Close"].iloc[-1]
        resultado["VIX"] = round(vix, 2)
    except Exception as e:
        print(f"[VIX] {ticker} -> {e}")
        resultado["VIX"] = None

    try:
        pais = pais_por_ticker.get(ticker.upper(), "default")
        resultado["Riesgo País"] = obtener_riesgo_pais(pais)
    except Exception as e:
        print(f"[Riesgo País] {ticker} -> {e}")
        resultado["Riesgo País"] = None

    indicadores_clave = [
        "PEG Ratio", "P/E Ratio", "P/B Ratio", "ROE", "FCF Yield",
        "Beta", "Revenue Growth YoY", "% Subida a Máx"
    ]
    completos = sum([1 for k in indicadores_clave if resultado.get(k) is not None])
    resultado["Cobertura"] = f"{completos}/{len(indicadores_clave)}"

    if resultado["Tipo"] == "Bono":
        indicadores_clave = ["Dividend Yield", "Beta", "P/B Ratio"]
        completos = sum([1 for k in indicadores_clave if resultado.get(k) is not None])
        resultado["Cobertura"] = f"{completos}/{len(indicadores_clave)}"

    if completos == 0:
        resultado["Advertencia"] = "⚠️ Solo precio disponible, sin métricas fundamentales"

    return resultado
