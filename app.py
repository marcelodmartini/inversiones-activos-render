import pandas as pd
import streamlit as st
from datetime import datetime
from pycoingecko import CoinGeckoAPI
from helpers.graficos import graficar_precio_historico, graficar_radar_scores, graficar_subida_maximo

# Importaciones de módulos helpers
from helpers.score import ticker_map, obtener_pais_ticker, es_bono_argentino
from helpers.yahoo import analizar_con_yfinance
from helpers.alphavantage import analizar_con_alphavantage
from helpers.coingecko import analizar_con_coingecko
from helpers.rava import obtener_precio_bono_rava
from helpers.investpy_utils import analizar_con_investpy
from helpers.fundamentales import obtener_info_fundamental
from helpers.score import calcular_score, cargar_paises_te
from config import ES_CLOUD, ALPHA_VANTAGE_API_KEY
from helpers.byma import obtener_precio_bono_byma
from helpers.logger import log_info, log_error
from helpers.proyecciones import agregar_proyecciones_forward
from config import OPENAI_API_KEY
import openai
import glob
import os

log_info("La app inició correctamente")
cargar_paises_te()

def obtener_csv_mas_reciente(patron="AnalisisFinal-*-export.csv"):
    archivos = glob.glob(patron)
    if not archivos:
        return None
    return sorted(archivos, key=os.path.getmtime, reverse=True)[0]

if "debug_logs" not in st.session_state:
    st.session_state.debug_logs = []

st.title("Análisis de Activos Financieros con Fallback Inteligente y Múltiples Fuentes")
st.write("Subí un archivo CSV con una columna llamada 'Ticker' (ej: AAPL, BTC, AL30D, etc.)")

col1, col2 = st.columns(2)
with col1:
    fecha_inicio = st.date_input("Fecha de inicio", value=datetime(2010, 1, 1))
with col2:
    fecha_fin = st.date_input("Fecha de fin", value=datetime.today())

uploaded_file = st.file_uploader("Cargar archivo CSV (solo tickers)", type=["csv"])
archivo_por_defecto = obtener_csv_mas_reciente()

if uploaded_file:
    df_input = pd.read_csv(uploaded_file)
    st.success("✅ Archivo CSV con tickers cargado manualmente")
elif archivo_por_defecto:
    df_input = pd.read_csv(archivo_por_defecto)
    st.warning(f"⚠️ No se cargó archivo manualmente. Usando el más reciente: `{archivo_por_defecto}`")
else:
    st.error("❌ No se cargó archivo CSV y no se encontró uno por defecto en la carpeta.")
    st.stop()

client = openai.OpenAI(api_key=OPENAI_API_KEY)

st.header("💬 Chat con IA Financiera (OpenAI)")
prompt = st.text_area("Escribí tu consulta para ChatGPT", placeholder="Ej: ¿Conviene invertir en bonos ajustados por CER o en acciones de empresas energéticas argentinas?")
if st.button("Consultar IA") and prompt.strip():
    with st.spinner("Consultando a ChatGPT..."):
        try:
            messages = [
                {"role": "system", "content": "Actuá como un asesor financiero profesional..."},
                {"role": "user", "content": "Hola, quiero hacerte una consulta de inversión financiera."},
                {"role": "assistant", "content": "Hola, encantado de ayudarte. ¿Qué activo, estrategia o análisis querés consultar?"},
                {"role": "user", "content": prompt}
            ]
            response = client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=1500,
            )
            st.markdown("**Respuesta:**")
            st.write(response.choices[0].message.content)
        except Exception as e:
            st.error(f"Error al contactar a OpenAI: {e}")

cg = CoinGeckoAPI()
errores_conexion, resultados = [], []
criptos_disponibles = [c['id'] for c in cg.get_coins_list()]

