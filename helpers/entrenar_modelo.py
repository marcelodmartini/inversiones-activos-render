import pandas as pd
import yfinance as yf
import glob
import os
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import joblib
import matplotlib.pyplot as plt

# Configuración
CARPETA_HISTORICOS = os.path.join(os.path.dirname(__file__), "..", "historicos")
ARCHIVO_SALIDA_MODELO = "modelo_retorno.pkl"
ARCHIVO_SALIDA_RMSE = "modelo_rmse.txt"
ARCHIVO_HISTOGRAMA = "modelo_histograma.png"
MODELO_ACTIVO = "rf"  # "lr" para LinearRegression, "rf" para RandomForest

features = [
    "Beta", "ROE", "ROIC", "PEG Ratio", "FCF Yield", "P/E Ratio", "P/B Ratio",
    "Dividend Yield", "Debt/Equity", "EV/EBITDA", "Forward EPS",
    "Forward Revenue Growth", "Margen Futuro", "Score Numérico Total"
]

def obtener_precio_a_12m(ticker, fecha_base_str):
    try:
        fecha_base = datetime.strptime(fecha_base_str, "%Y-%m-%d")
        fecha_12m = fecha_base + timedelta(days=365)
        df = yf.Ticker(ticker).history(
            start=fecha_12m.strftime("%Y-%m-%d"),
            end=(fecha_12m + timedelta(days=5)).strftime("%Y-%m-%d")
        )
        return df['Close'].iloc[0] if not df.empty else None
    except:
        return None

# Cargar todos los CSV de historicos y generar dataset
datos = []
for archivo in glob.glob(os.path.join(CARPETA_HISTORICOS, "AnalisisFinal-*-export.csv")):
    fecha_base_str = os.path.basename(archivo).split("-")[1]
    df = pd.read_csv(archivo)
    for _, fila in df.iterrows():
        if fila.get("Tipo") == "Bono":
            continue
        ticker = fila.get("Ticker")
        actual = fila.get("Actual")
        if pd.isna(ticker) or pd.isna(actual):
            continue
        precio_12m = obtener_precio_a_12m(ticker, fecha_base_str)
        if precio_12m is None:
            continue
        retorno_12m = (precio_12m - actual) / actual * 100
        fila_features = {col: fila.get(col) for col in features}
        if all(pd.notna(v) for v in fila_features.values()):
            fila_features["retorno_12m"] = retorno_12m
            datos.append(fila_features)

# Entrenamiento
df_modelo = pd.DataFrame(datos)
X = df_modelo[features]
y = df_modelo["retorno_12m"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

if MODELO_ACTIVO == "rf":
    modelo = RandomForestRegressor(n_estimators=100, random_state=42)
    print("🔍 Usando modelo: RandomForestRegressor")
else:
    modelo = LinearRegression()
    print("🔍 Usando modelo: LinearRegression")

modelo.fit(X_train, y_train)
y_pred = modelo.predict(X_test)
rmse = mean_squared_error(y_test, y_pred, squared=False)
print(f"✅ Modelo entrenado. RMSE: {rmse:.2f}")

joblib.dump(modelo, ARCHIVO_SALIDA_MODELO)
print(f"📁 Modelo guardado en: {ARCHIVO_SALIDA_MODELO}")

# Guardar RMSE
with open(ARCHIVO_SALIDA_RMSE, "w") as f:
    f.write(f"{rmse:.2f}")

# Histograma de errores
errores = y_test - y_pred
plt.figure(figsize=(10, 6))
plt.hist(errores, bins=30, edgecolor='k')
plt.title("Histograma de errores del modelo (Predicción - Real)")
plt.xlabel("Error de predicción")
plt.ylabel("Frecuencia")
plt.grid(True)
plt.tight_layout()
plt.savefig(ARCHIVO_HISTOGRAMA)
print(f"📊 Histograma guardado en: {ARCHIVO_HISTOGRAMA}")
