import os
import shutil
import pandas as pd
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import json
import re

# Import the core AI modules
from core.phase1_gateway import CognitiveGateway
from core.phase2a_ml_math import MLRiskEngine
from core.phase2b_rag_logic import RAGComplianceEngine
from core.orchestrator import CreditOrchestrator
from core.phase4_hitl_router import HITLRouter
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

# Initialize the API
app = FastAPI(
    title="CreditCortex",
    description="Explainable AI core for evaluating MSME loan applications.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Waking up AI Agents...")
gateway = CognitiveGateway()
ml_engine = MLRiskEngine()
rag_engine = RAGComplianceEngine()
orchestrator = CreditOrchestrator()
hitl_router = HITLRouter()

os.makedirs("customer_data/raw_uploads", exist_ok=True)
os.makedirs("customer_data/clean_tabular", exist_ok=True)
os.makedirs("customer_data/clean_text", exist_ok=True)


def extract_json(text):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except:
            return None
    return None

@app.post("/evaluate-loan")
async def evaluate_loan(file: UploadFile = File(...)):
    """
    Accepts a borrower's business profile PDF, processes it through the 
    Dual-Track AI Pipeline, and returns the Credit Memo and Routing Decision.
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    # Define temporary paths for this specific request
    pdf_path = f"customer_data/raw_uploads/{file.filename}"
    csv_path = f"customer_data/clean_tabular/{file.filename.replace('.pdf', '.csv')}"
    text_path = f"customer_data/clean_text/{file.filename.replace('.pdf', '.txt')}"

    try:
        # Save the uploaded file to disk
        with open(pdf_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # The new gateway returns the exact status and a single string of text
        gateway_status, borrower_profile_text = gateway.process_document(
            file_path=pdf_path, 
            tabular_output_path=csv_path, 
            text_output_path=text_path
        )

        # The new Pre-Flight Gate relies on the LLM's structured output
        if gateway_status["status"] == "HALTED":
            missing = gateway_status["missing"]
            return {
                "routing": {
                    "status": "PAUSED",
                    "assigned_queue": "DOCUMENT_COLLECTION_TEAM",
                    "reason": f"Gateway halted. Missing semantic data: {', '.join(missing)}"
                },
                "credit_memo": f"### ⚠️ Document Ingestion Alert\n\nThe AI was unable to locate critical requirements (`{', '.join(missing)}`) in the uploaded document. \n\n**Action Required:** Please contact the borrower to submit a complete application.",
                "metrics": {"risk_score_predicted": 0, "shap_signals": {}},
                "borrower_data": {}
            }

        # If it passed the gateway, we guarantee the CSV is perfect
        applicant_data = pd.read_csv(csv_path)
        applicant_data_row = applicant_data.iloc[[0]]
        if "foir" in applicant_data_row.columns and applicant_data_row["foir"].max() > 1:
            applicant_data_row["foir"] = applicant_data_row["foir"] / 100

        applicant_data_row.fillna(0, inplace=True)
        
        risk_score, shap_text, raw_shap_dict = ml_engine.evaluate_borrower(applicant_data_row)
        retrieved_rules = rag_engine.evaluate_compliance(borrower_profile_text)

        decision_json = orchestrator.get_decision_json(
            borrower_profile=borrower_profile_text,
            risk_score=risk_score,
            shap_signals=shap_text,
            retrieved_rules=retrieved_rules
        )

        extracted_data = applicant_data_row.to_dict(orient="records")[0]
        extracted_data["credit_score_avg"] = extracted_data.get("cibil_score", 0)

        routing = hitl_router.determine_routing_action(
            risk_score=risk_score,
            rag_output=decision_json,
            features=extracted_data
        )

        final_memo = orchestrator.generate_credit_memo(
            borrower_profile=borrower_profile_text,
            risk_score=risk_score,
            shap_signals=shap_text,
            retrieved_rules=retrieved_rules,
            decision=decision_json["final_decision"]   # 🔥 IMPORTANT
        )
        
        if not applicant_data.empty:
            raw_data_dict = json.loads(applicant_data.to_json(orient="records"))[0]
        else:
            raw_data_dict = {}
        

        conduct_metrics = {
            "cheque_bounces": extracted_data.get("cheque_bounce_count_6m", 0),
            "max_dpd": extracted_data.get("max_dpd_12m", 0),
            "recent_enquiries": extracted_data.get("recent_enquiries_6m", 0)
        }

        percentage_metrics = {
            "foir": extracted_data.get("foir", 0),
            "dti": extracted_data.get("foir", 0),  # fallback if same
            "credit_utilization": extracted_data.get("credit_utilization", 0)
        }
        return {
            "routing": routing,
            "decision": decision_json,
            "credit_memo": final_memo,
            "conduct_metrics": conduct_metrics,          # 🔥 ADD THIS
            "percentage_metrics": percentage_metrics     # 🔥 ADD THIS
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline Execution Failed: {str(e)}")

    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)