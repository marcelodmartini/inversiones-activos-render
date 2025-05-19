import re
import yfinance as yf
import tradingeconomics as te
from config import TRADINGECONOMICS_API_KEY

# Fallback si falla la API
riesgo_pais_por_pais = {
    "argentina": 1450,
    "brazil": 260,
    "mexico": 320,
    "chile": 170,
    "colombia": 370,
    "usa": 50,
    "china": 70,
    "india": 90,
    "europa": 80,
    "default": 400
}

# Ticker base → país
pais_por_ticker = {
    "SUPV": "argentina", "BBAR": "argentina", "PAMP": "argentina",
    "YPFD": "argentina", "TGSU2": "argentina", "FALABELLA": "chile",
    "CEMEXCPO": "mexico", "EC": "colombia", "EMBR3": "brazil"
}

# Tickers locales a Yahoo Finance
ticker_map = {
    "YPFD": "YPF.BA", "TGSU2": "TGSU2.BA", "MIRG": "MIRG.BA", "VISTA": "VIST",
    "FALABELLA": "FALABELLA.CL", "CEMEXCPO": "CEMEXCPO.MX", "OM:STIL": "STIL.ST", "HLSE:ETTE": "ETTE.HE"
}

def es_bono_argentino(ticker):
    return bool(re.match(r"^(AL|GD|TX|TV|AE|TB)[0-9]+[D]?$", ticker.upper()))

def obtener_riesgo_pais(pais="argentina"):
    pais = pais.lower()
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
        if not df.empty:
            valor = round(float(df.iloc[0]["Value"]))
            print(f"[TradingEconomics] ✅ Riesgo país de {pais}: {valor}")
            return valor
        else:
            print(f"[TradingEconomics] ⚠️ No se encontró riesgo país para {pais}, usando fallback")
    except Exception as e:
        print(f"[TradingEconomics] ❌ Error al consultar riesgo país para {pais}: {e}")
    return riesgo_pais_por_pais.get(pais, riesgo_pais_por_pais["default"])

def obtener_contexto_mundial(ticker):
    try:
        vix = yf.Ticker("^VIX").history(period="1d")['Close'].iloc[-1]
        pais = pais_por_ticker.get(ticker.upper(), "default")
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
        beta = resultado.get("Beta", 0)
        debt_equity = resultado.get("Debt/Equity", 999)
        ev_ebitda = resultado.get("EV/EBITDA", 999)
        roe = resultado.get("ROE", 0)
        roic = resultado.get("ROIC", 0)
        peg = resultado.get("PEG Ratio", 999)
        fcf_yield = resultado.get("FCF Yield", 0)
        pe = resultado.get("P/E Ratio", 999)
        pb = resultado.get("P/B Ratio", 999)
        dividend_yield = resultado.get("Dividend Yield", 0)
        upside = resultado.get("% Subida a Máx", 0)
        revenue_growth = resultado.get("Revenue Growth YoY", 0)

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
        if dividend_yield and dividend_yield > 0.02: score += 1
        if upside > 40: score += 1
        if revenue_growth > 15: score += 1

        # Contexto mundial (VIX + riesgo país)
        contexto, score_contexto = obtener_contexto_mundial(ticker)
        resultado["Contexto Global"] = contexto
        score += score_contexto

        # Score final
        if score >= 12: return "⭐⭐⭐⭐⭐ (5/5 - Excelente)", 5
        elif score >= 9: return "⭐⭐⭐⭐ (4/5 - Muy Bueno)", 4
        elif score >= 6: return "⭐⭐⭐ (3/5 - Aceptable)", 3
        elif score >= 4: return "⭐⭐ (2/5 - Riesgoso)", 2
        else: return "⭐ (1/5 - Débil)", 1

    except Exception as e:
        print(f"[Score] ❌ Error calculando score para {resultado.get('Ticker')}: {e}")
        return "N/A", 0
