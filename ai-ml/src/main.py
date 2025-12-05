# src/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.schemas import CustomerData, PredictionResponse
import random  # Placeholder temporal hasta que carguemos el modelo real

app = FastAPI(
    title="ChurnInsight AI Engine",
    description="Microservicio de IA para predicción de fuga de clientes",
    version="1.0.0"
)

# --- Configuración CORS (Vital para conectar con Next.js) ---
origins = [
    "http://localhost:3000",  # Tu frontend local
    "http://localhost:8080",  # Tu backend Spring Boot
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Endpoints ---

@app.get("/")
def root():
    return {"message": "ChurnInsight AI Engine is running 🚀"}


@app.get("/health")
def health_check():
    return {"status": "active", "service": "ai-engine"}


@app.post("/api/predict", response_model=PredictionResponse)
def predict_churn(data: CustomerData):
    # TODO: Aquí cargaremos tu modelo .pkl real más adelante.
    # Por ahora simulamos una predicción para probar el flujo.

    fake_prob = random.uniform(0.1, 0.9)
    risk = "High" if fake_prob > 0.7 else "Low"

    return {
        "churn_probability": round(fake_prob, 2),
        "risk_level": risk,
        "recommended_action": "Offer Discount" if risk == "High" else "Maintain Service"
    }