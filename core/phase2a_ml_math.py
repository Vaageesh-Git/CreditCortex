import pandas as pd
import numpy as np
import xgboost as xgb
import shap
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

class MLRiskEngine:
    def __init__(self, artifact_dir="../core/artifacts/"):
        # We define a directory to save our trained model files
        self.artifact_dir = artifact_dir
        os.makedirs(self.artifact_dir, exist_ok=True)
        
        self.model_path = os.path.join(self.artifact_dir, "xgboost_risk_model.json")
        self.features_path = os.path.join(self.artifact_dir, "feature_names.joblib")
        
        self.model = xgb.XGBClassifier(
            objective='binary:logistic',
            eval_metric='logloss',
            max_depth=5, 
            learning_rate=0.1,
            n_estimators=100
        )
        self.explainer = None
        self.feature_names = None

    def train_and_save_model(self, file_path: str, target_column: str = 'is_npa'):
        """Runs strictly on a schedule (e.g., monthly). Trains and saves the artifacts."""
        print(f"--- INITIATING OFFLINE TRAINING PIPELINE ---")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Dataset not found at {file_path}.")

        df = pd.read_csv(file_path)
        X = df.drop(columns=[target_column])
        y = df[target_column]
        self.feature_names = X.columns.tolist()

        print(f"Training on {len(X)} records...")
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        self.model.fit(X_train, y_train)
        
        # Save the Model and Feature Names securely to disk
        self.model.save_model(self.model_path)
        joblib.dump(self.feature_names, self.features_path)
        print(f"SUCCESS: Model saved to {self.model_path}")
        print(f"SUCCESS: Features saved to {self.features_path}\n")

    def load_production_model(self):
        """Loads the saved artifacts into memory for real-time inference."""
        if not os.path.exists(self.model_path) or not os.path.exists(self.features_path):
            raise RuntimeError("Saved model artifacts not found. Run training pipeline first.")

        # Load the pre-trained weights
        self.model.load_model(self.model_path)
        self.feature_names = joblib.load(self.features_path)
        
        # Re-initialize the SHAP explainer instantly from the loaded tree
        self.explainer = shap.TreeExplainer(self.model)
        # print("Production model loaded into memory.")

    def evaluate_borrower(self, borrower_features: pd.DataFrame):
        """The production function. Runs instantly using the loaded model."""
        if self.explainer is None:
             self.load_production_model()

        # Ensure the incoming data matches the exact columns the model was trained on
        borrower_features = borrower_features[self.feature_names]

        # 1. Get Mathematical Prediction (Lightning Fast)
        risk_probability = float(self.model.predict_proba(borrower_features)[0][1])
        
        # 2. Get Explainability Signals (SHAP)
        shap_values = self.explainer.shap_values(borrower_features)
        
        # 3. Format Signals for the LLM
        signals = []
        for i, col in enumerate(self.feature_names):
            impact = shap_values[0][i]
            val = borrower_features.iloc[0, i]
            
            if impact > 0.5: 
                signals.append(f"CRITICAL RISK (+): {col} is at {val}, heavily increasing default probability.")
            elif impact > 0.1:
                signals.append(f"MODERATE RISK (+): {col} is at {val}, slightly increasing default probability.")
            elif impact < -0.5: 
                signals.append(f"STRONG POSITIVE (-): {col} is at {val}, heavily decreasing default probability.")

        explanation_text = "\n".join(signals) if signals else "No overwhelming singular factors detected."
        
        return risk_probability, explanation_text

# --- Execution Simulation ---
if __name__ == "__main__":
    engine = MLRiskEngine()
    DATASET_PATH = "../data/clean_tabular/training_dataset.csv" 
    
    # Toggle this flag to simulate your deployment environment
    IS_TRAINING_DAY = False 
    
    if IS_TRAINING_DAY:
        # A CRON job or MLOps pipeline runs this once a month
        engine.train_and_save_model(DATASET_PATH)
    else:
        # The Live API runs this every time a loan officer hits "Submit"
        print("--- REAL-TIME API INFERENCE ---")
        
        # Mocking an incoming request from the Document Gateway
        mock_data = pd.DataFrame({
            'avg_monthly_balance': [150000],
            'cheque_bounce_count_6m': [6],
            'gst_to_bank_variance_pct': [22.5],
            'credit_to_debit_ratio': [0.8],
            'industry_risk_tier': [3]
        })
        
        try:
            # The model loads from disk (if not already in memory) and predicts instantly
            risk_score, explanation = engine.evaluate_borrower(mock_data)
            
            print(f"Predicted NPA Risk: {risk_score * 100:.2f}%")
            print("AI Feedback Signals:")
            print(explanation)
        except RuntimeError as e:
             print(f"API Error: {e}")