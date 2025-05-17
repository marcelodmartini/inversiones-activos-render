import pandas as pd
import streamlit as st
from datetime import datetime
from pycoingecko import CoinGeckoAPI
from helpers.graficos import graficar_precio_historico, graficar_radar_scores, graficar_subida_maximo

# Importaciones de módulos helpers
from helpers.score import ticker_map, pais_por_ticker, es_bono_argentino
from helpers.yahoo import analizar_con_yfinance
from helpers.alphavantage import analizar_con_alphavantage
from helpers.coingecko import analizar_con_coingecko
from helpers.rava import obtener_precio_bono_rava
from helpers.investpy_utils import analizar_con_investpy
from helpers.fundamentales import obtener_info_fundamental
from helpers.score import calcular_score
from config import ES_CLOUD, ALPHA_VANTAGE_API_KEY
from helpers.byma import obtener_precio_bono_byma
import subprocess
import os


if "debug_logs" not in st.session_state:
    st.session_state.debug_logs = []

# Título y fecha
st.title("Análisis de Activos Financieros con Fallback Inteligente y Múltiples Fuentes")
st.write("Subí un archivo CSV con una columna llamada 'Ticker' (ej: AAPL, BTC, AL30D, etc.)")


col1, col2 = st.columns(2)
with col1:
    fecha_inicio = st.date_input("Fecha de inicio", value=datetime(2010, 1, 1))
with col2:
    fecha_fin = st.date_input("Fecha de fin", value=datetime.today())

uploaded_file = st.file_uploader("Cargar archivo CSV", type=["csv"])
cg = CoinGeckoAPI()

