from pydantic import BaseModel, Field

class ChurnPredictRequest(BaseModel):
    tenure: int = Field(..., description="Tenure in months", example=12, ge=0)
    monthly_charges: float = Field(..., description="Monthly subscription charges", example=65.0, ge=0)
    contract_type: int = Field(..., description="Contract type (0=Month-to-month, 1=One year, 2=Two year)", example=1, ge=0, le=2)

class ChurnPredictResponse(BaseModel):
    prediction: str = Field(..., description="Prediction ('Churn' or 'No Churn')", example="No Churn")
    model_version: str = Field(..., description="Model version used for inference", example="1.0")
    timestamp: str = Field(..., description="RFC3339 Timestamp of the prediction", example="2026-06-21T10:00:00Z")
