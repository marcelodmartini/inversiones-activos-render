# Análisis de Activos Financieros con Fallback Inteligente y Score Unificado

Este `README.md` explica en detalle el funcionamiento de la aplicación Streamlit `Análisis de Activos Financieros`, que permite evaluar acciones, bonos y criptomonedas mediante indicadores fundamentales, técnicos y contexto macroeconómico, generando un Score Final inteligente.

---

## 📊 Descripción de Columnas del Informe

| Columna                      | Descripción                                                                             |
| ---------------------------- | --------------------------------------------------------------------------------------- |
| **Score Final**              | Calificación de 1 a 5 estrellas según métricas fundamentales, técnicas y contexto.      |
| **Score Numérico Total**     | Puntaje acumulado numérico basado en \~20 condiciones.                                  |
| **Justificación Score**      | Lista textual de los factores que aportaron al score (ej: "ROE > 10%", "MACD cruzado"). |
| **Semáforo Riesgo**          | Riesgo del activo según su Beta: 🟢 Bajo, 🟡 Medio, 🔴 Alto.                            |
| **Ticker**                   | Código identificador del activo (ej: AAPL, AL30D, BTC).                                 |
| **Fuente**                   | Fuente de datos utilizada: Yahoo, Alpha Vantage, CoinGecko, Investpy, etc.              |
| **Mínimo / Máximo / Actual** | Precios registrados en el período seleccionado.                                         |
| **% Subida a Máx**           | Potencial de revalorización al máximo anterior.                                         |
| **Tipo**                     | Clasificación: "Acción", "Bono", "Criptomoneda".                                        |
| **Advertencia**              | Indica si faltan métricas fundamentales.                                                |
| **País**                     | País de origen del activo.                                                              |
| **PEG, P/E, P/B Ratio**      | Ratios de valuación fundamentales.                                                      |
| **ROE, ROIC**                | Indicadores de rentabilidad.                                                            |
| **FCF Yield**                | Rendimiento de flujo de caja libre.                                                     |
| **Debt/Equity**              | Nivel de apalancamiento financiero.                                                     |
| **EV/EBITDA**                | Ratio empresa / beneficios.                                                             |
| **Dividend Yield**           | Rentabilidad por dividendos.                                                            |
| **Beta**                     | Volatilidad relativa respecto al mercado.                                               |
| **Contexto**                 | Breve resumen de la empresa, traducido.                                                 |
| **CAGR 3Y**                  | Tasa de crecimiento anual compuesta en 3 años.                                          |
| **Volumen Saludable**        | Si el volumen supera el promedio de 20 días.                                            |
| **Cobertura**                | Métricas obtenidas / disponibles. Ej: 8/10                                              |
| **VIX / Riesgo País**        | Indicadores de contexto macro.                                                          |
| **Contexto Global**          | Evaluación del entorno económico: MUY FAVORABLE, MODERADO o ADVERSO.                    |

---

## 🧠 ¿Por qué este Score es confiable y preciso?

El cálculo del **Score Final (1 a 5 estrellas)** se basa en una combinación avanzada de métricas **financieras**, **fundamentales**, **técnicas**, **proyecciones a futuro**, **riesgos regulatorios**, **contexto macroeconómico global**, e incluso **análisis sectorial estratégico**.

### ✅ ¿Qué lo hace exacto?

- **Cobertura integral de 40+ variables cuantitativas** extraídas de múltiples fuentes confiables (Yahoo Finance, FMP, Finnhub, TradingEconomics, CoinGecko, etc.).
- **Proyecciones Forward**: el modelo evalúa datos como *EPS futuro*, *crecimiento proyectado de ingresos*, y *margen futuro neto* para anticipar escenarios.
- **Métricas técnicas** como RSI, MACD, EMA y Bandas de Bollinger aportan señales de momentum, soportes y tendencias.
- **Penalizaciones inteligentes** por sectores cíclicos, exposición a regulaciones o desbalance financiero.
- **Bonus por contexto macro** según VIX y Riesgo País real, lo cual permite adaptar el score al entorno global.
- **Modelado ML opcional**: el script incluye una interfaz para incorporar predicciones con modelos entrenados externamente (`modelo_retorno.pkl`), para mejorar la exactitud predictiva.
- **Justificaciones trazables**: cada Score incluye una lista clara de condiciones que explican por qué subió o bajó, lo que permite hacer *backtesting transparente*.
- **Soporte para activos diversos**: acciones, bonos, CEDEARs y criptomonedas pueden ser evaluados con precisión en un mismo panel.

### 🎯 Ventajas sobre otros sistemas

