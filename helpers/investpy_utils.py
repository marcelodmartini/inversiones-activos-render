import investpy
from datetime import datetime, time
import warnings
import time as time_module  # para sleep

def analizar_con_investpy(nombre, pais, fecha_inicio, fecha_fin, reintentos=2, espera=1.5):
    """
    Analiza un activo usando Investpy, devolviendo métricas básicas y el histórico.

    Args:
        nombre (str): Nombre del activo según Investpy (ej: 'YPF')
        pais (str): País del activo (ej: 'argentina')
        fecha_inicio (datetime.date): Fecha de inicio
        fecha_fin (datetime.date): Fecha de fin
        reintentos (int): Cantidad de reintentos si falla la descarga
        espera (float): Segundos entre reintentos

    Returns:
        dict | None: Diccionario con métricas y dataframe 'Hist' o None si falla.
    """
    for intento in range(1, reintentos + 1):
        try:
            fecha_inicio_dt = datetime.combine(fecha_inicio, time.min)
            fecha_fin_dt = datetime.combine(fecha_fin, time.min)

            df = investpy.get_stock_historical_data(
                stock=nombre,
                country=pais,
                from_date=fecha_inicio_dt.strftime('%d/%m/%Y'),
                to_date=fecha_fin_dt.strftime('%d/%m/%Y')
            )

            if df.empty or 'Close' not in df.columns:
                warnings.warn(f"[Investpy] Datos vacíos o mal formateados para {nombre} ({pais})")
                return None

            # Asegurar índice datetime
            if not df.index.inferred_type.startswith("datetime"):
                df.index = pd.to_datetime(df.index)

            min_price = df['Close'].min()
            max_price = df['Close'].max()
            current_price = df['Close'].iloc[-1]

            if pd.isna(current_price) or current_price <= 0:
                subida = None
            else:
                subida = (max_price - current_price) / current_price * 100

            return {
                "Ticker": nombre,
                "Fuente": f"Investpy ({pais})",
                "Mínimo": round(min_price, 2) if pd.notna(min_price) else None,
                "Máximo": round(max_price, 2) if pd.notna(max_price) else None,
                "Actual": round(current_price, 2) if pd.notna(current_price) else None,
                "% Subida a Máx": round(subida, 2) if subida is not None else None,
                "Hist": df
            }

        except Exception as e:
            print(f"[Investpy] Error al intentar obtener {nombre} ({pais}) - Intento {intento}: {e}")
            warnings.warn(f"[Investpy] Falló intento {intento} para {nombre} - {e}")
            if intento < reintentos:
                time_module.sleep(espera)
            else:
                return None
