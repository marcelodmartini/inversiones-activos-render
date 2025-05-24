import re
import yfinance as yf
import tradingeconomics as te
import requests
import pandas as pd
import numpy as np
import os
import joblib
from datetime import datetime
from config import TRADINGECONOMICS_API_KEY

# --- Fallback por país ---
riesgo_pais_por_pais = {
    "argentina": 1450, "brazil": 260, "mexico": 320,
    "chile": 170, "colombia": 370, "usa": 50,
    "china": 70, "india": 90, "europe": 80,
    "default": 400
}

# --- Mapeo países YF → TE ---
mapa_paises_yf = {
    "united states": "usa", "united kingdom": "europe",
    "germany": "europe", "france": "europe", "italy": "europe",
    "spain": "europe"
}

# --- Ticker locales mapeados ---
ticker_map = {
    "YPFD": "YPF.BA", "TGSU2": "TGSU2.BA", "MIRG": "MIRG.BA", "VISTA": "VIST",
    "FALABELLA": "FALABELLA.CL", "CEMEXCPO": "CEMEXCPO.MX", "OM:STIL": "STIL.ST", "HLSE:ETTE": "ETTE.HE"
}

paises_disponibles_te = set()

# --- Función para detectar bonos argentinos ---
def es_bono_argentino(ticker):
    ticker = ticker.upper()
    return any([
        ticker.endswith("D"),
        ticker.startswith("AL"),
        ticker.startswith("GD"),
        ticker.startswith("AE"),
        ticker.startswith("TO"),
        ticker.startswith("TV"),
        ticker in [
            "AA22", "AA26", "AL29", "AL30", "AL35", "AL41", "AL44", "AL50",
            "BA37", "BA75", "BPLDD", "BPLDC", "DICA", "DICY", "PARY", "PBA25",
            "PBA26", "PBA37", "PBD19", "PBJ25", "PBY22", "PR13", "PR15", "PR17",
            "TV23", "TV24", "TV25", "TV26", "TV27", "TV28", "TV29", "TV30", "TVPP"
        ]
    ])

# --- Función para calcular CAGR histórico de 3 años ---
def calcular_cagr_3y(df):
    try:
        if df.shape[0] >= 756:
            inicial = df['Close'].iloc[-756]
            final = df['Close'].iloc[-1]
            cagr = (final / inicial) ** (1 / 3) - 1
            return round(cagr * 100, 2)
    except:
        pass
    return None

# --- Análisis de volumen promedio ---
def analizar_volumen(df):
    try:
        vol_actual = df['Volume'].iloc[-1]
        vol_prom = df['Volume'].rolling(20).mean().iloc[-1]
        return vol_actual > vol_prom
    except:
        return False

# --- Guardar scoring histórico para backtesting ---
def guardar_score_historico(df_result):
    fecha_actual = datetime.now().strftime("%Y-%m-%d")
    nombre_archivo = f"AnalisisFinal-{fecha_actual}_export.csv"
    path = os.path.join("historicos", nombre_archivo)
    os.makedirs("historicos", exist_ok=True)
    df_result.to_csv(path, index=False)
    print(f"Score guardado en {path}")

# --- Predicción de retorno con ML ---
def predecir_retorno_ml(resultado):
    try:
        modelo = joblib.load("modelo_retorno.pkl")
        features = [
            resultado.get("Beta"), resultado.get("ROE"), resultado.get("ROIC"),
            resultado.get("PEG Ratio"), resultado.get("FCF Yield"),
            resultado.get("P/E Ratio"), resultado.get("P/B Ratio"),
            resultado.get("Dividend Yield"), resultado.get("Debt/Equity"),
            resultado.get("EV/EBITDA"), resultado.get("Forward EPS"),
            resultado.get("Forward Revenue Growth"), resultado.get("Margen Futuro"),
            resultado.get("Score Numérico Total")
        ]
        if None in features:
            return None
        return round(modelo.predict([features])[0], 2)
    except:
        return None

# --- Indicadores técnicos ---
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

def calcular_ema(df):
    df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
    df['EMA200'] = df['Close'].ewm(span=200, adjust=False).mean()
    return df

def calcular_bollinger(df, window=20):
    sma = df['Close'].rolling(window).mean()
    std = df['Close'].rolling(window).std()
    df['Bollinger Lower'] = sma - 2 * std
    df['Bollinger Upper'] = sma + 2 * std
    return df