with st.spinner("Analizando activos..."):
    for raw_ticker in df_input['Ticker']:
        if pd.isna(raw_ticker) or not str(raw_ticker).strip():
            continue
        fuentes_probadas = []
        raw_ticker = str(raw_ticker).strip()
        ticker_real = ticker_map.get(raw_ticker.upper(), raw_ticker)
        ticker_clean = raw_ticker.upper()
        es_bono = es_bono_argentino(ticker_clean)
        resultado = None

        if not ES_CLOUD:
            try:
                fuentes_probadas.append("Yahoo Finance")
                resultado = analizar_con_yfinance(ticker_real, fecha_inicio, fecha_fin)
            except Exception as e:
                errores_conexion.append(f"[Yahoo Finance] {ticker_clean}: {e}")

        if not resultado and ALPHA_VANTAGE_API_KEY and not ES_CLOUD:
            try:
                fuentes_probadas.append("Alpha Vantage")
                resultado = analizar_con_alphavantage(ticker_clean, fecha_inicio, fecha_fin)
            except Exception as e:
                errores_conexion.append(f"[Alpha Vantage] {ticker_clean}: {e}")

        if not resultado and raw_ticker.lower() in criptos_disponibles:
            try:
                fuentes_probadas.append("CoinGecko")
                resultado = analizar_con_coingecko(cg, raw_ticker.lower(), fecha_inicio, fecha_fin)
            except Exception as e:
                errores_conexion.append(f"[CoinGecko] {raw_ticker.lower()}: {e}")

        if not resultado:
            try:
                pais = obtener_pais_ticker(ticker_clean)
                fuentes_probadas.append(f"Investpy ({pais})")
                resultado = analizar_con_investpy(ticker_clean, pais, fecha_inicio, fecha_fin)
            except Exception as e:
                errores_conexion.append(f"[Investpy] {ticker_clean}: {e}")

        if not resultado and es_bono:
            try:
                fuentes_probadas.append("BYMA Open Data")
                precio_byma = obtener_precio_bono_byma(ticker_clean)
                if precio_byma:
                    resultado = precio_byma
                    resultado["Tipo"] = "Bono"
                    resultado["Advertencia"] = "⚠️ Solo precio disponible, sin métricas fundamentales"
            except Exception as e:
                errores_conexion.append(f"[BYMA] {ticker_clean}: {e}")

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
        resultado = agregar_proyecciones_forward(resultado, ticker_map)
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

columnas_prioritarias = ["Ticker", "Semáforo Riesgo", "Crecimiento Futuro", "Cobertura", "Score Final", "% Subida a Máx", "Beta", "País"]
columnas_existentes = [col for col in columnas_prioritarias if col in df_result.columns]
columnas_resto = [col for col in df_result.columns if col not in columnas_existentes]
df_result = df_result[columnas_existentes + columnas_resto]

def recomendar(score_texto, crecimiento):
    score_valor = int(score_texto[0]) if score_texto and "/" in score_texto else 0
    if score_valor >= 4 and crecimiento == "🟢 Alto":
        return "✅ Comprar"
    elif score_valor >= 3 and crecimiento in ["🟢 Alto", "🟡 Moderado"]:
        return "👀 Revisar"
    else:
        return "❌ Evitar"

df_result["Recomendación"] = df_result.apply(lambda row: recomendar(row["Score Final"], row.get("Crecimiento Futuro", "")), axis=1)

def resaltar(val, mapa):
    if not val or not isinstance(val, str): return ""
    return f"background-color: {mapa.get(val, '#eeeeee')}; font-weight: bold"

styled_df = df_result.style\
    .applymap(lambda val: resaltar(val, {"VERDE": "#c8e6c9", "AMARILLO": "#fff9c4", "ROJO": "#ffcdd2"}), subset=["Semáforo Riesgo"])\
    .applymap(lambda val: resaltar(val, {"🟢 Alto": "#c8e6c9", "🟡 Moderado": "#fff9c4", "🔴 Bajo": "#ffcdd2"}), subset=["Crecimiento Futuro"])\
    .applymap(lambda val: resaltar(val, {"✅ Comprar": "#c8e6c9", "👀 Revisar": "#fff9c4", "❌ Evitar": "#ffcdd2"}), subset=["Recomendación"])

if st.checkbox("📊 Mostrar gráficos individuales por activo analizado"):
    st.subheader("Gráficos por activo")
    for _, fila in df_result.iterrows():
        st.markdown(f"---\n### {fila['Ticker']}")
        hist = fila.get("Hist")
        if isinstance(hist, dict):
            hist = pd.DataFrame(hist)
        elif not isinstance(hist, pd.DataFrame):
            hist = None
        try:
            graficar_precio_historico(fila['Ticker'], hist)
            graficar_subida_maximo(fila['Ticker'], fila.get('Actual'), fila.get('Máximo'))
            graficar_radar_scores(fila['Ticker'], {k: v for k, v in fila.items() if isinstance(v, (int, float)) and k not in ['Mínimo', 'Máximo', 'Actual', '% Subida a Máx']})
        except Exception as e:
            st.warning(f"Error al graficar {fila['Ticker']}: {e}")

st.dataframe(styled_df, use_container_width=True)
if errores_conexion:
    st.warning("⚠️ Errores de conexión detectados:")
    for err in errores_conexion:
        st.text(err)

fecha_str = datetime.today().strftime("%Y-%m-%d")
nombre_salida = f"AnalisisFinal-{fecha_str}_export.csv"
df_result.drop(columns=["Hist"], errors="ignore").to_csv(nombre_salida, index=False)
csv = df_result.to_csv(index=False).encode('utf-8')

if st.session_state.debug_logs:
    st.markdown("### 🛠️ Logs de Depuración")
    st.text_area("Salida de depuración", "\n".join(st.session_state.debug_logs), height=300)

st.download_button("Descargar resultados en CSV", data=csv, file_name=nombre_salida)