| Característica                       | Este Score Unificado        | Rating Tradicional |
|-------------------------------------|-----------------------------|--------------------|
| Datos técnicos + fundamentales      | ✅ Integrado                | ❌ No combinados   |
| Forward + Histórico                 | ✅ Sí                       | ❌ Parcial         |
| Sector estratégico + contexto país  | ✅ Considerado              | ❌ Ignorado        |
| Transparencia de cálculo            | ✅ Justificaciones visibles | ❌ Caja negra       |
| Backtesting con CSV diario          | ✅ Guardado automático      | ❌ No aplica        |

---


## 📅 Cómo usar la app

1. Subí un archivo `.csv` con una columna `Ticker`.
2. Seleccioná un rango de fechas.
3. La app consultará automáticamente varias fuentes financieras.

---

## 🔹 Fuentes de datos utilizadas

* Yahoo Finance
* Alpha Vantage
* CoinGecko
* Investpy
* Finnhub
* Financial Modeling Prep (FMP)
* BYMA, Rava, IAMC (para bonos argentinos)

---

## 📊 Indicadores Calculados

* PEG Ratio, P/E, P/B
* ROE, ROIC, FCF Yield
* Debt/Equity, EV/EBITDA
* Dividend Yield, Beta
* CAGR 3Y (Crecimiento anual compuesto)
* Forward EPS / Revenue Growth
* RSI, MACD, EMA50, EMA200, Bollinger Bands
* Volumen saludable (comparado a 20 ruedas)

---

## 🛑 Semáforo de Riesgo

| Color       | Condición      | Significado     |
| ----------- | -------------- | --------------- |
| 🟢 VERDE    | Beta ≤ 1       | Bajo riesgo     |
| 🟡 AMARILLO | 1 < Beta ≤ 1.5 | Riesgo moderado |
| 🔴 ROJO     | Beta > 1.5     | Riesgo alto     |

---

## 💡 Score Financiero Final (1 a 5)

| Score | Nivel     | Descripción                                         |
| ----- | --------- | --------------------------------------------------- |
| 5/5   | Excelente | Alta calidad, fundamentos y contexto muy favorables |
| 4/5   | Muy Bueno | Muy buenos fundamentales y buenas proyecciones      |
| 3/5   | Aceptable | Balanceado, pero con advertencias                   |
| 2/5   | Riesgoso  | Fundamentos débiles, volatilidad o contexto malo    |
| 1/5   | Débil     | Score bajo o sector desfavorable                    |

---

## 📊 Cómo se calcula el Score

### Puntúa cada uno de los siguientes criterios:

* **Beta ≤ 1**
* **Debt/Equity < 1**
* **EV/EBITDA < 15**
* **ROE > 10%**, **ROIC > 8%**
* **PEG Ratio < 1.5** o justificado
* **FCF Yield > 0% (+1) y >5% (+1)**
* **P/E < 20**, **P/B < 3**
* **Dividend Yield > 2%**
* **% Subida a Máximo > 40%**
* **Revenue Growth YoY > 15%**
* **Crecimiento futuro (Forward Revenue > 10%)**
* **EPS futuro positivo**, **Margen Futuro > 15%**

### Indicadores Técnicos que suman puntos

* RSI saludable (30 < RSI < 70)
* MACD cruzado al alza
* EMA50 > EMA200
* Precio debajo de Banda de Bollinger inferior

### Bonus de contexto y sector

* **Contexto Global muy favorable: +2**, moderado: +1
* **Sector estratégico** (IA, energía, defensa): +1

### Penalizaciones

* **P/E > 60** o **ROE negativo**: −1
* **Sector cíclico o con riesgo regulatorio por país**: −1 o más

---

## 📈 Justificación del Score y Backtesting

Cada activo incluye la columna `Justificación Score` con el detalle exacto de los puntos sumados o restados.
Esto permite auditar el score y entender por qué un activo fue recomendado o no.

El archivo con los scores finales es guardado automáticamente en `/historicos/` para permitir el backtesting.

---

## 🛋 Requisitos

```txt
streamlit
yfinance
tradingeconomics
pandas
investpy
requests
pycoingecko
alpha_vantage
deep-translator
joblib
```

## 🔐 Variables en `.streamlit/secrets.toml`

```toml
ALPHA_VANTAGE_API_KEY = "..."
FINNHUB_API_KEY = "..."
FMP_API_KEY = "..."
TRADINGECONOMICS_API_KEY = "..."
OPENAI_API_KEY = "..."
```

---

## 🌟 Hecho con pasión por \[marcelodmartini]