# --- Contexto y país ---
def cargar_paises_te():
    global paises_disponibles_te
    try:
        te.login(TRADINGECONOMICS_API_KEY)
        url = f"https://api.tradingeconomics.com/country?c={TRADINGECONOMICS_API_KEY}"
        r = requests.get(url)
        if r.status_code == 200:
            paises_disponibles_te = {p["country"].lower() for p in r.json()}
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

sectores_ciclicos = ["consumer discretionary", "financial", "industrials", "real estate"]
riesgos_regulatorios = {
    "argentina": ["bank", "financiera", "banco"],
    "venezuela": ["petrol", "energy"],
    "china": ["tech", "internet"]
}

def penalizacion_sectorial(pais, sector):
    sector = sector.lower()
    penalizacion = 0
    if any(sc in sector for sc in sectores_ciclicos):
        penalizacion -= 1
    if pais in riesgos_regulatorios:
        if any(r in sector for r in riesgos_regulatorios[pais]):
            penalizacion -= 1
    return penalizacion

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

# --- Proyección y sector ---
def agregar_proyecciones_forward(resultado, ticker_map):
    ticker = resultado.get("Ticker", "")
    ticker_ = ticker_map.get(ticker.upper(), ticker.upper())
    try:
        info = yf.Ticker(ticker_).info
        forward_eps = info.get("forwardEps")
        forward_rev_growth = info.get("revenueGrowth")
        margin_future = info.get("netMargins")
        sector = info.get("sector")
        resultado["Forward EPS"] = forward_eps
        resultado["Forward Revenue Growth"] = forward_rev_growth * 100 if forward_rev_growth else None
        resultado["Margen Futuro"] = margin_future
        resultado["Sector"] = sector
        if forward_rev_growth:
            if forward_rev_growth >= 0.15:
                resultado["Crecimiento Futuro"] = "🟢 Alto"
            elif forward_rev_growth >= 0.05:
                resultado["Crecimiento Futuro"] = "🟡 Moderado"
            else:
                resultado["Crecimiento Futuro"] = "🔴 Bajo"
        else:
            resultado["Crecimiento Futuro"] = "🔴 Bajo"
    except:
        resultado["Forward EPS"] = None
        resultado["Forward Revenue Growth"] = None
        resultado["Margen Futuro"] = None
        resultado["Crecimiento Futuro"] = "🔴 Bajo"
    return resultado

