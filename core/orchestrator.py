import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Load your GROQ_API_KEY from your .env file
load_dotenv()

class CreditOrchestrator:
    def __init__(self):
        print("Initializing the AI Chief Credit Officer (Powered by Groq)...")
        
        # We use LLaMA 3 70B for deep reasoning and strict formatting compliance.
        # Temperature is kept at 0 to prevent creative hallucinations in banking decisions.
        self.llm = ChatGroq(
            temperature=0,
            model_name="llama-3.3-70b-versatile", 
            max_tokens=1500
        )

    def build_system_prompt(self):
        """The master prompt that dictates the AI's behavior and formatting rules."""
        system_template = """
        You are an expert Chief Credit Officer for a regulated banking institution.
        Your task is to review a loan application using the mathematical risk signals and the regulatory rules provided to you.
        
        You must synthesize these inputs and generate a formal 'Explainable Credit Appraisal Memo'.
        
        RULES:
        1. NO HALLUCINATIONS: You must only cite rules that are explicitly provided in the 'Regulatory Context'.
        2. CONFLICT RESOLUTION: If the Mathematical Risk is high, but the Regulatory rules say they are eligible for a scheme, note the conflict explicitly in a 'Risk vs. Eligibility' section.
        3. EXPLAINABILITY: Translate the 'SHAP Risk Signals' into clear, non-technical business language.
        4. STRUCTURE: Use markdown formatting. Include sections for: Executive Summary, Quantitative Risk Analysis, Regulatory & Policy Compliance, and Final Recommendation.
        
        BORROWER PROFILE (Masked):
        {borrower_profile}
        
        QUANTITATIVE RISK (Track A Output):
        Predicted Default Risk: {risk_score}%
        Risk Signals (SHAP):
        {shap_signals}
        
        REGULATORY CONTEXT (Track B Output):
        {retrieved_rules}
        """
        
        return ChatPromptTemplate.from_messages([
            ("system", system_template),
            ("user", "Please generate the Credit Appraisal Memo based on the provided inputs.")
        ])

    def generate_credit_memo(self, borrower_profile: str, risk_score: float, shap_signals: str, retrieved_rules: str):
        """The final convergence function. Synthesizes inputs into the final decision."""
        print("\n--- SYNTHESIZING DUAL-TRACK DATA ---")
        
        prompt = self.build_system_prompt()
        chain = prompt | self.llm | StrOutputParser()
        
        formatted_risk = round(risk_score * 100, 2)
        
        print("Drafting final Credit Appraisal Memo at Groq speed...\n")
        response = chain.invoke({
            "borrower_profile": borrower_profile,
            "risk_score": formatted_risk,
            "shap_signals": shap_signals,
            "retrieved_rules": retrieved_rules
        })
        
        return response