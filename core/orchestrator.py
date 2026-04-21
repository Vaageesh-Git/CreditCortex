import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

class CreditOrchestrator:
    def __init__(self):
        print("Initializing the AI Chief Credit Officer (Powered by Gemini)...")
        self.llm = ChatGroq(
            temperature=0,
            model_name="llama-3.3-70b-versatile", 
            max_tokens=1500
        )

    def build_system_prompt(self):
        system_template = """You are an expert Chief Credit Officer. Generate a professional CREDIT APPRAISAL MEMO.

    ----------------------------------------
    STRICT RULES:
    1. The FINAL DECISION is: {decision}
    2. If decision is APPROVE, use a confident tone. Highlight the borrower's strengths.
    3. If decision is REVIEW, specify exactly what a human needs to verify.
    4. You MUST NOT contradict the provided decision: {decision}.
    ----------------------------------------

    STRUCTURE:
    - Executive Summary: State the decision immediately.
    - Quantitative Risk Analysis: Explain the {risk_score}% risk and SHAP factors.
    - Regulatory & Policy Compliance: Mention specific RBI 2025/2026 directions.
    - Final Recommendation: Must end with a standalone line: {decision}

    BORROWER PROFILE: {borrower_profile}
    QUANTITATIVE RISK: Predicted Default Risk: {risk_score}%
    SHAP Signals: {shap_signals}
    REGULATORY CONTEXT: {retrieved_rules}

    IMPORTANT: Do not modify numeric values. Use exact figures provided.
    """
        return ChatPromptTemplate.from_messages([
            ("system", system_template),
            ("user", "Generate the Credit Appraisal Memo.")
        ])

    def build_decision_prompt(self):
        system_template = """
        You are an expert Chief Credit Officer for a regulated banking institution.

        Your task is to analyze a loan application using:
        1. Mathematical Risk Signals (ML output)
        2. Regulatory Rules (provided context)

        ----------------------------------------
        OUTPUT FORMAT (STRICT)
        ----------------------------------------
        You MUST return ONLY a valid JSON object.
        DO NOT include markdown, explanations, or headings.

        JSON STRUCTURE:
        {{
        "final_decision": "APPROVE | REJECT | REVIEW",
        "policy_violation": true/false,
        "requires_manual_review": true/false,
        "confidence_level": "HIGH | MEDIUM | LOW",
        "key_risk_factors": [],
        "key_positive_factors": []
        }}

        ----------------------------------------
        DECISION RULES (PRIORITY ORDER):

        1. REJECT if: 
           - risk_score > 50% OR 
           - CIBIL < 650 OR 
           - Explicit Policy Violation found in Regulatory Context.

        2. APPROVE if:
           - risk_score < 5% AND 
           - CIBIL >= 750 AND 
           - FOIR <= 45% (Indicates high repayment capacity).

        3. REVIEW if:
           - 5% <= risk_score <= 50% OR
           - CIBIL is between 650-749 OR
           - Missing critical income verification data.

        4. policy_violation = true ONLY if explicit regulatory rule is violated.
        5. requires_manual_review = true ONLY if decision = REVIEW.
        ----------------------------------------

        INPUT DATA:
        BORROWER PROFILE: {borrower_profile}
        QUANTITATIVE RISK: Predicted Default Risk: {risk_score}%
        SHAP Signals: {shap_signals}
        REGULATORY CONTEXT: {retrieved_rules}
        """
        return ChatPromptTemplate.from_messages([
            ("system", system_template),
            ("user", "Return JSON decision.")
        ])

    def generate_credit_memo(self, borrower_profile, risk_score, shap_signals, retrieved_rules, decision):
        """The final convergence function. Synthesizes inputs into the final decision."""
        print("\n--- SYNTHESIZING DUAL-TRACK DATA ---")
        
        prompt = self.build_system_prompt()
        chain = prompt | self.llm | StrOutputParser()
        
        formatted_risk = round(risk_score * 100, 2)
        
        print("Drafting final Credit Appraisal Memo at Gemini speed...\n")
        response = chain.invoke({
            "borrower_profile": borrower_profile,
            "risk_score": formatted_risk,
            "shap_signals": shap_signals,
            "retrieved_rules": retrieved_rules,
            "decision": decision 
        })
        
        return response

    def get_decision_json(self, borrower_profile, risk_score, shap_signals, retrieved_rules):
        prompt = self.build_decision_prompt()
        chain = prompt | self.llm | StrOutputParser()

        formatted_risk = round(risk_score * 100, 2)

        response = chain.invoke({
            "borrower_profile": borrower_profile,
            "risk_score": formatted_risk,
            "shap_signals": shap_signals,
            "retrieved_rules": retrieved_rules
        })

        import json
        try:
            return json.loads(response)
        except:
            return {"final_decision": "REVIEW"}