# --- Cálculo de Score ---
def calcular_score(resultado):
    if resultado.get("Tipo") == "Bono":
        return "N/A", 0
    score = 0
    ticker = resultado.get("Ticker", "")
    justificaciones = []

    # Métricas financieras
    if (b := resultado.get("Beta")) is not None and b <= 1:
        score += 1
        justificaciones.append("Beta <= 1")
    if (de := resultado.get("Debt/Equity")) and 0 < de < 1:
        score += 1
        justificaciones.append("Deuda/Equity < 1")
    if (ev := resultado.get("EV/EBITDA")) and 0 < ev < 15:
        score += 1
        justificaciones.append("EV/EBITDA < 15")
    if (roe := resultado.get("ROE")) and roe > 0.10:
        score += 1
        justificaciones.append("ROE > 10%")
    if (roic := resultado.get("ROIC")) and roic > 0.08:
        score += 1
        justificaciones.append("ROIC > 8%")
    if (peg := resultado.get("PEG Ratio")):
        if 0 < peg < 1.5 or (peg > 1.5 and resultado.get("Forward Revenue Growth", 0) > 20):
            score += 1
            justificaciones.append("PEG Ratio razonable")
    if (fcf := resultado.get("FCF Yield")):
        if fcf > 0: score += 1; justificaciones.append("FCF positivo")
        if fcf > 5: score += 1; justificaciones.append("FCF > 5%")
    if (pe := resultado.get("P/E Ratio")) and 0 < pe < 20:
        score += 1
        justificaciones.append("P/E < 20")
    if (pb := resultado.get("P/B Ratio")) and 0 < pb < 3:
        score += 1
        justificaciones.append("P/B < 3")
    if (div := resultado.get("Dividend Yield")) and div > 0.02:
        score += 1
        justificaciones.append("Dividendo > 2%")
    if (up := resultado.get("% Subida a Máx")) and up > 40:
        score += 1
        justificaciones.append("Potencial subida > 40%")
    if (rev := resultado.get("Revenue Growth YoY")) and rev > 15:
        score += 1
        justificaciones.append("Crecimiento histórico > 15%")

    # Proyecciones futuras
    if (eps_fwd := resultado.get("Forward EPS")):
        if eps_fwd > 0: score += 1; justificaciones.append("EPS futuro positivo")
        elif eps_fwd < 0: score -= 1; justificaciones.append("EPS futuro negativo")
    if (rev_fwd := resultado.get("Forward Revenue Growth")):
        if rev_fwd > 10: score += 1; justificaciones.append("Crecimiento futuro > 10%")
        elif rev_fwd < 0: score -= 1; justificaciones.append("Crecimiento futuro negativo")
    if (margen := resultado.get("Margen Futuro")) and margen > 0.15:
        score += 1
        justificaciones.append("Margen futuro saludable")

    # Técnicos (sin cambios)
    try:
        hist = resultado.get("Hist")
        if isinstance(hist, dict):
            df = pd.DataFrame(hist)
            df = calcular_ema(df)
            df = calcular_bollinger(df)
            df["RSI"] = calcular_rsi(df)
            df["MACD"], df["Signal"] = calcular_macd(df)
            rsi = df["RSI"].dropna().iloc[-1]
            macd = df["MACD"].iloc[-1]
            signal = df["Signal"].iloc[-1]
            precio = df['Close'].iloc[-1]
            if 30 < rsi < 70: score += 1; justificaciones.append("RSI saludable")
            if macd > signal: score += 1; justificaciones.append("MACD cruzado")
            if df["EMA50"].iloc[-1] > df["EMA200"].iloc[-1]: score += 1; justificaciones.append("Tendencia EMA positiva")
            if precio < df["Bollinger Lower"].iloc[-1]: score += 1; justificaciones.append("En banda inferior Bollinger")
    except:
        pass

    # Penalizaciones
    if (pe := resultado.get("P/E Ratio")) and pe > 60:
        score -= 1
        justificaciones.append("P/E > 60 (penaliza)")
    if (roe := resultado.get("ROE")) and roe < 0:
        score -= 1
        justificaciones.append("ROE negativo")

    # Sector estratégico
    sector = str(resultado.get("Sector") or "").lower()
    if any(x in sector for x in ["ai", "inteligencia", "energ", "defens", "cloud", "infra", "semic", "space", "uran", "aero"]):
        score += 1
        justificaciones.append("Sector estratégico")

    # Penalización por ciclo macro-sectorial o riesgo regulatorio
    pais = obtener_pais_ticker(ticker)
    penal = penalizacion_sectorial(pais, sector)
    score += penal
    if penal < 0:
        justificaciones.append(f"Penalización sectorial por {pais}/{sector} ({penal})")

    # Contexto
    contexto, bonus = obtener_contexto_mundial(ticker)
    resultado["Contexto Global"] = contexto
    score += bonus
    if bonus > 0:
        justificaciones.append(f"Contexto global favorable (+{bonus})")

    # --- Precio objetivo ---
    try:
        actual = resultado.get("Actual")
        eps_fwd = resultado.get("Forward EPS")
        if eps_fwd and eps_fwd > 0 and actual and actual > 0:
            target_base = eps_fwd * 18
            target_bull = eps_fwd * 25
            target_bear = eps_fwd * 12
            resultado["Target Base 12M"] = round(target_base, 2)
            resultado["Target Alcista 12M"] = round(target_bull, 2)
            resultado["Target Conservador"] = round(target_bear, 2)
            resultado["Proyección 12M (%)"] = round((target_base - actual) / actual * 100, 2)
        else:
            resultado["Target Base 12M"] = None
            resultado["Target Alcista 12M"] = None
            resultado["Target Conservador"] = None
            resultado["Proyección 12M (%)"] = None
            justificaciones.append("Sin proyección por EPS negativo o datos inválidos")
    except:
        resultado["Target Base 12M"] = None
        resultado["Target Alcista 12M"] = None
        resultado["Target Conservador"] = None
        resultado["Proyección 12M (%)"] = None

    resultado["Score Numérico Total"] = score
    resultado["Justificación Score"] = justificaciones

    if score >= 13:
        return "⭐⭐⭐⭐⭐ (5/5 - Excelente)", 5
    elif score >= 10:
        return "⭐⭐⭐⭐ (4/5 - Muy Bueno)", 4
    elif score >= 7:
        return "⭐⭐⭐ (3/5 - Aceptable)", 3
    elif score >= 4:
        return "⭐⭐ (2/5 - Riesgoso)", 2
    else:
        return "⭐ (1/5 - Débil)", 1
