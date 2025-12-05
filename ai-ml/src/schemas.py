# src/schemas.py
from pydantic import BaseModel, Field

class CustomerData(BaseModel):
    customer_id: str = Field(..., description="ID único del cliente")
    monthly_charges: float = Field(..., gt=0, description="Cargos mensuales en dólares")
    total_services: int = Field(..., ge=0, description="Cantidad de servicios contratados")
    contract_type: str = Field(..., description="Tipo de contrato: Month-to-month, One year, etc.")

    class Config:
        json_schema_extra = {
            "example": {
                "customer_id": "cust_12345",
                "monthly_charges": 75.50,
                "total_services": 3,
                "contract_type": "Month-to-month"
            }
        }

class PredictionResponse(BaseModel):
    churn_probability: float
    risk_level: str
    recommended_action: str