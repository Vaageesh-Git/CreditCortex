import os
import shutil
import pandas as pd
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import json

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

# Add this block to allow React to talk to FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TEMP allow all
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the AI Engines globally so they stay in memory between requests
print("Waking up AI Agents...")
gateway = CognitiveGateway()
ml_engine = MLRiskEngine()
rag_engine = RAGComplianceEngine()
orchestrator = CreditOrchestrator()
hitl_router = HITLRouter()

# Ensure directories exist
os.makedirs("data/raw_uploads", exist_ok=True)
os.makedirs("data/clean_tabular", exist_ok=True)
os.makedirs("data/clean_text", exist_ok=True)

@app.post("/evaluate-loan")
async def evaluate_loan(file: UploadFile = File(...)):
    """
    Accepts a borrower's business profile PDF, processes it through the 
    Dual-Track AI Pipeline, and returns the Credit Memo and Routing Decision.
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    # Define temporary paths for this specific request
    pdf_path = f"data/raw_uploads/{file.filename}"
    csv_path = f"data/clean_tabular/{file.filename.replace('.pdf', '.csv')}"
    text_path = f"data/clean_text/{file.filename.replace('.pdf', '.txt')}"

    try:
        # Save the uploaded file to disk
        with open(pdf_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # PHASE 1: Data Gateway
        _, unstructured_text_list = gateway.process_document(
            file_path=pdf_path, 
            tabular_output_path=csv_path, 
            text_output_path=text_path
        )
        borrower_profile_text = " ".join(unstructured_text_list)

        # PHASE 2A: Mathematical Risk (XGBoost)
        if not os.path.exists(csv_path):
            # Fault-Tolerant Early Exit
            return JSONResponse(status_code=200, content={
                "status": "PAUSED",
                "assigned_queue": "DOCUMENT_COLLECTION_TEAM",
                "reason": "Missing structured financial tables in uploaded PDF.",
                "credit_memo": "ERROR: Credit Memo generation aborted due to missing financial data."
            })
        
        applicant_data = pd.read_csv(csv_path).iloc[[0]]
        risk_score, shap_signals, raw_shap_dict = ml_engine.evaluate_borrower(applicant_data)

        # PHASE 2B: Regulatory Compliance (RAG)
        retrieved_rules = rag_engine.evaluate_compliance(borrower_profile_text)

        # PHASE 3: The Orchestrator
        final_memo = orchestrator.generate_credit_memo(
            borrower_profile=borrower_profile_text,
            risk_score=risk_score,
            shap_signals=shap_signals,
            retrieved_rules=retrieved_rules
        )

        # PHASE 4: HITL Routing
        routing_decision = hitl_router.determine_routing_action(risk_score, final_memo)
        if not applicant_data.empty:
            raw_data_dict = json.loads(applicant_data.to_json(orient="records"))[0]
        else:
            raw_data_dict = {}
        
        # Return the JSON Response
        return {
            "routing": routing_decision,
            "credit_memo": final_memo,
            "metrics": {
                "risk_score_predicted": round(risk_score * 100, 2),
                "shap_signals": raw_shap_dict
            },
            "borrower_data": raw_data_dict
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline Execution Failed: {str(e)}")

    finally:
        # Cleanup: Remove the uploaded PDF from the server after processing
        if os.path.exists(pdf_path):
            os.remove(pdf_path)