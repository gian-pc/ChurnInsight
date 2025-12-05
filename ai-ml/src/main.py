# src/main.py
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.schemas import CustomerData, PredictionResponse
import os

app = FastAPI(
    title="ChurnInsight AI Engine",
    description="Microservicio de IA para predicción de fuga de clientes",
    version="1.0.0"
)

# --- Configuración CORS (Vital para conectar con el Frontend) ---
origins = [
    "http://localhost:3000",  # Frontend Next.js
    "http://localhost:8080",  # Backend Spring Boot
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Cargar el Modelo (.pkl) al Iniciar ---
# Nota: Asumimos que el modelo está en ai-ml/models/churn_model.pkl
MODEL_PATH = "models/churn_model.pkl"
model = None

try:
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        print(f"✅ Modelo cargado exitosamente desde {MODEL_PATH}")
    else:
        print(f"⚠️ ALERTA: No se encontró el modelo en {MODEL_PATH}. La API fallará si intentas predecir.")
except Exception as e:
    print(f"❌ Error al cargar el modelo: {e}")


# --- Helpers ---
def preprocess_input(data: CustomerData) -> pd.DataFrame:
    """
    Transforma los datos que llegan de la API al formato que espera el modelo.
    """
    # Mapeo simple: Convertir el texto del contrato a números
    # IMPORTANTE: Esto debe coincidir con cómo se entrenó el modelo.
    # Si tu modelo se entrenó con LabelEncoder, esto es una aproximación.
    contract_mapping = {
        "Month-to-month": 0,
        "One year": 1,
        "Two year": 2
    }

    contract_code = contract_mapping.get(data.contract_type, 0)  # Default a 0 (Riesgo alto) si no coincide

    # Crear el DataFrame con las columnas exactas
    input_df = pd.DataFrame([{
        'monthly_charges': data.monthly_charges,
        'total_services': data.total_services,
        'contract_type_code': contract_code
    }])

    return input_df


# --- Endpoints ---

@app.get("/")
def root():
    return {"message": "ChurnInsight AI Engine is running 🚀"}


@app.get("/health")
def health_check():
    status = "active" if model else "degraded (model not loaded)"
    return {"status": status, "service": "ai-engine"}


@app.post("/api/predict", response_model=PredictionResponse)
def predict_churn(data: CustomerData):
    if not model:
        raise HTTPException(status_code=503, detail="El modelo de IA no está cargado.")

    try:
        # 1. Preprocesar datos
        features = preprocess_input(data)

        # 2. Realizar inferencia (Predicción)
        # predict_proba devuelve array: [[prob_no_churn, prob_churn]]
        # Usamos [0][1] para obtener la probabilidad de '1' (que se vaya)
        prediction_prob = model.predict_proba(features)[0][1]

        # 3. Determinar riesgo
        risk_level = "High" if prediction_prob > 0.6 else "Low"
        if prediction_prob > 0.85: risk_level = "Critical"

        # 4. Generar recomendación automática
        actions = {
            "Critical": "Contactar inmediatamente y ofrecer 20% descuento.",
            "High": "Ofrecer mejora de plan o servicio adicional gratis.",
            "Low": "Mantener monitoreo estándar."
        }

        return {
            "churn_probability": round(prediction_prob, 2),
            "risk_level": risk_level,
            "recommended_action": actions.get(risk_level, "Sin acción requerida")
        }

    except Exception as e:
        # Si el modelo falla (ej. columnas diferentes), mostramos el error
        print(f"Error detallado: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del modelo: {str(e)}")