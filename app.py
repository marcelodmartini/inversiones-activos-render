import pandas as pd
import streamlit as st
import re
from datetime import datetime
from pycoingecko import CoinGeckoAPI
from helpers.graficos import graficar_precio_historico, graficar_radar_scores, graficar_subida_maximo
from helpers.score import (
    ticker_map, obtener_pais_ticker, es_bono_argentino, calcular_score,
    cargar_paises_te, agregar_proyecciones_forward, calcular_cagr_3y,
    analizar_volumen, guardar_score_historico, predecir_retorno_ml
)
from helpers.yahoo import analizar_con_yfinance
from helpers.alphavantage import analizar_con_alphavantage
from helpers.coingecko import analizar_con_coingecko
from helpers.rava import obtener_precio_bono_rava
from helpers.investpy_utils import analizar_con_investpy
from helpers.fundamentales import obtener_info_fundamental
from helpers.byma import obtener_precio_bono_byma
from helpers.logger import log_info, log_error
from config import ES_CLOUD, ALPHA_VANTAGE_API_KEY, OPENAI_API_KEY
import openai
import glob
import os
import subprocess
from pandas.io.formats.style import Styler

log_info("La app inició correctamente")
cargar_paises_te()
st.set_page_config(page_title="Análisis Financiero IA", layout="wide")

def recomendar(score_texto, crecimiento):
    match = re.search(r"(\\d+)/5", str(score_texto))
    score_valor = int(match.group(1)) if match else 0
    if score_valor >= 4:
        return "✅ Comprar"
    elif score_valor == 3 and crecimiento in ["🟢 Alto", "🟡 Moderado"]:
        return "🙀 Revisar"
    return "❌ Evitar"

def obtener_csv_mas_reciente(patron="historicos/AnalisisFinal-*-export.csv"):
    archivos = glob.glob(patron)
    return sorted(archivos, key=os.path.getmtime, reverse=True)[0] if archivos else None

if st.sidebar.button("🔁 Reentrenar modelo manualmente"):
    try:
        subprocess.run(["python", "helpers/entrenar_modelo.py"], check=True)
        st.sidebar.success("✅ Modelo reentrenado exitosamente.")
    except Exception as e:
        st.sidebar.error(f"❌ Error al reentrenar el modelo: {e}")

try:
    subprocess.run(["python", "helpers/entrenar_modelo.py"], check=True)
    log_info("Modelo reentrenado automáticamente")
except Exception as e:
    log_error(f"Error al reentrenar el modelo automáticamente: {e}")

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
    if "Ticker" not in df_input.columns:
        st.error("❌ El archivo debe contener una columna llamada 'Ticker'.")
        st.stop()
    st.success("✅ Archivo CSV con tickers cargado manualmente")
elif archivo_por_defecto:
    df_input = pd.read_csv(archivo_por_defecto)
    if "Ticker" not in df_input.columns:
        st.error(f"❌ El archivo por defecto `{archivo_por_defecto}` no contiene la columna 'Ticker'.")
        st.stop()
    st.warning(f"⚠️ Usando archivo por defecto: `{archivo_por_defecto}`")
else:
    st.error("❌ No se cargó ningún archivo CSV válido.")
    st.stop()

client = openai.OpenAI(api_key=OPENAI_API_KEY)
st.header("💬 Chat con IA Financiera (OpenAI)")
prompt = st.text_area("Escribí tu consulta para ChatGPT", placeholder="Ej: ¿Conviene invertir en bonos ajustados por CER o en acciones energéticas?")

