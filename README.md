# Análisis de Activos Financieros con Fallback Inteligente y Score Unificado

Aquí tienes el contenido para un archivo `README.md` que explica detalladamente el significado de cada columna del análisis financiero generado por tu script:

---

# 📊 Análisis de Activos Financieros — Descripción de Columnas

Este documento explica el significado de cada columna incluida en el análisis generado por la aplicación Streamlit `Análisis de Activos Financieros con Fallback Inteligente y Múltiples Fuentes`. El archivo CSV descargable contiene un resumen completo de activos como acciones, bonos y criptomonedas con métricas clave.

---

## 🗂️ Columnas del Informe

| Columna             | Descripción                                                                                                                                            |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Score Final**     | Calificación general del activo basada en un sistema de puntuación de 1 a 5 estrellas, según métricas financieras clave.                               |
| **Semáforo Riesgo** | Indicador visual de riesgo basado en la volatilidad (Beta): <br>🟢 **VERDE**: Bajo riesgo<br>🟡 **AMARILLO**: Riesgo medio<br>🔴 **ROJO**: Riesgo alto |
| **Ticker**          | Código identificador del activo, usado por plataformas financieras (ej: `AAPL`, `AL30D`, `BTC`).                                                       |
| **Fuente**          | Fuente de donde se obtuvo el precio del activo: puede ser *Yahoo Finance*, *Alpha Vantage*, *Investpy*, *CoinGecko*, o *Rava*.                         |
| **Mínimo**          | Precio mínimo registrado dentro del rango de fechas seleccionado.                                                                                      |
| **Máximo**          | Precio máximo registrado dentro del mismo período.                                                                                                     |
| **Actual**          | Precio actual del activo según la última cotización disponible.                                                                                        |
| **% Subida a Máx**  | Potencial de revalorización hasta el máximo histórico dentro del período (%).                                                                          |
| **Tipo**            | Clasificación del activo: `"Acción"`, `"Bono"` o `"Criptomoneda"`.                                                                                     |
| **Advertencia**     | Mensaje opcional si no se encontraron datos fundamentales completos. Puede aparecer: `⚠️ Solo precio disponible, sin métricas fundamentales`.          |
| **País**            | País de origen de la empresa emisora o del activo.                                                                                                     |
| **PEG Ratio**       | Relación Precio/Beneficio ajustada al crecimiento. Valor ideal: < 1.5.                                                                                 |
| **P/E Ratio**       | Relación Precio/Utilidad (Price to Earnings). Menor a 20 es ideal en términos generales.                                                               |
| **P/B Ratio**       | Relación Precio/Valor Libro. Ideal: < 3 para evitar sobrevaloración.                                                                                   |
| **ROE**             | Rentabilidad sobre el Patrimonio (Return on Equity). Mide eficiencia financiera. Ideal: > 10%.                                                         |
| **ROIC**            | Rentabilidad sobre el Capital Invertido (Return on Invested Capital). Ideal: > 8%.                                                                     |
| **FCF Yield**       | Rendimiento del Flujo de Caja Libre (%). Ideal: > 5%.                                                                                                  |
| **Debt/Equity**     | Proporción de deuda respecto al capital propio. Ideal: < 1.                                                                                            |
| **EV/EBITDA**       | Relación entre Valor Empresa y EBITDA. Valor inferior a 15 es generalmente positivo.                                                                   |
| **Dividend Yield**  | Rentabilidad por dividendos (%). Ideal para inversores de ingresos: > 2%.                                                                              |
| **Beta**            | Volatilidad relativa del activo respecto al mercado. Beta < 1 indica menor riesgo.                                                                     |
| **Contexto**        | Breve resumen de la empresa o activo, traducido automáticamente al español.                                                                            |
| **Cobertura**       | Indica cuántas de las métricas fundamentales clave fueron obtenidas. Ejemplo: `5/6`.                                                                   |
| **Error**           | Campo opcional que aparece si no se pudo obtener ninguna información del activo.                                                                       |

---

## 📝 Notas Adicionales

* Si un activo no cuenta con datos fundamentales suficientes, solo se mostrará el precio y se incluirá una advertencia.
* Los valores se calculan para el rango de fechas indicado por el usuario al inicio de la aplicación.
* El sistema puede usar varias fuentes alternativas automáticamente (fallback) en caso de que una no proporcione datos.


Esta app desarrollada en Streamlit permite analizar acciones, criptomonedas y activos bursátiles de múltiples países y fuentes, generando una grilla con indicadores financieros clave, semáforo de riesgo y un **score final del 1 al 5** que evalúa la calidad de inversión de cada activo.

## 📥 ¿Cómo usar?
1. Subí un archivo `.csv` con una columna `Ticker` (ej: AAPL, BTC, GLEN.L, PETR4.SA).
2. Elegí la fecha de inicio y fin del análisis.
3. La app consultará automáticamente a las siguientes fuentes:
   - Yahoo Finance
   - Alpha Vantage
   - CoinGecko
   - Investpy
   - Finnhub
   - Financial Modeling Prep (FMP)

## 📊 Indicadores calculados
Para cada activo, la app obtiene y calcula los siguientes indicadores fundamentales:

- PEG Ratio
- P/E Ratio
- P/B Ratio
- ROE
- ROIC
- FCF Yield
- Debt/Equity
- EV/EBITDA
- Dividend Yield
- Beta
- País
- Contexto actual de la empresa (traducido al español)

## 🚦 Semáforo de Riesgo
Basado en el valor del **Beta**:

