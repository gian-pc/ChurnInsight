# src/train_model.py
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib
import os

# Asegurarnos de que existe la carpeta models
if not os.path.exists("models"):
    os.makedirs("models")

print("🏗️ Construyendo modelo optimizado para producción...")

# 1. Generar Dataset Compatible con la API
# Usamos EXACTAMENTE los nombres que definimos en schemas.py
np.random.seed(42)
n = 1000

data = {
    'monthly_charges': np.random.uniform(20, 120, n),
    'total_services': np.random.randint(1, 5, n),
    # 0: Month-to-month, 1: One year, 2: Two year
    'contract_type_code': np.random.choice([0, 1, 2], n)
}

df = pd.DataFrame(data)


# Lógica de negocio simulada (Reglas del juego)
# Si paga mucho (>80) y tiene contrato mensual (0), se va (1).
def get_churn(row):
    score = 0
    if row['monthly_charges'] > 80: score += 3
    if row['contract_type_code'] == 0: score += 4
    if row['total_services'] == 1: score += 1

    # Probabilidad basada en el score
    prob = score / 10.0
    return 1 if np.random.random() < prob else 0


df['churn'] = df.apply(get_churn, axis=1)

# 2. Entrenar Modelo
X = df[['monthly_charges', 'total_services', 'contract_type_code']]
y = df['churn']

print(f"📊 Entrenando con {n} datos simulados...")
model = RandomForestClassifier(n_estimators=50, random_state=42)
model.fit(X, y)

# 3. Guardar el nuevo cerebro
joblib.dump(model, "models/churn_model.pkl")
print("✅ ¡Modelo 'churn_model.pkl' actualizado y sincronizado con la API!")