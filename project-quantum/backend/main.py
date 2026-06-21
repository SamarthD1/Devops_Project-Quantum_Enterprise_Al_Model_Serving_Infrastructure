import os
import time
import asyncio
import datetime
from fastapi import FastAPI, Request, Response, HTTPException, status
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

from schemas import (
    LoanPredictRequest, LoanPredictResponse,
    HousePredictRequest, HousePredictResponse,
    ChurnPredictRequest, ChurnPredictResponse
)
from model_loader import ModelLoader, ModelUnavailableException
from utils.logger import setup_logger

# Initialize FastAPI App
app = FastAPI(
    title="Project Quantum AI Inference Server",
    description="Enterprise AI Model Serving Infrastructure API",
    version="1.0"
)

# Enable CORS for frontend API calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Logger and Model Loader
logger = setup_logger()
model_loader = ModelLoader()

# Prometheus Metrics Definition
HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total HTTP Requests",
    ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP Request Latency in Seconds",
    ["method", "endpoint"]
)

PREDICTIONS_TOTAL = Counter(
    "predictions_total",
    "Total Prediction Requests",
    ["model", "outcome"]
)

MODEL_STATUS = Gauge(
    "model_status",
    "Status of ML models (1 = Active, 0 = Inactive/Simulated Failure)",
    ["model"]
)

# Initialize Model Gauges
MODEL_STATUS.labels(model="loan").set(1)
MODEL_STATUS.labels(model="house").set(1)
MODEL_STATUS.labels(model="churn").set(1)

# Middleware to calculate response times and track request counts
@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    method = request.method
    endpoint = request.url.path
    
    # Do not track /metrics requests in latencies/counts to prevent spamming
    if endpoint == "/metrics":
        return await call_next(request)
        
    start_time = time.time()
    
    try:
        response = await call_next(request)
        status_code = response.status_code
    except Exception as e:
        status_code = 500
        raise e
    finally:
        latency = time.time() - start_time
        
        # Track metrics
        HTTP_REQUESTS_TOTAL.labels(method=method, endpoint=endpoint, status=status_code).inc()
        REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(latency)
        
        # Log request details in structured JSON
        extra_fields = {
            "method": method,
            "endpoint": endpoint,
            "status_code": status_code,
            "latency_seconds": round(latency, 4),
            "client_ip": request.client.host if request.client else "unknown"
        }
        
        log_msg = f"HTTP Request: {method} {endpoint} -> {status_code}"
        if status_code >= 500:
            logger.error(log_msg, extra={"extra_fields": extra_fields})
        elif status_code >= 400:
            logger.warning(log_msg, extra={"extra_fields": extra_fields})
        else:
            logger.info(log_msg, extra={"extra_fields": extra_fields})
            
    return response

# Custom Exception Handler for Model Unavailable Exception
@app.exception_handler(ModelUnavailableException)
async def model_unavailable_exception_handler(request: Request, exc: ModelUnavailableException):
    logger.error(f"Prediction failed: {str(exc)}")
    # Log details to Prom counter
    HTTP_REQUESTS_TOTAL.labels(method=request.method, endpoint=request.url.path, status=503).inc()
    return Response(
        content=f'{{"detail": "{str(exc)}"}}',
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        media_type="application/json"
    )

# --- Core API Endpoints ---

@app.get("/")
def read_root():
    return {"status": "running"}

@app.get("/health")
def health_check():
    # Return 200 if all models are loaded, otherwise return 200 or 503 depending on requirements.
    # In enterprise setups, if core models are offline, health might fail.
    # Here, we keep it simple: healthy if server is up, but report model availability.
    model_states = {
        "loan": model_loader.is_model_active("loan"),
        "house": model_loader.is_model_active("house"),
        "churn": model_loader.is_model_active("churn")
    }
    
    if not any(model_states.values()):
        return Response(
            content='{"status": "degraded", "detail": "All model endpoints are offline"}',
            status_code=status.HTTP_200_OK,
            media_type="application/json"
        )
        
    return {"status": "healthy", "models": model_states}

@app.get("/metrics", response_class=PlainTextResponse)
def metrics():
    # Update Gauge values before yielding metrics
    MODEL_STATUS.labels(model="loan").set(1 if model_loader.is_model_active("loan") else 0)
    MODEL_STATUS.labels(model="house").set(1 if model_loader.is_model_active("house") else 0)
    MODEL_STATUS.labels(model="churn").set(1 if model_loader.is_model_active("churn") else 0)
    
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# --- Prediction APIs ---

