import os
import joblib
import pandas as pd
import logging

logger = logging.getLogger("quantum_backend")

class ModelUnavailableException(Exception):
    """Raised when a machine learning model is temporarily disabled or offline."""
    pass

class ModelLoader:
    def __init__(self):
        self.models_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
        self.models = {}
        # Stores models that have been simulated as failed/offline
        self.disabled_models = set()
        self.model_versions = {
            "loan": "v1.0",
            "house": "v1.0",
            "churn": "v1.0"
        }
        self.load_all_models()

    def load_all_models(self):
        """Loads all serialized models from the models directory."""
        model_files = {
            "loan": "loan_model.pkl",
            "house": "house_model.pkl",
            "churn": "churn_model.pkl"
        }
        
        for name, filename in model_files.items():
            path = os.path.join(self.models_dir, filename)
            if os.path.exists(path):
                try:
                    self.models[name] = joblib.load(path)
                    logger.info(f"Successfully loaded model: {name} from {path}")
                except Exception as e:
                    logger.error(f"Failed to load model {name} from {path}: {str(e)}")
            else:
                logger.warning(f"Model file not found: {path}. Run train_models.py to create it.")

    def toggle_model_status(self, model_name: str, enabled: bool):
        """Disables or enables a model for simulation purposes."""
        if not enabled:
            self.disabled_models.add(model_name)
            logger.warning(f"Simulating failure: Model '{model_name}' has been disabled/turned offline.")
        else:
            self.disabled_models.discard(model_name)
            logger.info(f"Simulating recovery: Model '{model_name}' has been re-enabled/turned online.")

    def is_model_active(self, model_name: str) -> bool:
        """Returns True if the model is active and loaded, False otherwise."""
        return model_name in self.models and model_name not in self.disabled_models

    def predict_loan(self, income: float, credit_score: int, loan_amount: float) -> str:
        """Runs inference on the Loan Approval model."""
        if not self.is_model_active("loan"):
            raise ModelUnavailableException("Loan Approval model is temporarily unavailable.")
            
        model = self.models["loan"]
        # Convert inputs to DataFrame matching original training features
        X = pd.DataFrame([{
            "income": income,
            "credit_score": credit_score,
            "loan_amount": loan_amount
        }])
        
        prediction_val = int(model.predict(X)[0])
        return "Approved" if prediction_val == 1 else "Rejected"

    def predict_house(self, area: float, bedrooms: int, bathrooms: float) -> float:
        """Runs inference on the House Price model."""
        if not self.is_model_active("house"):
            raise ModelUnavailableException("House Price model is temporarily unavailable.")
            
        model = self.models["house"]
        X = pd.DataFrame([{
            "area": area,
            "bedrooms": bedrooms,
            "bathrooms": bathrooms
        }])
        
        return float(model.predict(X)[0])

    def predict_churn(self, tenure: int, monthly_charges: float, contract_type: int) -> str:
        """Runs inference on the Customer Churn model."""
        if not self.is_model_active("churn"):
            raise ModelUnavailableException("Customer Churn model is temporarily unavailable.")
            
        model = self.models["churn"]
        X = pd.DataFrame([{
            "tenure": tenure,
            "monthly_charges": monthly_charges,
            "contract_type": contract_type
        }])
        
        prediction_val = int(model.predict(X)[0])
        return "Churn" if prediction_val == 1 else "No Churn"
