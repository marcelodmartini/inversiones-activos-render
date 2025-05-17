import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import numpy as np


def graficar_precio_historico(nombre, df):
    if df is None or df.empty or 'Close' not in df.columns:
        st.warning(f"No hay datos de cierre disponibles para {nombre}.")
        return

    fig, ax = plt.subplots()
    df['Close'].plot(ax=ax, label='Precio Cierre', linewidth=2)
    ax.axhline(df['Close'].iloc[-1], color='red', linestyle='--', label='Precio Actual')
    ax.set_title(f'Histórico de precios: {nombre}')
    ax.set_xlabel('Fecha')
    ax.set_ylabel('Precio')
    ax.legend()
    st.pyplot(fig)


def graficar_radar_scores(nombre, scores_dict):
    if not scores_dict:
        st.warning(f"No hay métricas suficientes para el radar financiero de {nombre}.")
        return

    labels = list(scores_dict.keys())
    values = list(scores_dict.values())
    num_vars = len(labels)

    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    values += values[:1]  # cerrar el gráfico
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.plot(angles, values, color='blue', linewidth=2)
    ax.fill(angles, values, color='skyblue', alpha=0.25)
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    ax.set_title(f'Score Financiero: {nombre}')

    st.pyplot(fig)


def graficar_subida_maximo(nombre, actual, maximo):
    if actual is None or maximo is None or actual == 0:
        return
    subida = (maximo - actual) / actual * 100
    st.metric(label=f"% Subida a Máximo ({nombre})", value=f"{subida:.2f}%")
