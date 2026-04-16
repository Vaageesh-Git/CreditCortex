import os
import pandas as pd
from dotenv import load_dotenv
from core.phase4_hitl_router import HITLRouter
from core.phase1_gateway import CognitiveGateway
from core.phase2a_ml_math import MLRiskEngine
from core.phase2b_rag_logic import RAGComplianceEngine
from core.orchestrator import CreditOrchestrator

load_dotenv()

def process_loan_application(pdf_file_path: str, new_tabular_data_path: str):
    """
    The end-to-end production pipeline. 
    No mock data. Everything is generated dynamically.
    """
    print("==================================================")
    print("INITIATING AI LENDING PIPELINE")
    print("==================================================\n")

    # Initialize all engines
    gateway = CognitiveGateway()
    ml_engine = MLRiskEngine()
    rag_engine = RAGComplianceEngine()
    orchestrator = CreditOrchestrator()
    hitl_router = HITLRouter()

    # ---------------------------------------------------------
    # PHASE 1: Data Gateway (Ingestion & Masking)
    # ---------------------------------------------------------
    print("--> [PHASE 1] Running Cognitive Gateway...")

    text_path = "data/clean_text/masked_profile.txt"
    _, unstructured_text_list = gateway.process_document(
        file_path=pdf_file_path, 
        tabular_output_path=new_tabular_data_path, 
        text_output_path=text_path
    )
    
    # Combine the masked text blocks into a single profile string
    borrower_profile_text = " ".join(unstructured_text_list)

    # ---------------------------------------------------------
    # PHASE 2A: Mathematical Risk (XGBoost + SHAP)
    # ---------------------------------------------------------
    print("--> [PHASE 2A] Running ML Risk Engine...")
    if not os.path.exists(new_tabular_data_path):
        print("    [!] WARNING: No financial tables found. Halting AI underwriting.")
        routing_decision = {
            "status": "PAUSED",
            "assigned_queue": "DOCUMENT_COLLECTION_TEAM",
            "reason": "Missing structured financial tables in uploaded PDF."
        }
        return "ERROR: Credit Memo generation aborted due to missing financial data.", routing_decision
    
    applicant_data = pd.read_csv(new_tabular_data_path).iloc[[0]]
    risk_score, shap_signals = ml_engine.evaluate_borrower(applicant_data)

    # ---------------------------------------------------------
    # PHASE 2B: Regulatory Compliance (FAISS RAG)
    # ---------------------------------------------------------
    print("--> [PHASE 2B] Running RAG Compliance Engine...")
    retrieved_rules = rag_engine.evaluate_compliance(borrower_profile_text)

    # ---------------------------------------------------------
    # PHASE 3: The Gemini Orchestrator
    # ---------------------------------------------------------
    print("--> [PHASE 3] Generating Explainable Credit Memo...")
    final_memo = orchestrator.generate_credit_memo(
        borrower_profile=borrower_profile_text,
        risk_score=risk_score,
        shap_signals=shap_signals,
        retrieved_rules=retrieved_rules
    )

    # ---------------------------------------------------------
    # PHASE 4: Human-in-the-Loop Routing
    # ---------------------------------------------------------
    print("--> [PHASE 4] Executing HITL Governance Routing...")
    routing_decision = hitl_router.determine_routing_action(risk_score, final_memo)

    # ---------------------------------------------------------
    # FINAL OUTPUT DISPATCH
    # ---------------------------------------------------------
    print("\n================ FINAL SYSTEM OUTPUT ================")
    print(final_memo)
    print("\n================ ROUTING DECISION ===================")
    print(f"STATUS: {routing_decision['status']}")
    print(f"QUEUE:  {routing_decision['assigned_queue']}")
    print(f"REASON: {routing_decision['reason']}")
    print("=====================================================")

    return final_memo, routing_decision


if __name__ == "__main__":

    APPLICANT_PDF = "data/raw_uploads/applicant_business_profile.pdf"
    APPLICANT_CSV = "data/clean_tabular/new_application.csv"
    
    try:
        process_loan_application(APPLICANT_PDF, APPLICANT_CSV)
    except Exception as e:
        print(f"\nPipeline Execution Failed: {e}")