
# helpers/iamc.py
import pandas as pd

def obtener_precio_bono_iamc(ticker):
    # Esta función simula lectura desde un archivo CSV descargado manualmente de IAMC
    # Podés automatizar esto con pandas.read_csv desde un path local o remoto
    try:
        iamc_path = "./iamc_cotizaciones.csv"  # debe existir con columnas: 'Ticker', 'Precio'
        df = pd.read_csv(iamc_path)
        row = df[df['Ticker'].str.upper() == ticker.upper()]
        if row.empty:
            return None
        current_price = float(row.iloc[0]['Precio'])
        return {
            "Ticker": ticker,
            "Actual": round(current_price, 2),
            "Fuente": "IAMC (archivo local)"
        }
    except Exception as e:
        print(f"[IAMC] {ticker}: {e}")
        print(f"[ERROR] IAMC falló para {ticker} - {e}")
        return None