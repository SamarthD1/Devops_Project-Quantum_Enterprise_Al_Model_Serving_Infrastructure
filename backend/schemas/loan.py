from pydantic import BaseModel, Field

class LoanPredictRequest(BaseModel):
    income: float = Field(..., description="Annual income of the applicant", example=50000.0)
    credit_score: int = Field(..., description="Credit score of the applicant (300-850)", example=750, ge=300, le=850)
    loan_amount: float = Field(..., description="Requested loan amount", example=100000.0)

class LoanPredictResponse(BaseModel):
    prediction: str = Field(..., description="Decision ('Approved' or 'Rejected')", example="Approved")
    model_version: str = Field(..., description="Model version used for inference", example="1.0")
    timestamp: str = Field(..., description="RFC3339 Timestamp of the prediction", example="2026-06-21T10:00:00Z")
