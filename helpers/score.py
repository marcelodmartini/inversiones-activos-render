import re
import yfinance as yf
import tradingeconomics as te
import requests
import pandas as pd
from config import TRADINGECONOMICS_API_KEY

# --- Fallback por país ---
riesgo_pais_por_pais = {
    "argentina": 1450, "brazil": 260, "mexico": 320,
    "chile": 170, "colombia": 370, "usa": 50,
    "china": 70, "india": 90, "europe": 80,
    "default": 400
}

# --- Mapeo países YF → TE
mapa_paises_yf = {
    "united states": "usa", "united kingdom": "europe",
    "germany": "europe", "france": "europe", "italy": "europe",
    "spain": "europe"
}

# --- Ticker locales mapeados
ticker_map = {
    "YPFD": "YPF.BA", "TGSU2": "TGSU2.BA", "MIRG": "MIRG.BA", "VISTA": "VIST",
    "FALABELLA": "FALABELLA.CL", "CEMEXCPO": "CEMEXCPO.MX", "OM:STIL": "STIL.ST", "HLSE:ETTE": "ETTE.HE"
}

paises_disponibles_te = set()

# --- RSI y MACD ---
def calcular_rsi(df, window=14):
    delta = df['Close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calcular_macd(df, short=12, long=26, signal=9):
    ema_short = df['Close'].ewm(span=short, adjust=False).mean()
    ema_long = df['Close'].ewm(span=long, adjust=False).mean()
    macd = ema_short - ema_long
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    return macd, signal_line

def agregar_proyecciones_forward(resultado, ticker_map):
    ticker = resultado.get("Ticker", "")
    ticker_ = ticker_map.get(ticker.upper(), ticker.upper())

    try:
        info = yf.Ticker(ticker_).info
        forward_eps = info.get("forwardEps")
        forward_rev_growth = info.get("revenueGrowth")
        sector = info.get("sector")

        if forward_eps is not None:
            resultado["Forward EPS"] = forward_eps

        if forward_rev_growth is not None:
            forward_pct = forward_rev_growth * 100
            resultado["Forward Revenue Growth"] = forward_pct
            if forward_pct >= 15:
                resultado["Crecimiento Futuro"] = "🟢 Alto"
            elif forward_pct >= 5:
                resultado["Crecimiento Futuro"] = "🟡 Moderado"
            else:
                resultado["Crecimiento Futuro"] = "🔴 Bajo"
        else:
            resultado["Crecimiento Futuro"] = "🔴 Bajo"

        if sector:
            resultado["Sector"] = sector

    except Exception:
        resultado["Forward EPS"] = None
        resultado["Forward Revenue Growth"] = None
        resultado["Crecimiento Futuro"] = "🔴 Bajo"

    return resultado

# --- Funciones core ---
def cargar_paises_te():
    global paises_disponibles_te
    try:
        te.login(TRADINGECONOMICS_API_KEY)
        url = f"https://api.tradingeconomics.com/country?c={TRADINGECONOMICS_API_KEY}"
        r = requests.get(url)
        if r.status_code == 200:
            paises_disponibles_te = {p["country"].lower() for p in r.json()}
        elif r.status_code == 403:
            paises_disponibles_te = set()
    except:
        paises_disponibles_te = set()

def obtener_pais_ticker(ticker):
    ticker_ = ticker_map.get(ticker.upper(), ticker.upper())
    try:
        info = yf.Ticker(ticker_).info
        pais = info.get("country", "").lower()
        return mapa_paises_yf.get(pais, pais) or "default"
    except:
        return "default"

def obtener_riesgo_pais(pais):
    if not paises_disponibles_te:
        cargar_paises_te()
    pais = pais.lower()
    if pais not in paises_disponibles_te:
        return riesgo_pais_por_pais.get(pais, riesgo_pais_por_pais["default"])
    try:
        df = te.getIndicatorData(country=pais, output_type="df")
        df = df[df["Category"].str.lower().str.contains("bond|risk")]
        if not df.empty:
            return round(float(df.iloc[0]["Value"]))
    except:
        pass
    return riesgo_pais_por_pais.get(pais, riesgo_pais_por_pais["default"])

def obtener_contexto_mundial(ticker):
    try:
        vix = yf.Ticker("^VIX").history("5d")["Close"].dropna().iloc[-1]
        pais = obtener_pais_ticker(ticker)
        riesgo = obtener_riesgo_pais(pais)
        if vix < 18 and riesgo < 500:
            return "Contexto Global: MUY FAVORABLE", 2
        elif vix < 25 and riesgo < 1000:
            return "Contexto Global: MODERADO", 1
        else:
            return "Contexto Global: ADVERSO", 0
    except:
        return "Contexto Global: DESCONOCIDO", 0

def es_bono_argentino(ticker):
    return bool(re.match(r"^(AL|GD|TX|TV|AE|TB)[0-9]+[D]?$", ticker.upper()))

def calcular_score(resultado):
    if resultado.get("Tipo") == "Bono":
        return "N/A", 0

    score = 0
    ticker = resultado.get("Ticker", "")

    # Métricas financieras clásicas
    if (b := resultado.get("Beta")) is not None and b <= 1: score += 1
    if (de := resultado.get("Debt/Equity")) and 0 < de < 1: score += 1
    if (ev := resultado.get("EV/EBITDA")) and 0 < ev < 15: score += 1
    if (roe := resultado.get("ROE")) and roe > 0.10: score += 1
    if (roic := resultado.get("ROIC")) and roic > 0.08: score += 1
    if (peg := resultado.get("PEG Ratio")) and 0 < peg < 1.5: score += 1
    if (fcf := resultado.get("FCF Yield")):
        if fcf > 0: score += 1
        if fcf > 5: score += 1
    if (pe := resultado.get("P/E Ratio")) and 0 < pe < 20: score += 1
    if (pb := resultado.get("P/B Ratio")) and 0 < pb < 3: score += 1
    if (div := resultado.get("Dividend Yield")) and div > 0.02: score += 1
    if (up := resultado.get("% Subida a Máx")) and up > 40: score += 1
    if (rev := resultado.get("Revenue Growth YoY")) and rev > 15: score += 1

    # Proyecciones futuras
    if (eps_fwd := resultado.get("Forward EPS")):
        if eps_fwd > 0: score += 1
        elif eps_fwd < 0: score -= 1
    if (rev_fwd := resultado.get("Forward Revenue Growth")):
        if rev_fwd > 10: score += 1
        elif rev_fwd < 0: score -= 1

    # Técnicos (RSI y MACD)
    try:
        hist = resultado.get("Hist")
        if isinstance(hist, dict):
            df = pd.DataFrame(hist)
            df["RSI"] = calcular_rsi(df)
            df["MACD"], df["Signal"] = calcular_macd(df)
            rsi = df["RSI"].dropna().iloc[-1]
            macd = df["MACD"].iloc[-1]
            signal = df["Signal"].iloc[-1]
            if 30 < rsi < 70: score += 1
            if macd > signal: score += 1
    except:
        pass

    # Penalizaciones por outliers
    if (pe := resultado.get("P/E Ratio")) and pe > 60: score -= 1
    if (roe := resultado.get("ROE")) and roe < 0: score -= 1

    # Sectores estratégicos
    sector = resultado.get("Sector", "").lower()
    if any(x in sector for x in ["ai", "inteligencia", "energ", "defens"]): score += 1

    # Contexto global
    contexto, bonus = obtener_contexto_mundial(ticker)
    resultado["Contexto Global"] = contexto
    score += bonus

    # Escala final
    if score >= 13: return "⭐⭐⭐⭐⭐ (5/5 - Excelente)", 5
    elif score >= 10: return "⭐⭐⭐⭐ (4/5 - Muy Bueno)", 4
    elif score >= 7: return "⭐⭐⭐ (3/5 - Aceptable)", 3
    elif score >= 4: return "⭐⭐ (2/5 - Riesgoso)", 2
    else: return "⭐ (1/5 - Débil)", 1