@app.post("/predict/loan", response_model=LoanPredictResponse)
def predict_loan(payload: LoanPredictRequest):
    try:
        prediction = model_loader.predict_loan(
            income=payload.income,
            credit_score=payload.credit_score,
            loan_amount=payload.loan_amount
        )
        version = model_loader.model_versions["loan"]
        timestamp = datetime.datetime.utcnow().isoformat() + "Z"
        
        # Track metrics
        PREDICTIONS_TOTAL.labels(model="loan", outcome=prediction).inc()
        
        logger.info(f"Successful loan approval prediction: {prediction}", extra={
            "extra_fields": {
                "model": "loan",
                "version": version,
                "input": payload.dict(),
                "output": prediction
            }
        })
        
        return LoanPredictResponse(
            prediction=prediction,
            model_version=version,
            timestamp=timestamp
        )
    except ModelUnavailableException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in loan prediction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing loan prediction."
        )

@app.post("/predict/house", response_model=HousePredictResponse)
def predict_house(payload: HousePredictRequest):
    try:
        prediction = model_loader.predict_house(
            area=payload.area,
            bedrooms=payload.bedrooms,
            bathrooms=payload.bathrooms
        )
        version = model_loader.model_versions["house"]
        timestamp = datetime.datetime.utcnow().isoformat() + "Z"
        
        PREDICTIONS_TOTAL.labels(model="house", outcome="price_computed").inc()
        
        logger.info(f"Successful house price prediction: ${prediction:,.2f}", extra={
            "extra_fields": {
                "model": "house",
                "version": version,
                "input": payload.dict(),
                "output": prediction
            }
        })
        
        return HousePredictResponse(
            prediction=prediction,
            model_version=version,
            timestamp=timestamp
        )
    except ModelUnavailableException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in house price prediction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing house price prediction."
        )

@app.post("/predict/churn", response_model=ChurnPredictResponse)
def predict_churn(payload: ChurnPredictRequest):
    try:
        prediction = model_loader.predict_churn(
            tenure=payload.tenure,
            monthly_charges=payload.monthly_charges,
            contract_type=payload.contract_type
        )
        version = model_loader.model_versions["churn"]
        timestamp = datetime.datetime.utcnow().isoformat() + "Z"
        
        PREDICTIONS_TOTAL.labels(model="churn", outcome=prediction).inc()
        
        logger.info(f"Successful customer churn prediction: {prediction}", extra={
            "extra_fields": {
                "model": "churn",
                "version": version,
                "input": payload.dict(),
                "output": prediction
            }
        })
        
        return ChurnPredictResponse(
            prediction=prediction,
            model_version=version,
            timestamp=timestamp
        )
    except ModelUnavailableException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in customer churn prediction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing customer churn prediction."
        )

# --- Failure Simulation APIs ---

@app.post("/simulate/high-latency")
async def simulate_high_latency():
    logger.warning("Simulation initiated: Injecting 5 seconds of latency...")
    await asyncio.sleep(5)
    logger.info("Simulation completed: Latency injection resolved.")
    return {"message": "Success", "injected_latency_seconds": 5}

@app.post("/simulate/error")
def simulate_error():
    logger.error("Simulation initiated: Intentional 500 error triggered.")
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Intentional server error triggered for monitoring demonstration."
    )

@app.post("/simulate/model-failure")
def simulate_model_failure(model: str, action: str):
    """
    Simulates model failure by toggling a model's state.
    - model: 'loan', 'house', or 'churn'
    - action: 'disable' or 'enable'
    """
    if model not in ["loan", "house", "churn"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid model name. Choose from 'loan', 'house', or 'churn'."
        )
        
    if action == "disable":
        model_loader.toggle_model_status(model, enabled=False)
        MODEL_STATUS.labels(model=model).set(0)
        return {"status": "success", "message": f"Model '{model}' is now OFFLINE."}
    elif action == "enable":
        model_loader.toggle_model_status(model, enabled=True)
        MODEL_STATUS.labels(model=model).set(1)
        return {"status": "success", "message": f"Model '{model}' is now ONLINE."}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid action. Choose 'disable' or 'enable'."
        )
