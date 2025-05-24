# Análisis de Activos Financieros con Fallback Inteligente y Score Unificado

Este `README.md` explica en detalle el funcionamiento de la aplicación Streamlit `Análisis de Activos Financieros`, que permite evaluar acciones, bonos y criptomonedas mediante indicadores fundamentales, técnicos, contexto macroeconómico y proyecciones de retorno con modelos de Machine Learning, generando un Score Final inteligente.

---

## 📊 Descripción de Columnas del Informe

| Columna                      | Descripción                                                                        |
| ---------------------------- | ---------------------------------------------------------------------------------- |
| **Score Final**              | Calificación de 1 a 5 estrellas según métricas fundamentales, técnicas y contexto. |
| **Score Numérico Total**     | Puntaje acumulado numérico basado en \~20 condiciones.                             |
| **Justificación Score**      | Lista textual de los factores que aportaron al score.                              |
| **Semáforo Riesgo**          | Riesgo del activo según su Beta: 🟢 Bajo, 🟡 Medio, 🔴 Alto.                       |
| **Ticker**                   | Código identificador del activo (ej: AAPL, AL30D, BTC).                            |
| **Fuente**                   | Fuente de datos utilizada: Yahoo, Alpha Vantage, CoinGecko, Investpy, etc.         |
| **Mínimo / Máximo / Actual** | Precios registrados en el período seleccionado.                                    |
| **% Subida a Máx**           | Potencial de revalorización al máximo anterior.                                    |
| **Tipo**                     | Clasificación: "Acción", "Bono", "Criptomoneda".                                   |
| **Advertencia**              | Indica si faltan métricas fundamentales.                                           |
| **País**                     | País de origen del activo.                                                         |
| **PEG, P/E, P/B Ratio**      | Ratios de valuación fundamentales.                                                 |
| **ROE, ROIC**                | Indicadores de rentabilidad.                                                       |
| **FCF Yield**                | Rendimiento de flujo de caja libre.                                                |
| **Debt/Equity**              | Nivel de apalancamiento financiero.                                                |
| **EV/EBITDA**                | Ratio empresa / beneficios.                                                        |
| **Dividend Yield**           | Rentabilidad por dividendos.                                                       |
| **Beta**                     | Volatilidad relativa respecto al mercado.                                          |
| **Contexto**                 | Breve resumen de la empresa, traducido.                                            |
| **CAGR 3Y**                  | Tasa de crecimiento anual compuesta en 3 años.                                     |
| **Volumen Saludable**        | Si el volumen supera el promedio de 20 días.                                       |
| **Cobertura**                | Métricas obtenidas / disponibles. Ej: 8/10                                         |
| **VIX / Riesgo País**        | Indicadores de contexto macro.                                                     |
| **Contexto Global**          | Evaluación del entorno económico: MUY FAVORABLE, MODERADO o ADVERSO.               |
| **Target Base 12M**          | Precio objetivo estimado a 12 meses, usando Forward EPS × PER 18.                  |
| **Target Alcista 12M**       | Precio objetivo optimista, usando Forward EPS × PER 25.                            |
| **Target Conservador**       | Precio objetivo pesimista, usando Forward EPS × PER 12.                            |
| **Proyección 12M (%)**       | Potencial de subida estimado: (Target Base - Actual) / Actual.                     |
| **Retorno 12M ML (%)**       | Predicción del modelo ML para el retorno esperado a 12 meses.                      |
| **Recomendación**            | Sugerencia final: ✅ Comprar, 🙀 Revisar, ❌ Evitar.                                |

---

## 🧠 Cómo funciona el modelo de predicción y cálculo de Score

Esta aplicación integra análisis fundamental, técnico y proyecciones de Machine Learning para ofrecer una evaluación completa de activos financieros. A continuación se detalla cómo se calculan las métricas más importantes:

### 🔍 Datos históricos

Los datos provienen de archivos `.csv` ubicados en la carpeta `/historicos/`, con nombre tipo `AnalisisFinal-YYYYMMDD_export.csv`. Cada archivo contiene:

* Indicadores fundamentales y técnicos de activos (acciones, CEDEARs, criptomonedas).
* Datos extraídos de Yahoo Finance, CoinGecko, AlphaVantage, etc.
* Precio actual (`Actual`) y fecha base para calcular retorno a 12 meses.

---

### 📊 Modelo de predicción: `modelo_retorno.pkl`

Entrenado con `RandomForestRegressor` usando datos históricos. El modelo aprende a predecir el retorno a 12 meses de un activo en función de sus indicadores.

* **Entrenamiento:** se genera automáticamente desde `helpers/entrenar_modelo.py`
* **Inputs del modelo (features):**

  * `Beta`, `ROE`, `ROIC`, `PEG Ratio`, `FCF Yield`, `P/E Ratio`, `P/B Ratio`
  * `Dividend Yield`, `Debt/Equity`, `EV/EBITDA`, `Forward EPS`
  * `Forward Revenue Growth`, `Margen Futuro`, `Score Numérico Total`
* **Output (target):**

  * `retorno_12m = ((precio_12m - precio_actual) / precio_actual) × 100`

---

### 📈 Cálculo del Score y proyecciones

