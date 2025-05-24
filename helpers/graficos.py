import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import numpy as np


def graficar_precio_historico(nombre, df):
    if df is None or df.empty or 'Close' not in df.columns:
        st.warning(f"No hay datos de cierre disponibles para {nombre}.")
        return

    # Asegurar que el índice sea datetime
    if not pd.api.types.is_datetime64_any_dtype(df.index):
        df.index = pd.to_datetime(df.index)

    fig, ax = plt.subplots(figsize=(10, 5))
    df['Close'].plot(ax=ax, label='Precio Cierre', linewidth=2, color='blue')
    actual = df['Close'].iloc[-1]
    fecha_actual = df.index[-1].strftime("%Y-%m-%d")
    ax.axhline(actual, color='red', linestyle='--', label=f'Precio Actual ({actual:.2f})')
    ax.set_title(f'Histórico de precios: {nombre} (hasta {fecha_actual})')
    ax.set_xlabel('Fecha')
    ax.set_ylabel('Precio')
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend()
    st.pyplot(fig)


def graficar_radar_scores(nombre, scores_dict):
    if not scores_dict:
        st.warning(f"No hay métricas suficientes para el radar financiero de {nombre}.")
        return

    labels = list(scores_dict.keys())
    values = list(scores_dict.values())
    num_vars = len(labels)

    # Normalizar si hay valores fuera de rango
    valores_validos = [v for v in values if isinstance(v, (int, float))]
    max_val = max(valores_validos) if valores_validos else 1
    if max_val > 10:
        values = [v / max_val * 10 for v in values]

    # Armar el radar
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    values += values[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.plot(angles, values, color='navy', linewidth=2)
    ax.fill(angles, values, color='skyblue', alpha=0.3)
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_title(f'Score Financiero: {nombre}', size=14)
    st.pyplot(fig)


def graficar_subida_maximo(nombre, actual, maximo):
    if not isinstance(actual, (int, float)) or not isinstance(maximo, (int, float)) or actual <= 0:
        st.warning(f"No se pudo calcular la subida para {nombre}.")
        return
    subida = (maximo - actual) / actual * 100
    st.metric(label=f"% Subida a Máximo ({nombre})", value=f"{subida:.2f}%")
