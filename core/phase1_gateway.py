import os
import pandas as pd
from typing import Optional
from unstructured.partition.pdf import partition_pdf
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

# =================================================================
# 1. THE ML SCHEMA (Pydantic)
# Define the EXACT columns your XGBoost model expects.
# The descriptions teach the LLM how to map messy text to clean math.
# =================================================================
class ApplicantFinancials(BaseModel):
    # --- 1. CORE REQUIREMENTS ---
    loan_amnt: Optional[float] = Field(default=None, description="Total loan amount requested. CRITICAL: Remove currency symbols and commas. Convert Lakhs/Crores to numbers (e.g., 50 Lakhs = 5000000).")
    annual_inc: Optional[float] = Field(default=None, description="Annual income, revenue, or turnover. Convert Lakhs/Crores to raw numbers.")
    cibil_score: Optional[float] = Field(default=None, description="The applicant's CIBIL score, Experian score, or Equifax score. (Replaces FICO).")
    
    # --- 2. BANK STATEMENT ANALYSIS (BSA) METRICS ---
    cheque_bounce_count_6m: Optional[float] = Field(default=0.0, description="The number of cheque bounces, inward returns, or NACH/ECS mandates failed in the last 6 months. This is a massive risk flag.")
    avg_monthly_balance: Optional[float] = Field(default=None, description="The Average Monthly Balance (AMB) maintained in the bank account. CRITICAL: Remove commas and currency symbols.")
    foir: Optional[float] = Field(default=None, description="Fixed Obligation to Income Ratio (FOIR). The percentage of monthly income going toward existing EMIs. Remove the % sign.")
    
    # --- 3. MSME SPECIFIC METRICS ---
    gst_to_bank_variance_pct: Optional[float] = Field(default=0.0, description="The variance percentage between reported GST turnover and actual bank credits. If they state GST matches bank statements exactly, return 0.")
    business_vintage_years: Optional[float] = Field(default=None, description="How many years the business has been in operation. Return a raw number (e.g., '3.5' for three and a half years).")
    
    # --- 4. BUREAU RISK FLAGS ---
    max_dpd_12m: Optional[float] = Field(default=0.0, description="Maximum Days Past Due (DPD) on any existing loan in the last 12 months. E.g., if they were 30 days late, return 30.")
    recent_enquiries_6m: Optional[float] = Field(default=0.0, description="Number of CIBIL/bureau hard enquiries made by the applicant in the last 6 months for other loans.")

class CognitiveGateway:
    def __init__(self):
        print("Initializing LLM-Driven Semantic Extraction Gateway...")
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()
        
        # We use a fast LLM for extraction (Llama 3 8B is perfect for this)
        self.llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0)
        # Force the LLM to output ONLY our strict Pydantic schema
        self.structured_llm = self.llm.with_structured_output(ApplicantFinancials)

    def mask_pii(self, text: str) -> str:
        """Scans text for PII (Names, Emails, Phone Numbers) and masks it locally."""
        results = self.analyzer.analyze(
            text=text, 
            entities=["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", "CREDIT_CARD"], 
            language='en'
        )
        anonymized_result = self.anonymizer.anonymize(text=text, analyzer_results=results)
        return anonymized_result.text

    def process_document(self, file_path: str, tabular_output_path: str, text_output_path: str):
        """Extracts text, translates it into strict ML features via LLM, and enforces the Pre-Flight Gate."""
        print(f"\nProcessing Document: {file_path}")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Raw PDF not found at {file_path}")

        # 1. Extract ALL text universally (ignoring table formatting)
        elements = partition_pdf(filename=file_path, strategy="hi_res")
        raw_text = " ".join([str(element) for element in elements])
        clean_text = self.mask_pii(raw_text)

        # 2. Save Masked Text for RAG (Track B)
        os.makedirs(os.path.dirname(text_output_path), exist_ok=True)
        with open(text_output_path, "w", encoding="utf-8") as f:
            f.write(clean_text)

        # 3. LLM Extraction (Track A)
        print("-> Running Semantic Extraction...")
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert data extraction AI for a bank. 
            Extract the financial metrics from the provided text. 
            RULES:
            1. Output RAW NUMBERS ONLY.
            2. Strip all currency symbols ($, ₹), commas, and percentage signs (%).
            3. If a required value is entirely missing, return null."""),
            ("user", "Extract data from this profile:\n\n{text}")
        ])
        
        extraction_chain = prompt | self.structured_llm
        extracted_data = extraction_chain.invoke({"text": clean_text})
        extracted_dict = extracted_data.model_dump()
        print(f"-> Extracted Data: {extracted_dict}")

        # 4. THE PRE-FLIGHT GATE
        CRITICAL_FIELDS = ["loan_amnt", "annual_inc"]
        missing_fields = [field for field in CRITICAL_FIELDS if extracted_dict.get(field) is None]

        if missing_fields:
            print(f"-> GATEWAY HALT: Missing critical fields {missing_fields}")
            return {"status": "HALTED", "missing": missing_fields}, clean_text

        # 5. Save the perfectly formatted 1-row CSV for XGBoost
        os.makedirs(os.path.dirname(tabular_output_path), exist_ok=True)
        df = pd.DataFrame([extracted_dict])
        df.to_csv(tabular_output_path, index=False)
        print(f"-> Semantic mapping successful. Saved aligned features to {tabular_output_path}")

        return {"status": "SUCCESS", "missing": []}, clean_text