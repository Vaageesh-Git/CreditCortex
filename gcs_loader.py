import os
from google.cloud import storage

BUCKET_NAME = os.getenv("GCS_BUCKET")

def download_file(bucket, blob_name, destination):
    if not os.path.exists(destination):
        print(f"Downloading {blob_name}...")
        blob = bucket.blob(blob_name)
        blob.download_to_filename(destination)

def download_all_assets():
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)

    os.makedirs("models", exist_ok=True)
    os.makedirs("vector_db", exist_ok=True)

    download_file(bucket, "xgboost_risk_model.json", "models/xgboost_risk_model.json")
    download_file(bucket, "feature_names.joblib", "models/feature_names.joblib")

    download_file(bucket, "index.faiss", "vector_db/index.faiss")
    download_file(bucket, "index.pkl", "vector_db/index.pkl")