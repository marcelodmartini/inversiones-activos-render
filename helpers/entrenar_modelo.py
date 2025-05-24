import pandas as pd
import yfinance as yf
import glob
import os
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib
import matplotlib.pyplot as plt

# Configuración
CARPETA_HISTORICOS = os.path.join(os.path.dirname(__file__), "..", "historicos")
ARCHIVO_SALIDA_MODELO = "modelo_retorno.pkl"
ARCHIVO_SALIDA_RMSE = "modelo_rmse.txt"
ARCHIVO_HISTOGRAMA = "modelo_histograma.png"
MODELO_ACTIVO = "rf"  # "lr" para LinearRegression, "rf" para RandomForest

features_completos = [
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
    except Exception as e:
        print(f"⚠️ Error obteniendo precio 12M para {ticker}: {e}")
        return None

# Cargar todos los CSV de historicos y generar dataset
datos = []
for archivo in glob.glob(os.path.join(CARPETA_HISTORICOS, "AnalisisFinal-*_export.csv")):
    try:
        fecha_base_str = os.path.basename(archivo).split("-")[1]
        df = pd.read_csv(archivo)
        print(f"📄 Procesando archivo: {archivo} (Filas: {len(df)})")
        print("→ NaNs por columna:")
        print(df[features_completos].isna().sum())

        for _, fila in df.iterrows():
            if fila.get("Tipo") == "Bono":
                continue
            ticker = fila.get("Ticker")
            actual = fila.get("Actual")
            if pd.isna(ticker) or pd.isna(actual) or actual <= 0:
                continue
            precio_12m = obtener_precio_a_12m(ticker, fecha_base_str)
            if precio_12m is None:
                print(f"🔸 Sin precio futuro para {ticker}")
                continue
            retorno_12m = (precio_12m - actual) / actual * 100
            fila_features = {col: fila.get(col) for col in features_completos}
            fila_features["retorno_12m"] = retorno_12m
            datos.append(fila_features)
    except Exception as e:
        print(f"⚠️ Error procesando {archivo}: {e}")

df_modelo = pd.DataFrame(datos)
print(f"✅ Registros válidos para entrenamiento: {len(df_modelo)}")

if df_modelo.empty:
    raise ValueError("❌ No se pudo generar dataset de entrenamiento válido. Verificá los archivos en /historicos/")

# Verificar cobertura antes de imputar
print("→ Filas con al menos 8 columnas completas:", (df_modelo[features_completos].notna().sum(axis=1) >= 8).sum())

# Filtro extra: evitar valores negativos extremos en retorno objetivo
df_modelo = df_modelo[df_modelo["retorno_12m"] > -100]

# Imputación con la media
for col in features_completos:
    if col in df_modelo.columns and df_modelo[col].isnull().any():
        media_col = df_modelo[col].mean()
        df_modelo[col] = df_modelo[col].fillna(media_col)

# Entrenamiento
X = df_modelo[features_completos]
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
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"✅ Modelo entrenado. RMSE: {rmse:.2f} | MAE: {mae:.2f} | R2: {r2:.2f}")
joblib.dump(modelo, ARCHIVO_SALIDA_MODELO)
print(f"📁 Modelo guardado en: {ARCHIVO_SALIDA_MODELO}")

# Guardar RMSE
try:
    with open(ARCHIVO_SALIDA_RMSE, "w") as f:
        f.write(f"RMSE: {rmse:.2f}\nMAE: {mae:.2f}\nR2: {r2:.2f}")
    print(f"📄 RMSE guardado en: {ARCHIVO_SALIDA_RMSE}")
except Exception as e:
    print(f"❌ Error al guardar RMSE: {e}")

# Histograma de errores
errores = y_test - y_pred
plt.figure(figsize=(10, 6))
plt.hist(errores, bins=30, edgecolor='k')
plt.title("Histograma de errores del modelo (Predicción - Real)")
plt.xlabel("Error de predicción")
plt.ylabel("Frecuencia")
plt.grid(True)
plt.tight_layout()
try:
    plt.savefig(ARCHIVO_HISTOGRAMA)
    print(f"📊 Histograma guardado en: {ARCHIVO_HISTOGRAMA}")
except Exception as e:
    print(f"❌ Error al guardar histograma: {e}")

# Path útil
print("📂 Path actual:", os.getcwd())
print("📂 RMSE file path:", os.path.abspath(ARCHIVO_SALIDA_RMSE))
print("📂 Histograma file path:", os.path.abspath(ARCHIVO_HISTOGRAMA))
