# helpers/score.py
import re

def es_bono_argentino(ticker):
    return bool(re.match(r"^(AL|GD|TX|TV|AE|TB)[0-9]+[D]?$", ticker.upper()))

pais_por_ticker = {
    "SUPV": "argentina", "BBAR": "argentina", "PAMP": "argentina",
    "YPFD": "argentina", "TGSU2": "argentina", "FALABELLA": "chile",
    "CEMEXCPO": "mexico", "EC": "colombia", "EMBR3": "brazil"
}

ticker_map = {
    "YPFD": "YPF.BA", "TGSU2": "TGSU2.BA", "MIRG": "MIRG.BA", "VISTA": "VIST",
    "FALABELLA": "FALABELLA.CL", "CEMEXCPO": "CEMEXCPO.MX", "OM:STIL": "STIL.ST", "HLSE:ETTE": "ETTE.HE"
}

# helpers/score.py
def calcular_score(resultado):
    if resultado.get("Tipo") == "Bono":
        return "N/A", 0

    score = 0
    try:
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

        if beta <= 1: score += 1
        if debt_equity < 1: score += 1
        if ev_ebitda < 15: score += 1
        if roe > 0.1: score += 1
        if roic > 0.08: score += 1
        if peg < 1.5: score += 1
        if fcf_yield > 5: score += 1
        if pe < 20: score += 1
        if pb < 3: score += 1
        if dividend_yield and dividend_yield > 0.02: score += 1

        if score >= 9: return "⭐⭐⭐⭐⭐ (5/5 - Excelente)", 5
        elif score >= 7: return "⭐⭐⭐⭐ (4/5 - Muy Bueno)", 4
        elif score >= 5: return "⭐⭐⭐ (3/5 - Aceptable)", 3
        elif score >= 3: return "⭐⭐ (2/5 - Riesgoso)", 2
        else: return "⭐ (1/5 - Débil)", 1
    except:
        return "N/A", 0
