# Análisis de Activos Financieros con Fallback Inteligente y Score Unificado

Este `README.md` explica en detalle el funcionamiento de la aplicación Streamlit `Análisis de Activos Financieros`, que permite evaluar acciones, bonos y criptomonedas mediante indicadores fundamentales, técnicos, contexto macroeconómico y proyecciones de retorno con modelos de Machine Learning, generando un Score Final inteligente.

---

## 📊 Descripción de Columnas del Informe

| Columna                      | Descripción                                                                        |
| ---------------------------- | ---------------------------------------------------------------------------------- |
| **Score Final**              | Calificación de 1 a 5 estrellas según métricas fundamentales, técnicas y contexto. |
| **Score Numérico Total**     | Puntaje acumulado numérico basado en ~20 condiciones.                             |
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
| **Recomendación**            | Sugerencia final: ✅ Comprar, 🙀 Revisar, ❌ Evitar.                                 |

---

## 🧠 ¿Por qué este Score es confiable y preciso?

El **Score Final (1 a 5 estrellas)** combina métricas **financieras**, **fundamentales**, **técnicas**, **estratégicas**, y **de contexto** con un modelo predictivo de retorno a 12 meses opcional usando Machine Learning:

### ✅ Elementos clave

* **Proyecciones Forward**: Forward EPS, crecimiento de ingresos, margen futuro.
* **Precio objetivo estimado**: PER proyectado en escenarios conservador/base/alcista.
* **Señales técnicas**: RSI, MACD, EMA, Bollinger Bands.
* **Riesgo macro**: VIX + Riesgo País (desde TradingEconomics o fallback local).
* **Penalizaciones y bonus**: Por sector cíclico, regulaciones o sector estratégico.
* **Predicción ML (opcional)**: si se entrena un modelo con `historicos/`, se obtiene `modelo_retorno.pkl`, que estima retorno 12M basado en features reales.

---

## 🌟 Valor agregado del modelo ML

Con un archivo `modelo_retorno.pkl` entrenado sobre los scores anteriores (archivos `.csv` en `/historicos/`):

* El sistema aprende a **predecir la rentabilidad esperada a 12 meses** de nuevos activos.
* Se utiliza `RandomForestRegressor` como modelo base por robustez y performance.
* Input del modelo: indicadores como ROE, FCF Yield, Beta, PEG, Forward EPS, Score total, etc.
* Output: estimación en `%` de retorno proyectado.
* Se guarda también el RMSE del modelo (`modelo_rmse.txt`) y un histograma de errores (`modelo_histograma.png`) para análisis visual.

---

## 🧪 Funcionamiento paso a paso

1. **Carga de datos**: el usuario sube un archivo `.csv` con tickers o se carga el último archivo histórico.
2. **Consulta de fuentes**: se prueban múltiples APIs y fuentes (Yahoo, Alpha Vantage, CoinGecko, Investpy, BYMA) para cada ticker.
3. **Cálculo de métricas**: se extraen más de 40 indicadores financieros, técnicos y de contexto.
4. **Cálculo de Score**: se asigna un score numérico y textual justificado, con bonus y penalizaciones según sector y entorno.
5. **Predicción ML (opcional)**: si hay modelo entrenado, se predice el retorno esperado a 12 meses.
6. **Visualización**: se muestran tablas, radar de scores, gráficos de precios y métricas del modelo.
7. **Exportación**: se guarda automáticamente el resultado como `.csv` en `/historicos/`.

---

## 📅 Cómo usar la app

1. Subí un archivo `.csv` con una columna `Ticker`.
2. Seleccioná un rango de fechas.
3. La app consulta varias fuentes (Yahoo, Alpha Vantage, CoinGecko, etc.).
4. Se calculan métricas, score y proyecciones, y se guarda el resultado en `/historicos/`.
5. Podés descargar el informe final en CSV.
6. Podés reentrenar el modelo con un botón o automáticamente al inicio.

---

## 💡 Indicadores Calculados

* PEG Ratio, P/E, P/B
* ROE, ROIC, FCF Yield
* Debt/Equity, EV/EBITDA
* Dividend Yield, Beta
* CAGR 3Y (Crecimiento anual compuesto)
* Forward EPS / Revenue Growth
* RSI, MACD, EMA50, EMA200, Bollinger Bands
* Volumen saludable (comparado a 20 ruedas)
* Precio objetivo (Base, Alcista, Conservador)
* Proyección de retorno 12M (%) (ML opcional)

---

## 🚦 Semáforo de Riesgo

| Color       | Condición      | Significado     |
| ----------- | -------------- | --------------- |
| 🟢 VERDE    | Beta ≤ 1       | Bajo riesgo     |
| 🟡 AMARILLO | 1 < Beta ≤ 1.5 | Riesgo moderado |
| 🔴 ROJO     | Beta > 1.5     | Riesgo alto     |

---

## ⭐ Score Financiero Final (1 a 5)

| Score | Nivel     | Descripción                                         |
| ----- | --------- | --------------------------------------------------- |
| 5/5   | Excelente | Alta calidad, fundamentos y contexto muy favorables |
| 4/5   | Muy Bueno | Muy buenos fundamentales y buenas proyecciones      |
| 3/5   | Aceptable | Balanceado, pero con advertencias                   |
| 2/5   | Riesgoso  | Fundamentos débiles, volatilidad o contexto malo    |
| 1/5   | Débil     | Score bajo o sector desfavorable                    |

---

## 🧮 Cómo se calcula el Score

### Puntos positivos

* Beta ≤ 1
* Debt/Equity < 1
* EV/EBITDA < 15
* ROE > 10%, ROIC > 8%
* PEG < 1.5 o justificado
* FCF Yield > 0% (+1) y > 5% (+1)
* P/E < 20, P/B < 3
* Dividend Yield > 2%
* % Subida a Máximo > 40%
* Revenue Growth YoY > 15%
* Forward Revenue > 10%
* EPS futuro positivo, Margen futuro > 15%
* RSI saludable, MACD cruzado, EMA50 > EMA200, Bollinger baja

### Bonus y penalizaciones

* Contexto MUY FAVORABLE: +2 | MODERADO: +1
* Sector estratégico: +1 (IA, defensa, energía, cloud)
* P/E > 60 o ROE negativo: −1
* Sector cíclico/regulatorio: −1

---

## 📈 Backtesting y almacenamiento

Todos los resultados se guardan en `./historicos/AnalisisFinal-YYYY-MM-DD_export.csv` para
permitir backtesting o reentrenamiento del modelo ML (`modelo_retorno.pkl`).

---

## 📦 Requisitos

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

🔐 Variables en .streamlit/secrets.toml
ALPHA_VANTAGE_API_KEY = "..."
OPENAI_API_KEY = "..."
TRADINGECONOMICS_API_KEY = "..."
FINNHUB_API_KEY = "..."
FMP_API_KEY = "..."

🌟 Hecho con pasión por [marcelodmartini]