if st.button("Consultar IA") and prompt.strip():
    with st.spinner("Consultando a ChatGPT..."):
        try:
            messages = [
                {"role": "system", "content": "Actuá como un asesor financiero profesional con experiencia en macroeconomía, análisis bursátil y estrategias de inversión."},
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

def recomendar(score_texto, crecimiento):
    match = re.search(r"(\\d+)/5", str(score_texto))
    score_valor = int(match.group(1)) if match else 0
    if score_valor >= 4:
        return "✅ Comprar"
    elif score_valor == 3 and crecimiento in ["🟢 Alto", "🟡 Moderado"]:
        return "🙀 Revisar"
    return "❌ Evitar"

with st.spinner("Analizando activos..."):
    for raw_ticker in df_input['Ticker']:
        if pd.isna(raw_ticker) or not str(raw_ticker).strip():
            continue
        fuentes_probadas = []
        raw_ticker = str(raw_ticker).strip()
        ticker_clean = raw_ticker.upper()
        ticker_real = ticker_map.get(ticker_clean, ticker_clean)
        es_bono = es_bono_argentino(ticker_clean)
        resultado = None

        if not ES_CLOUD:
            try:
                fuentes_probadas.append("Yahoo Finance")
                resultado = analizar_con_yfinance(ticker_real, fecha_inicio, fecha_fin)
            except Exception as e:
                errores_conexion.append(f"[Yahoo Finance] {ticker_clean}: {e}")

        if not resultado and ALPHA_VANTAGE_API_KEY:
            try:
                fuentes_probadas.append("Alpha Vantage")
                resultado = analizar_con_alphavantage(ticker_clean, fecha_inicio, fecha_fin)
            except Exception as e:
                errores_conexion.append(f"[Alpha Vantage] {ticker_clean}: {e}")

        if not resultado and ticker_clean.lower() in criptos_disponibles:
            try:
                fuentes_probadas.append("CoinGecko")
                resultado = analizar_con_coingecko(cg, ticker_clean.lower(), fecha_inicio, fecha_fin)
            except Exception as e:
                errores_conexion.append(f"[CoinGecko] {ticker_clean.lower()}: {e}")

        if not resultado:
            try:
                pais = obtener_pais_ticker(ticker_clean)
                fuentes_probadas.append(f"Investpy ({pais})")
                resultado = analizar_con_investpy(ticker_clean, pais, fecha_inicio, fecha_fin)
            except Exception as e:
                errores_conexion.append(f"[Investpy] {ticker_clean}: {e}")

        if not resultado and es_bono:
            try:
                fuentes_probadas.append("BYMA")
                resultado = obtener_precio_bono_byma(ticker_clean)
                if resultado:
                    resultado["Tipo"] = "Bono"
                    resultado["Advertencia"] = "⚠️ Solo precio disponible, sin métricas fundamentales"
            except Exception as e:
                errores_conexion.append(f"[BYMA] {ticker_clean}: {e}")

        if resultado is None:
            resultado = {
                "Ticker": ticker_clean,
                "Error": "❌ No se encontró información en ninguna fuente",
                "Fuente": "Ninguna",
                "Fuentes Probadas": ", ".join(fuentes_probadas),
                "Advertencia": "⚠️ No se encontró información",
                "Tipo": "Desconocido"
            }

        info_fundamental = obtener_info_fundamental(ticker_clean)
        resultado = agregar_proyecciones_forward(resultado, ticker_map)
        for k, v in info_fundamental.items():
            if k not in resultado or resultado[k] is None:
                resultado[k] = v

        if "Tipo" not in resultado or resultado["Tipo"] == "Desconocido":
            resultado["Tipo"] = "Bono" if es_bono else "Acción"

        if "Sector" not in resultado or resultado["Sector"] is None:
            resultado["Sector"] = ""

        score_texto, score_numerico = calcular_score(resultado)
        resultado["Score Final"] = score_texto
        resultado["__orden_score"] = score_numerico
        resultados.append(resultado)

df_result = pd.DataFrame(resultados)
df_result = df_result.sort_values("__orden_score", ascending=False).drop(columns="__orden_score")
df_result["Recomendación"] = df_result.apply(lambda row: recomendar(row["Score Final"], row.get("Crecimiento Futuro", "")), axis=1)

columnas_prioritarias = [
    "Ticker", "Score Final", "Recomendación", "% Subida a Máx", "Crecimiento Futuro",
    "País", "Semáforo Riesgo", "Contexto Global", "Proyección 12M (%)", "Score Numérico Total"
]
columnas_restantes = [col for col in df_result.columns if col not in columnas_prioritarias]
df_result = df_result[columnas_prioritarias + columnas_restantes]

guardar_score_historico(df_result)

tooltips = {
    "Ticker": "Símbolo del activo",
    "Score Final": "Puntaje total (máx. 5) integrando fundamentales, técnicos y contexto",
    "Crecimiento Futuro": "Proyección de crecimiento basada en estimaciones Forward",
    "Target Base 12M": "Precio objetivo base estimado en 12 meses",
    "Target Alcista 12M": "Escenario optimista a 12 meses",
    "Target Conservador": "Escenario pesimista a 12 meses",
    "Proyección 12M (%)": "Proyección estimada de retorno a 12 meses",
    "% Subida a Máx": "Potencial de revalorización al máximo anterior",
    "Beta": "Volatilidad respecto al mercado",
    "Recomendación": "Sugerencia basada en el análisis integral"
}

st.dataframe(
    df_result,
    use_container_width=True,
    column_config={k: st.column_config.TextColumn(k, help=v) for k, v in tooltips.items() if k in df_result.columns}
)

# Simulador de inversión para el mejor activo
top1 = df_result.iloc[0]
st.subheader("💰 Simulación de Inversión 12M en el Mejor Activo")
if st.button(f"Simular inversión en {top1['Ticker']}"):
    monto = st.number_input("Ingresá el monto a invertir (USD)", value=1000.0, min_value=10.0, step=100.0)
    proy = top1.get("Proyección 12M (%)", 0)
    if pd.notna(proy):
        ganancia = monto * (proy / 100)
        total = monto + ganancia
        st.success(f"🔄 Proyección: {proy:.2f}%")
        st.info(f"📈 Valor estimado en 12 meses: USD {total:,.2f} (ganancia: USD {ganancia:,.2f})")

        # Guardar simulación
        sim_path = "historicos/simulaciones_inversion.csv"
        os.makedirs("historicos", exist_ok=True)
        sim_data = pd.DataFrame([{
            "Fecha": datetime.today().strftime("%Y-%m-%d"),
            "Ticker": top1['Ticker'],
            "Monto": monto,
            "Proyección 12M (%)": proy,
            "Valor Estimado": total,
            "Ganancia Estimada": ganancia
        }])
        if os.path.exists(sim_path):
            sim_data.to_csv(sim_path, mode="a", index=False, header=False)
        else:
            sim_data.to_csv(sim_path, index=False)
        st.success("💾 Simulación guardada en `historicos/simulaciones_inversion.csv`")
    else:
        st.warning("⚠️ Este activo no tiene proyección de retorno disponible.")

if st.checkbox("📊 Mostrar gráficos individuales por activo analizado"):
    st.subheader("Gráficos por activo")
    for _, fila in df_result.iterrows():
        st.markdown(f"---\n### {fila['Ticker']}")
        hist = fila.get("Hist")
        if isinstance(hist, dict): hist = pd.DataFrame(hist)
        elif not isinstance(hist, pd.DataFrame): hist = None
        try:
            graficar_precio_historico(fila['Ticker'], hist)
            graficar_subida_maximo(fila['Ticker'], fila.get('Actual'), fila.get('Máximo'))
            graficar_radar_scores(fila['Ticker'], {k: v for k, v in fila.items() if isinstance(v, (int, float))})
        except Exception as e:
            st.warning(f"Error al graficar {fila['Ticker']}: {e}")

st.subheader("📉 Métricas del Modelo de ML (Retorno 12M)")
try:
    with open("modelo_rmse.txt", "r") as f:
        rmse_value = f.read().strip()
        st.success(f"📈 RMSE del modelo: {rmse_value}")
except Exception as e:
    st.warning(f"No se pudo leer el RMSE: {e}")
try:
    st.image("modelo_histograma.png", caption="Distribución de errores del modelo (Predicción vs Real)", use_column_width=True)
except Exception as e:
    st.warning(f"No se pudo cargar el histograma de errores: {e}")

# Mostrar historial de simulaciones
sim_path = "historicos/simulaciones_inversion.csv"
if os.path.exists(sim_path):
    st.subheader("📂 Historial de Simulaciones")
    df_sims = pd.read_csv(sim_path)
    st.dataframe(df_sims, use_container_width=True)
    st.download_button("⬇️ Descargar historial de simulaciones", data=df_sims.to_csv(index=False).encode("utf-8"), file_name="simulaciones_inversion.csv")

if errores_conexion:
    st.warning("⚠️ Errores de conexión detectados:")
    for err in errores_conexion:
        st.text(err)

# Exportación CSV
fecha_str = datetime.today().strftime("%Y-%m-%d")
nombre_salida = f"AnalisisFinal-{fecha_str}_export.csv"
df_result.to_csv(nombre_salida, index=False)
csv = df_result.to_csv(index=False).encode('utf-8')
st.download_button("🗕️ Descargar resultados en CSV", data=csv, file_name=nombre_salida)
