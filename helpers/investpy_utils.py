import investpy
from datetime import datetime, time
import warnings


def analizar_con_investpy(nombre, pais, fecha_inicio, fecha_fin):
    global errores_conexion
    try:
        fecha_inicio_dt = datetime.combine(fecha_inicio, time.min)
        fecha_fin_dt = datetime.combine(fecha_fin, time.min)

        df = investpy.get_stock_historical_data(
            stock=nombre,
            country=pais,
            from_date=fecha_inicio_dt.strftime('%d/%m/%Y'),
            to_date=fecha_fin_dt.strftime('%d/%m/%Y')
        )
        min_price = df['Close'].min()
        max_price = df['Close'].max()
        current_price = df['Close'][-1]
        subida = (max_price - current_price) / current_price * 100
        return {
            "Ticker": nombre, "Fuente": f"Investpy ({pais})",
            "Mínimo": round(min_price, 2), "Máximo": round(max_price, 2),
            "Actual": round(current_price, 2), "% Subida a Máx": round(subida, 2),
            "Hist": hist  # 👉 agregado para el gráfico histórico
        }
    except Exception as e:
        print(f"[Investpy] {nombre}: {e}")
        print(f"[ERROR] Investpy falló para {nombre} - {e}")
        warnings.warn(f"DEBUG: Investpy falló para {nombre} - {e}")