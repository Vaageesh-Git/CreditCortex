import xgboost as xgb
import joblib
import faiss
import pickle

# Global variables (so they can be reused)
model = None
feature_names = None
index = None
metadata = None

def load_all_assets():
    global model, feature_names, index, metadata

    print("Loading ML model...")
    model = xgb.Booster()
    model.load_model("models/xgboost_risk_model.json")

    print("Loading feature names...")
    feature_names = joblib.load("models/feature_names.joblib")

    print("Loading FAISS index...")
    index = faiss.read_index("vector_db/index.faiss")

    print("Loading metadata...")
    with open("vector_db/index.pkl", "rb") as f:
        metadata = pickle.load(f)

    print("All assets loaded successfully!")