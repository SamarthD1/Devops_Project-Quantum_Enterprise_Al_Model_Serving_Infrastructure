from pydantic import BaseModel, Field

class HousePredictRequest(BaseModel):
    area: float = Field(..., description="House area in square feet", example=1200.0, gt=0)
    bedrooms: int = Field(..., description="Number of bedrooms", example=3, ge=0)
    bathrooms: float = Field(..., description="Number of bathrooms", example=2.0, ge=0)

class HousePredictResponse(BaseModel):
    prediction: float = Field(..., description="Predicted house price in USD", example=550000.0)
    model_version: str = Field(..., description="Model version used for inference", example="1.0")
    timestamp: str = Field(..., description="RFC3339 Timestamp of the prediction", example="2026-06-21T10:00:00Z")
