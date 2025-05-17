# helpers/coingecko.py
from datetime import datetime, time, timedelta
import warnings


def analizar_con_coingecko(coin_id):
    global errores_conexion
    try:
        # Convertir fecha_inicio y fecha_fin de date a datetime (para usar .timestamp)
        fecha_inicio_dt = datetime.combine(fecha_inicio, time.min)
        fecha_fin_dt = datetime.combine(fecha_fin, time.min)

        if (fecha_fin_dt - fecha_inicio_dt).days > 365:
            fecha_inicio_dt = fecha_fin_dt - timedelta(days=365)

        data = cg.get_coin_market_chart_range_by_id(
            id=coin_id,
            vs_currency='usd',
            from_timestamp=int(fecha_inicio_dt.timestamp()),
            to_timestamp=int(fecha_fin_dt.timestamp())
        )
        prices = [p[1] for p in data['prices']]
        if not prices:
            return None
        min_price = min(prices)
        max_price = max(prices)
        current_price = prices[-1]
        subida = (max_price - current_price) / current_price * 100
        return {
            "Ticker": coin_id,
            "Fuente": "CoinGecko",
            "Mínimo": round(min_price, 2),
            "Máximo": round(max_price, 2),
            "Actual": round(current_price, 2),
            "% Subida a Máx": round(subida, 2),
            "Hist": hist  # 👉 agregado para el gráfico histórico
        }
    except Exception as e:
        print(f"[CoinGecko] {coin_id}: {e}")
        print(f"[ERROR] CoinGecko falló para {coin_id} - {e}")
        warnings.warn(f"DEBUG: CoinGecko falló para {coin_id} - {e}")