errores_conexion = []
if uploaded_file:
    df_input = pd.read_csv(uploaded_file)
    if 'Ticker' not in df_input.columns:
        st.error("El archivo CSV debe contener una columna llamada 'Ticker'")
        st.stop()

    resultados = []
    criptos_disponibles = [c['id'] for c in cg.get_coins_list()]

    with st.spinner("Analizando activos..."):
        for raw_ticker in df_input['Ticker']:
            if pd.isna(raw_ticker) or str(raw_ticker).strip() == "":
                continue
            fuentes_probadas = []
            print(f"\n🔎 Analizando: {raw_ticker}")
            raw_ticker = str(raw_ticker).strip()
            ticker_real = ticker_map.get(raw_ticker.upper(), raw_ticker)
            ticker_clean = raw_ticker.upper()
            es_bono = es_bono_argentino(ticker_clean)
            resultado = None

            if not ES_CLOUD:
                try:
                    print(f"[INFO] Intentando con Yahoo Finance: {ticker_real}")
                    fuentes_probadas.append("Yahoo Finance")
                    resultado = analizar_con_yfinance(ticker_real, fecha_inicio, fecha_fin)
                except Exception as e:
                    errores_conexion.append(f"[Yahoo Finance] {ticker_clean}: {e}")
                    print(f"[ERROR] Yahoo Finance falló para {ticker_clean} - {e}")

            if not resultado and ALPHA_VANTAGE_API_KEY and not ES_CLOUD:
                try:
                    print(f"[INFO] Intentando con Alpha Vantage: {ticker_clean}")
                    fuentes_probadas.append("Alpha Vantage")
                    resultado = analizar_con_alphavantage(ticker_clean, fecha_inicio, fecha_fin)
                except Exception as e:
                    errores_conexion.append(f"[Alpha Vantage] {ticker_clean}: {e}")
                    print(f"[ERROR] Alpha Vantage falló para {ticker_clean} - {e}")

            if not resultado and raw_ticker.lower() in criptos_disponibles:
                try:
                    print(f"[INFO] Intentando con CoinGecko: {raw_ticker.lower()}")
                    fuentes_probadas.append("CoinGecko")
                    resultado = analizar_con_coingecko(cg, raw_ticker.lower(), fecha_inicio, fecha_fin)
                except Exception as e:
                    errores_conexion.append(f"[CoinGecko] {raw_ticker.lower()}: {e}")
                    print(f"[ERROR] CoinGecko falló para {raw_ticker.lower()} - {e}")
                    st.text(f"DEBUG: CoinGecko falló para {raw_ticker.lower()} - {e}")

            if not resultado:
                try:
                    pais = pais_por_ticker.get(raw_ticker.upper(), 'brazil')
                    print(f"[INFO] Intentando con Investpy ({pais}): {ticker_clean}")
                    fuentes_probadas.append(f"Investpy ({pais})")
                    resultado = analizar_con_investpy(ticker_clean, pais, fecha_inicio, fecha_fin)
                except Exception as e:
                    errores_conexion.append(f"[Investpy] {ticker_clean}: {e}")
                    print(f"[ERROR] Investpy falló para {ticker_clean} - {e}")

            if not resultado and es_bono:
                try:
                    print(f"[INFO] Intentando BYMA Open Data para bono: {ticker_clean}")
                    st.text(f"[INFO] Intentando BYMA Open Data para bono: {ticker_clean}")
                    fuentes_probadas.append("BYMA Open Data")
                    precio_byma = obtener_precio_bono_byma(ticker_clean)
                    if precio_byma:
                        resultado = precio_byma
                        resultado["Tipo"] = "Bono"
                        resultado["Advertencia"] = "⚠️ Solo precio disponible, sin métricas fundamentales"
                except Exception as e:
                    errores_conexion.append(f"[BYMA] {ticker_clean}: {e}")
                    print(f"[ERROR] BYMA falló para {ticker_clean} - {e}")

            # if not resultado:
            #     try:
            #         print(f"[INFO] Fallback: Rava para bono: {ticker_clean}")
            #         st.text(f"[INFO] Fallback: Rava para bono: {ticker_clean}")
            #         fuentes_probadas.append("Rava")
            #         precio_rava = obtener_precio_bono_rava(ticker_clean)
            #         if precio_rava:
            #             resultado = precio_rava
            #             resultado["Tipo"] = "Bono"
            #             resultado["Advertencia"] = "⚠️ Solo precio disponible, sin métricas fundamentales"
            #     except Exception as e:
            #         errores_conexion.append(f"[Rava] {ticker_clean}: {e}")
            #         print(f"[ERROR] Rava falló para {ticker_clean} - {e}")
            #         st.text(f"DEBUG: Rava falló para {ticker_clean} - {e}")


            if resultado:
                resultado["Fuente"] = resultado.get("Fuente", "No informada")
                resultado["Fuentes Probadas"] = ", ".join(fuentes_probadas)
            else:
                resultado = {
                    "Ticker": raw_ticker,
                    "Error": "❌ No se encontró información en ninguna fuente",
                    "Fuente": "Ninguna",
                    "Fuentes Probadas": ", ".join(fuentes_probadas),
                    "Advertencia": "⚠️ No se encontró información",
                    "Tipo": "Desconocido"
                }

            info_fundamental = obtener_info_fundamental(ticker_clean)

            if resultado:
                for k, v in info_fundamental.items():
                    if k not in ["Tipo", "Fuente", "Advertencia", "Error"] and (k not in resultado or resultado[k] is None):
                        resultado[k] = v
            else:
                resultado = info_fundamental
                resultado["Ticker"] = raw_ticker
                resultado["Error"] = "No se encontró información en ninguna fuente"

            score_texto, score_numerico = calcular_score(resultado)
            resultado["Score Final"] = score_texto
            resultado["__orden_score"] = score_numerico

            resultados.append(resultado)

    df_result = pd.DataFrame(resultados)
    df_result = df_result.sort_values("__orden_score", ascending=False).drop(columns="__orden_score")

    # Reordenar columnas con prioridad al principio
    columnas_prioritarias = ["Semáforo Riesgo", "Cobertura", "Score Final", "% Subida a Máx", "Beta", "País"]
    columnas_existentes = [col for col in columnas_prioritarias if col in df_result.columns]
    columnas_resto = [col for col in df_result.columns if col not in columnas_existentes]
    df_result = df_result[columnas_existentes + columnas_resto]


    def resaltar_riesgo(val):
        if not val or not isinstance(val, str):
            return ""
        color = {
            "VERDE": "#c8e6c9",
            "AMARILLO": "#fff9c4",
            "ROJO": "#ffcdd2"
        }.get(val.upper(), "#eeeeee")
        return f"background-color: {color}; font-weight: bold"

    styled_df = df_result.style.map(resaltar_riesgo, subset=["Semáforo Riesgo"])

    # Checkbox para mostrar gráficos
    mostrar_graficos = st.checkbox("📊 Mostrar gráficos individuales por activo analizado")

    if mostrar_graficos:
        st.subheader("Gráficos por activo")
        for _, fila in df_result.iterrows():
            st.markdown(f"---\n### {fila['Ticker']}")

            hist = fila.get("Hist")
            if isinstance(hist, dict):
                hist = pd.DataFrame(hist)
            elif not isinstance(hist, pd.DataFrame):
                hist = None  # Evita pasar float u otro tipo no compatible

            graficar_precio_historico(fila['Ticker'], hist)
            graficar_subida_maximo(fila['Ticker'], fila.get('Actual'), fila.get('Máximo'))
            graficar_radar_scores(fila['Ticker'], {
                k: v for k, v in fila.items()
                if isinstance(v, (int, float)) and k not in ['Mínimo', 'Máximo', 'Actual', '% Subida a Máx']
            })

    df_result_sin_hist = df_result.drop(columns=["Hist"], errors="ignore")
    styled_df = df_result_sin_hist.style.map(resaltar_riesgo, subset=["Semáforo Riesgo"])
    st.dataframe(styled_df, use_container_width=True)

    if errores_conexion:
        st.warning("⚠️ Errores de conexión detectados:")
        for err in errores_conexion:
            st.text(err)

    csv = df_result.to_csv(index=False).encode('utf-8')

    if st.session_state.debug_logs:
        st.markdown("### 🛠️ Logs de Depuración")
        st.text_area("Salida de depuración", "\n".join(st.session_state.debug_logs), height=300)

    st.download_button("Descargar resultados en CSV", data=csv, file_name="analisis_completo_activos.csv")
