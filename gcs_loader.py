import os
import json
from google.cloud import storage
from google.oauth2 import service_account

BUCKET_NAME = os.getenv("GCS_BUCKET")


def get_client():
    creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")

    if not creds_json:
        raise ValueError("GOOGLE_CREDENTIALS_JSON not set")

    creds_dict = json.loads(creds_json)
    credentials = service_account.Credentials.from_service_account_info(creds_dict)

    return storage.Client(credentials=credentials)


def download_all_assets():
    client = get_client() 
    bucket = client.bucket(BUCKET_NAME)

    os.makedirs("models", exist_ok=True)
    os.makedirs("vector_db", exist_ok=True)

    download_file(bucket, "xgboost_risk_model.json", "models/xgboost_risk_model.json")
    download_file(bucket, "feature_names.joblib", "models/feature_names.joblib")
    download_file(bucket, "index.faiss", "vector_db/index.faiss")
    download_file(bucket, "index.pkl", "vector_db/index.pkl")