| Semáforo   | Condición         | Significado              |
|------------|-------------------|---------------------------|
| 🟢 VERDE   | Beta ≤ 1          | Riesgo bajo              |
| 🟡 AMARILLO| 1 < Beta ≤ 1.5     | Riesgo moderado          |
| 🔴 ROJO    | Beta > 1.5        | Riesgo alto              |

## 🧮 Score Financiero Final (1 a 5)
Un indicador compuesto que sintetiza la salud financiera del activo. Se calcula con 10 métricas clave. El puntaje se traduce así:

| Score | Nivel      | Descripción                        |
|--------|------------|------------------------------------|
| 5/5    | Excelente | Alta calidad, baja deuda, alto potencial de crecimiento
| 4/5    | Muy bueno | Muy buenos fundamentos, leve riesgo
| 3/5    | Aceptable | Correcto, pero con advertencias
| 2/5    | Riesgoso  | Débil en fundamentos o volátil
| 1/5    | Débil     | Mala calidad financiera

### 🎯 Fórmula de cálculo:
Por cada condición cumplida se suma 1 punto (máx 10 puntos):

- ✅ Beta ≤ 1
- ✅ Debt/Equity < 1
- ✅ EV/EBITDA < 15
- ✅ ROE > 10%
- ✅ ROIC > 8%
- ✅ PEG Ratio < 1.5
- ✅ FCF Yield > 5%
- ✅ P/E Ratio < 20
- ✅ P/B Ratio < 3
- ✅ Dividend Yield > 2%

Luego:
- **9–10 puntos → 5/5**
- **7–8 → 4/5**
- **5–6 → 3/5**
- **3–4 → 2/5**
- **0–2 → 1/5**

## 📤 Resultados
- Grilla interactiva con colores por riesgo.
- Score final visible.
- Botón para descargar CSV completo.

## 📦 Requisitos (`requirements.txt`)
```txt
streamlit
yfinance
pandas
investpy
requests
pycoingecko
alpha_vantage
deep-translator
```

## 🔐 Variables en `.streamlit/secrets.toml`
```toml
ALPHA_VANTAGE_API_KEY = "..."
FINNHUB_API_KEY = "..."
FMP_API_KEY = "..."
```

## 🧪 Opcional
Podés expandir el modelo para incluir:
- Inteligencia artificial sobre `Contexto`
- Ranking por sectores o países
- Históricos de evolución de score

---
Hecho con ❤️ y múltiples APIs por [marcelodmartini]

# README.md

# 📊 Análisis de Activos Financieros con Múltiples Fuentes (Streamlit)

Este proyecto permite analizar acciones, bonos y criptomonedas desde distintas fuentes financieras, utilizando Streamlit como interfaz. Ofrece métricas fundamentales, precios históricos y un sistema de puntuación automatizado.

---

## 📁 Estructura del Proyecto

```
/finanzas_app
├── main_app.py                  # App principal Streamlit
├── config.py                    # API keys y configuración
├── requirements.txt             # Dependencias del proyecto
└── helpers/                     # Código modular por fuente
    ├── utils.py                 # Utilidades generales, regex, mapeos
    ├── score.py                 # Cálculo del puntaje financiero
    ├── yahoo.py                 # Datos históricos desde Yahoo Finance
    ├── alphavantage.py          # Datos desde Alpha Vantage API
    ├── coingecko.py             # Precios de criptomonedas (CoinGecko)
    ├── investpy                 # (pendiente si se requiere)
    ├── byma.py                  # Scraping de cotizaciones desde BYMA
    ├── iamc.py                  # Lectura de archivos IAMC locales
    ├── rava.py                  # Scraping desde Rava para bonos
    └── fundamentales.py         # Métricas fundamentales desde yfinance, Finnhub y FMP
```

---

## 🔧 Instalación

```bash
git clone https://github.com/tuusuario/finanzas_app.git
cd finanzas_app
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## 🚀 Ejecución

```bash
streamlit run main_app.py
```

Subí un archivo `.csv` con una columna `Ticker`, por ejemplo:
```
Ticker
AAPL
BTC
AL30D
TGSU2
```

---

## 📡 Fuentes de Datos

- 📈 **Yahoo Finance**: precios históricos y métricas básicas.
- 🔑 **Alpha Vantage**: precios ajustados (requiere API key).
- 💰 **CoinGecko**: precios de criptomonedas (gratis).
- 📊 **Finnhub**: métricas clave (requiere API key).
- 🧾 **Financial Modeling Prep (FMP)**: ratios financieros (requiere API key).
- 🧠 **Deep Translator**: para traducir resúmenes de negocios.
- 📎 **BYMA / IAMC / Rava**: scraping de bonos argentinos.

---

## 🧠 Puntuación Inteligente

Cada activo recibe una calificación del 1 al 5 basada en:
- Beta
- Deuda/Equidad
- ROE / ROIC
- EV/EBITDA
- Yield de flujo libre
- Ratio PEG / PER / PBR
- Dividend Yield

---

## 📌 Notas

- Para usar Alpha Vantage, Finnhub y FMP debes definir las claves API en `.streamlit/secrets.toml`:
```toml
ALPHA_VANTAGE_API_KEY = "tu_api_key"
FINNHUB_API_KEY = "tu_api_key"
FMP_API_KEY = "tu_api_key"
```

---

## Créditos

- [yFinance](https://pypi.org/project/yfinance/)
- [CoinGecko API](https://www.coingecko.com/en/api)
- [Alpha Vantage](https://www.alphavantage.co/)
- [Financial Modeling Prep](https://financialmodelingprep.com/)
- [InvestPy](https://github.com/alvarobartt/investpy)
- [Rava Bursátil](https://www.rava.com/)

---

**Desarrollado para inversores exigentes que buscan decisiones basadas en datos.**

