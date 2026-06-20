import os
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression, LinearRegression

# Ensure the output directory exists
MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
os.makedirs(MODELS_DIR, exist_ok=True)

def train_loan_model():
    print("Training Loan Approval Model...")
    # Generate synthetic data
    np.random.seed(42)
    n_samples = 1000
    
    # Features: income (annual in $), credit_score (300-850), loan_amount ($)
    income = np.random.normal(60000, 20000, n_samples).clip(15000, 200000)
    credit_score = np.random.normal(680, 80, n_samples).clip(300, 850)
    loan_amount = np.random.normal(150000, 70000, n_samples).clip(10000, 500000)
    
    # Decision logic + noise
    # Standard debt-to-income ratio check and credit score check
    log_odds = (credit_score - 620) / 50 + (income / loan_amount) * 3 - 2
    probability = 1 / (1 + np.exp(-log_odds))
    approved = (probability > 0.55).astype(int)
    
    X = pd.DataFrame({
        "income": income,
        "credit_score": credit_score,
        "loan_amount": loan_amount
    })
    y = approved
    
    model = LogisticRegression()
    model.fit(X, y)
    
    # Save the model
    model_path = os.path.join(MODELS_DIR, "loan_model.pkl")
    joblib.dump(model, model_path)
    print(f"Loan Approval Model saved to {model_path}")

def train_house_model():
    print("Training House Price Model...")
    # Generate synthetic data
    np.random.seed(42)
    n_samples = 1000
    
    # Features: area (sqft), bedrooms, bathrooms
    area = np.random.normal(1800, 600, n_samples).clip(500, 6000)
    bedrooms = np.random.choice([1, 2, 3, 4, 5], size=n_samples, p=[0.1, 0.3, 0.4, 0.15, 0.05])
    bathrooms = np.random.choice([1, 1.5, 2, 2.5, 3], size=n_samples)
    
    # Price function: 150 * area + 30000 * bedrooms + 20000 * bathrooms + noise
    price = 150 * area + 30000 * bedrooms + 20000 * bathrooms + np.random.normal(0, 15000, n_samples)
    price = price.clip(50000)
    
    X = pd.DataFrame({
        "area": area,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms
    })
    y = price
    
    model = LinearRegression()
    model.fit(X, y)
    
    # Save the model
    model_path = os.path.join(MODELS_DIR, "house_model.pkl")
    joblib.dump(model, model_path)
    print(f"House Price Model saved to {model_path}")

def train_churn_model():
    print("Training Customer Churn Model...")
    # Generate synthetic data
    np.random.seed(42)
    n_samples = 1000
    
    # Features: tenure (months), monthly_charges ($), contract_type (0=Month-to-month, 1=One year, 2=Two year)
    tenure = np.random.normal(24, 18, n_samples).clip(1, 72).astype(int)
    monthly_charges = np.random.normal(65, 30, n_samples).clip(15, 150)
    contract_type = np.random.choice([0, 1, 2], size=n_samples, p=[0.5, 0.25, 0.25])
    
    # Decision logic: churn probability is higher for short tenure, high charges, and month-to-month contracts
    log_odds = (monthly_charges / 50) - (tenure / 12) - contract_type * 1.5 + 0.5
    probability = 1 / (1 + np.exp(-log_odds))
    churn = (probability > 0.5).astype(int)
    
    X = pd.DataFrame({
        "tenure": tenure,
        "monthly_charges": monthly_charges,
        "contract_type": contract_type
    })
    y = churn
    
    model = LogisticRegression()
    model.fit(X, y)
    
    # Save the model
    model_path = os.path.join(MODELS_DIR, "churn_model.pkl")
    joblib.dump(model, model_path)
    print(f"Customer Churn Model saved to {model_path}")

if __name__ == "__main__":
    train_loan_model()
    train_house_model()
    train_churn_model()
    print("All models successfully trained and serialized!")