| Columna                | Descripción                                                           |
| ---------------------- | --------------------------------------------------------------------- |
| `Proyección 12M`       | Retorno estimado a 12 meses según `modelo_retorno.pkl`                |
| `Retorno 12M ML`       | Sinónimo de Proyección 12M, calculado con ML                          |
| `Score Final`          | Puntaje de 1 a 5 estrellas basado en métricas clave                   |
| `Score Numérico Total` | Suma de condiciones cumplidas (fundamentales, técnicas, proyecciones) |
| `Justificación Score`  | Lista textual de métricas que aportaron puntos al score               |
| `Semáforo Riesgo`      | Indicador de riesgo basado en `Beta`: 🟢 Bajo, 🟡 Medio, 🔴 Alto      |
| `Advertencia`          | Mensajes automáticos si hay riesgo alto, deuda elevada o EPS negativo |

---

## 🧠 ¿Por qué este Score es confiable y preciso?

El **Score Final (1 a 5 estrellas)** combina métricas **financieras**, **fundamentales**, **técnicas**, **estratégicas**, y **de contexto**, más un modelo predictivo opcional:

* Forward EPS, crecimiento proyectado e indicadores de margen.
* Múltiples ratios clásicos como ROE, ROIC, PEG, EV/EBITDA, etc.
* Análisis técnico (RSI, MACD, EMAs, Bollinger).
* Factores macroeconómicos como VIX y Riesgo País.
* Penalizaciones por sectores cíclicos o países con alta intervención.
* Bonus por pertenecer a sectores estratégicos (IA, energía, defensa).

---

## 🌟 Valor agregado del modelo ML

Con un modelo entrenado (`modelo_retorno.pkl`) usando archivos anteriores en `/historicos/`:

* Se predice el **retorno esperado a 12 meses**.
* Modelo: `RandomForestRegressor` (robusto y no lineal).
* Entrenamiento validado con RMSE, MAE y R².
* Se genera histograma de errores (`modelo_histograma.png`).
* El score y las métricas sirven como input del modelo.

---

## 🧪 Funcionamiento paso a paso

1. Cargás un `.csv` con tickers.
2. Se consultan múltiples fuentes (Yahoo, AV, CoinGecko, etc.).
3. Se calculan indicadores financieros, técnicos y de contexto.
4. Se asigna un **score** y proyecciones a 12 meses.
5. Si hay modelo, se predice el retorno futuro.
6. Todo se exporta a CSV para backtesting.

---

## 💡 Indicadores Calculados

* Ratios: PEG, P/E, P/B, ROE, ROIC, FCF Yield, Debt/Equity, EV/EBITDA, Dividend Yield
* Técnicos: RSI, MACD, EMA50/200, Bollinger Bands, Volumen
* Proyecciones: EPS, Revenue Growth, Precio objetivo (base, alcista, conservador)
* Score final, contexto mundial, cobertura de datos

---

## 🚦 Semáforo de Riesgo

| Color       | Condición      | Significado     |
| ----------- | -------------- | --------------- |
| 🟢 VERDE    | Beta ≤ 1       | Bajo riesgo     |
| 🟡 AMARILLO | 1 < Beta ≤ 1.5 | Riesgo moderado |
| 🔴 ROJO     | Beta > 1.5     | Riesgo alto     |

---

## ⭐ Score Financiero Final

| Score | Descripción                                          |
| ----- | ---------------------------------------------------- |
| 5/5   | Excelente: fundamentos y contexto muy favorables     |
| 4/5   | Muy Bueno: sólidos fundamentos y buenas proyecciones |
| 3/5   | Aceptable: balanceado, con advertencias              |
| 2/5   | Riesgoso: débiles fundamentos o entorno adverso      |
| 1/5   | Débil: fundamentos frágiles o sector desfavorable    |

---

## 🧮 Cómo se calcula el Score

**Puntos Positivos (suman +1 cada uno):**

* Beta ≤ 1
* Debt/Equity < 1
* EV/EBITDA < 15
* ROE > 10%, ROIC > 8%
* PEG < 1.5 o justificado
* FCF Yield > 0% (+1 adicional si > 5%)
* P/E < 20, P/B < 3
* Dividend Yield > 2%
* Subida a máximo > 40%
* Revenue Growth YoY > 15%
* EPS futuro positivo, Margen > 15%
* RSI entre 30 y 70, MACD cruzado, EMA50 > EMA200, Bollinger baja

**Bonus:**

* Contexto muy favorable: +2
* Sector estratégico: +1

**Penalizaciones:**

* P/E > 60: −1
* ROE < 0: −1
* Sector cíclico/regulado: −1

---

## 📈 Backtesting y almacenamiento

Los resultados se guardan en `./historicos/AnalisisFinal-YYYY-MM-DD_export.csv` para:

* Visualización futura
* Reentrenar modelos ML
* Medir evolución de activos

---

## 📦 Requisitos técnicos

```txt
streamlit
pandas
numpy
yfinance
requests
pycoingecko
alpha_vantage
investpy
tradingeconomics
deep-translator
openai
scikit-learn
joblib
matplotlib
plotly
seaborn
beautifulsoup4
lxml
playwright
tqdm
glob2
```

Configurar en `.streamlit/secrets.toml`:

```toml
ALPHA_VANTAGE_API_KEY = "..."
OPENAI_API_KEY = "..."
TRADINGECONOMICS_API_KEY = "..."
FINNHUB_API_KEY = "..."
FMP_API_KEY = "..."
```

---

🌟 Hecho con pasión por **\[marcelodmartini]**

---
