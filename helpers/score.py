import re
import yfinance as yf
import tradingeconomics as te
from config import TRADINGECONOMICS_API_KEY

# Fallback si falla la API o el país no es permitido
riesgo_pais_por_pais = {
    "argentina": 1450,
    "brazil": 260,
    "mexico": 320,
    "chile": 170,
    "colombia": 370,
    "usa": 50,
    "china": 70,
    "india": 90,
    "europe": 80,
    "default": 400
}

# Para corregir nombres según lo que devuelve yfinance
mapa_paises_yf = {
    "united states": "usa",
    "united kingdom": "europe",
    "germany": "europe",
    "france": "europe",
    "italy": "europe",
    "spain": "europe"
}

# Tickers locales → Yahoo Finance
ticker_map = {
    "YPFD": "YPF.BA", "TGSU2": "TGSU2.BA", "MIRG": "MIRG.BA", "VISTA": "VIST",
    "FALABELLA": "FALABELLA.CL", "CEMEXCPO": "CEMEXCPO.MX", "OM:STIL": "STIL.ST", "HLSE:ETTE": "ETTE.HE"
}

def es_bono_argentino(ticker):
    return bool(re.match(r"^(AL|GD|TX|TV|AE|TB)[0-9]+[D]?$", ticker.upper()))

def obtener_pais_ticker(ticker):
    ticker_ = ticker_map.get(ticker.upper(), ticker.upper())
    try:
        info = yf.Ticker(ticker_).info
        pais = info.get("country", "").lower()
        pais = mapa_paises_yf.get(pais, pais)
        if not pais:
            raise ValueError("No se pudo detectar país del ticker")
        return pais
    except Exception as e:
        print(f"[YFinance] ⚠️ No se pudo obtener país para {ticker}: {e}")
        return "default"

def obtener_riesgo_pais(pais="argentina"):
    pais = pais.lower()
    if pais == "default":
        print(f"[TradingEconomics] ⛔ País 'default' no es permitido para usuarios free. Usando fallback")
        return riesgo_pais_por_pais["default"]
    if not TRADINGECONOMICS_API_KEY:
        print(f"[Riesgo País] ❌ No API key configurada. Usando valor por defecto para {pais}")
        return riesgo_pais_por_pais.get(pais, riesgo_pais_por_pais["default"])
    try:
        print(f"[TradingEconomics] 🔑 Login con API Key...")
        te.login(TRADINGECONOMICS_API_KEY)
        print(f"[TradingEconomics] 🌎 Buscando riesgo país para: {pais}")
        df = te.getIndicatorData(country=pais, output_type="df")
        print(f"[TradingEconomics] 🔍 Filtrando indicadores 'bond' o 'risk'")
        df = df[df["Category"].str.lower().str.contains("bond|risk")]
        if not df.empty and "Value" in df.columns:
            valor = round(float(df.iloc[0]["Value"]))
            print(f"[TradingEconomics] ✅ Riesgo país de {pais}: {valor}")
            return valor
    except Exception as e:
        print(f"[TradingEconomics] ❌ Error al consultar riesgo país para {pais}: {e}")
    return riesgo_pais_por_pais.get(pais, riesgo_pais_por_pais["default"])

def obtener_contexto_mundial(ticker):
    try:
        vix = yf.Ticker("^VIX").history(period="1d")["Close"].iloc[-1]
        pais = obtener_pais_ticker(ticker)
        riesgo_pais = obtener_riesgo_pais(pais)

        if vix < 18 and riesgo_pais < 500:
            return "Contexto Global: MUY FAVORABLE", 2
        elif vix < 25 and riesgo_pais < 1000:
            return "Contexto Global: MODERADO", 1
        else:
            return "Contexto Global: ADVERSO", 0
    except Exception as e:
        print(f"[Contexto Mundial] ❌ Error al obtener VIX o riesgo país: {e}")
        return "Contexto Global: DESCONOCIDO", 0

def calcular_score(resultado):
    if resultado.get("Tipo") == "Bono":
        return "N/A", 0

    score = 0
    try:
        ticker = resultado.get("Ticker", "")

        # Métricas fundamentales
        beta = resultado.get("Beta") or 0
        debt_equity = resultado.get("Debt/Equity") or 999
        ev_ebitda = resultado.get("EV/EBITDA") or 999
        roe = resultado.get("ROE") or 0
        roic = resultado.get("ROIC") or 0
        peg = resultado.get("PEG Ratio") or 999
        fcf_yield = resultado.get("FCF Yield") or 0
        pe = resultado.get("P/E Ratio") or 999
        pb = resultado.get("P/B Ratio") or 999
        dividend_yield = resultado.get("Dividend Yield") or 0
        upside = resultado.get("% Subida a Máx") or 0
        revenue_growth = resultado.get("Revenue Growth YoY") or 0

        # Indicadores clave
        if beta <= 1: score += 1
        if debt_equity < 1: score += 1
        if ev_ebitda < 15: score += 1
        if roe > 0.10: score += 1
        if roic > 0.08: score += 1
        if peg < 1.5: score += 1
        if fcf_yield > 0: score += 1
        if fcf_yield > 5: score += 1
        if pe < 20: score += 1
        if pb < 3: score += 1
        if dividend_yield > 0.02: score += 1
        if upside > 40: score += 1
        if revenue_growth > 15: score += 1

        contexto, score_contexto = obtener_contexto_mundial(ticker)
        resultado["Contexto Global"] = contexto
        score += score_contexto

        if score >= 12: return "⭐⭐⭐⭐⭐ (5/5 - Excelente)", 5
        elif score >= 9: return "⭐⭐⭐⭐ (4/5 - Muy Bueno)", 4
        elif score >= 6: return "⭐⭐⭐ (3/5 - Aceptable)", 3
        elif score >= 4: return "⭐⭐ (2/5 - Riesgoso)", 2
        else: return "⭐ (1/5 - Débil)", 1

    except Exception as e:
        print(f"[Score] ❌ Error calculando score para {resultado.get('Ticker')}: {e}")
        return "N/A", 0
