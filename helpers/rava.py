# helpers/rava.py

import time
import requests
from bs4 import BeautifulSoup
from helpers.iamc import obtener_precio_bono_iamc

def obtener_precio_bono_rava(ticker):
    try:
        time.sleep(1.5)
        url = f"https://www.rava.com/perfil/{ticker}/historial"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/113.0.0.0"
        }
        r = requests.get(url, headers=headers, timeout=10, verify=False)

        if r.status_code != 200 or "Forbidden" in r.text:
            print(f"[Rava] {ticker}: {r.status_code} - Acceso denegado")
            return obtener_precio_bono_iamc(ticker)

        soup = BeautifulSoup(r.text, 'html.parser')
        tabla = soup.find("table")

        if not tabla:
            print(f"[Rava] {ticker}: tabla no encontrada")
            return obtener_precio_bono_iamc(ticker)

        rows = tabla.find_all("tr")[1:]
        precios = []

        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 5:
                try:
                    cierre = float(cols[4].text.strip().replace("$", "").replace(",", "."))
                    precios.append(cierre)
                except:
                    continue

        if not precios:
            print(f"[Rava] {ticker}: no se extrajo ningún precio")
            return obtener_precio_bono_iamc(ticker)

        min_price = min(precios)
        max_price = max(precios)
        current_price = precios[-1]
        subida = (max_price - current_price) / current_price * 100

        return {
            "Ticker": ticker.upper(),
            "Actual": round(current_price, 2),
            "Mínimo": round(min_price, 2),
            "Máximo": round(max_price, 2),
            "% Subida a Máx": round(subida, 2),
            "Hist": hist  # 👉 agregado para el gráfico histórico
        }

    except Exception as e:
        print(f"[ERROR] Rava falló para {ticker} - {e}")
        return obtener_precio_bono_iamc(ticker)
