import pandas as pd
import numpy as np
import xgboost as xgb
import shap
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.metrics import roc_auc_score
import numpy as np
from xgboost import callback

class MLRiskEngine:
    def __init__(self, artifact_dir="core/artifacts/"):
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

    def train_and_save_model(self, file_path: str, target_column: str = 'target'):
        print(f"--- INITIATING ADVANCED TRAINING PIPELINE ---")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Dataset not found at {file_path}.")

        df = pd.read_csv(file_path)
        df["credit_to_debit_ratio"] = df["annual_inc"] / (df["loan_amnt"] + 1)
        df["high_dti_flag"] = (df["foir"] > 0.5).astype(int)
        df["credit_score_avg"] = df["cibil_score"]

        X = df.drop(columns=[target_column])
        y = df[target_column]

        X = pd.get_dummies(X, drop_first=True)

        self.feature_names = X.columns.tolist()

        X_train, X_temp, y_train, y_temp = train_test_split(
            X, y, test_size=0.3, stratify=y, random_state=42
        )

        X_val, X_test, y_val, y_test = train_test_split(
            X_temp, y_temp, test_size=0.5, stratify=y_temp, random_state=42
        )

        scale_pos_weight = (len(y_train) - sum(y_train)) / sum(y_train)

        self.model = xgb.XGBClassifier(
            objective='binary:logistic',
            eval_metric='auc',
            max_depth=5,
            learning_rate=0.05,
            n_estimators=500,
            subsample=0.8,
            colsample_bytree=0.8,
            reg_alpha=0.1,
            reg_lambda=1,
            scale_pos_weight=scale_pos_weight,
            random_state=42
        )

        skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

        cv_scores = []

        print("Running Cross Validation...")

        for train_idx, val_idx in skf.split(X_train, y_train):
            X_tr, X_va = X_train.iloc[train_idx], X_train.iloc[val_idx]
            y_tr, y_va = y_train.iloc[train_idx], y_train.iloc[val_idx]

            self.model.fit(
                X_tr, y_tr,
                eval_set=[(X_va, y_va)],
                callbacks=[
                    callback.EarlyStopping(
                        rounds=10,
                        save_best=True
                    )
                ],
                verbose=False
            )

            preds = self.model.predict_proba(X_va)[:, 1]
            auc = roc_auc_score(y_va, preds)
            cv_scores.append(auc)

        print(f"CV AUC Scores: {cv_scores}")
        print(f"Mean CV AUC: {np.mean(cv_scores):.4f}")

        print("Training Final Model with Early Stopping...")

        self.model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            early_stopping_rounds=50,
            verbose=True
        )

        test_preds = self.model.predict_proba(X_test)[:, 1]
        test_auc = roc_auc_score(y_test, test_preds)

        print(f"Final Test AUC: {test_auc:.4f}")

        self.model.save_model(self.model_path)
        joblib.dump(self.feature_names, self.features_path)

        print(f"SUCCESS: Model saved to {self.model_path}")

    def load_production_model(self):
        """Loads the saved artifacts into memory for real-time inference."""
        if not os.path.exists(self.model_path) or not os.path.exists(self.features_path):
            raise RuntimeError("Saved model artifacts not found. Run training pipeline first.")

        # Load the pre-trained weights
        self.model.load_model(self.model_path)
        self.feature_names = joblib.load(self.features_path)
        
        # Re-initialize the SHAP explainer instantly from the loaded tree
        self.explainer = shap.TreeExplainer(self.model)

    def evaluate_borrower(self, borrower_features: pd.DataFrame):
        """The production function. Runs instantly using the loaded model."""
        if self.explainer is None:
             self.load_production_model()

        if "cibil_score" in borrower_features.columns:
            borrower_features["credit_score_avg"] = borrower_features["cibil_score"]

        if "annual_inc" in borrower_features.columns and "loan_amnt" in borrower_features.columns:
            borrower_features["credit_to_debit_ratio"] = borrower_features["annual_inc"] / (borrower_features["loan_amnt"] + 1)

        if "foir" in borrower_features.columns:
            borrower_features["high_dti_flag"] = (borrower_features["foir"] > 0.5).astype(int)
        
        aligned_features = pd.DataFrame(index=borrower_features.index, columns=self.feature_names)

        for col in self.feature_names:
            if col in borrower_features.columns:
                aligned_features[col] = borrower_features[col].values
            else:
                aligned_features[col] = 0

        borrower_features = aligned_features[self.feature_names]

        # 1. Get Mathematical Prediction
        risk_probability = float(self.model.predict_proba(borrower_features)[0][1])
        
        # 2. Get Explainability Signals (SHAP)
        shap_values = self.explainer.shap_values(borrower_features)
        
        # 3. Format Signals for the LLM
        signals = []
        raw_shap_dict = {}
        for i, col in enumerate(self.feature_names):
            # Force the numpy.float32 into a native Python float
            impact = float(shap_values[0][i]) 
            val = borrower_features.iloc[0, i]
            
            # Populate the dictionary for React
            raw_shap_dict[col] = impact 
            
            if impact > 0.5: 
                signals.append(f"CRITICAL RISK (+): {col} is at {val}, heavily increasing default probability.")
            elif impact > 0.1:
                signals.append(f"MODERATE RISK (+): {col} is at {val}, slightly increasing default probability.")
            elif impact < -0.5: 
                signals.append(f"STRONG POSITIVE (-): {col} is at {val}, heavily decreasing default probability.")

        explanation_text = "\n".join(signals) if signals else "No overwhelming singular factors detected."
        
        return risk_probability, explanation_text, raw_shap_dict

# --- Execution Simulation ---
if __name__ == "__main__":
    engine = MLRiskEngine()
    
    # Paths for your data
    TRAINING_DATASET_PATH = "system_data/training_data/cleaned_training_dataset.csv" 
    # This is the file that Phase 1 (Gateway) will output after processing a new loan application
    NEW_APPLICATION_PATH = "customer_data/clean_tabular/new_application.csv"
    
    # Toggle this flag to simulate your deployment environment
    IS_TRAINING_DAY = False 
    
    if IS_TRAINING_DAY:
        engine.train_and_save_model(TRAINING_DATASET_PATH)
    else:
        print("--- REAL-TIME API INFERENCE ---")
        
        try:
            # 1. Load the actual parsed borrower data generated by the Gateway
            if not os.path.exists(NEW_APPLICATION_PATH):
                 raise FileNotFoundError(f"Waiting for Phase 1 output. Please ensure applicant data is saved at: {NEW_APPLICATION_PATH}")
            
            print(f"Ingesting actual applicant features from {NEW_APPLICATION_PATH}...")
            incoming_data = pd.read_csv(NEW_APPLICATION_PATH)
            
            applicant_data = incoming_data.iloc[[0]] 
            
            risk_score, explanation = engine.evaluate_borrower(applicant_data)
            
            print(f"\nPredicted NPA Risk: {risk_score * 100:.2f}%")
            print("AI Feedback Signals:")
            print(explanation)
            
        except RuntimeError as e:
             print(f"Model Error: {e}")
        except Exception as e:
             print(f"System Error: {e}")