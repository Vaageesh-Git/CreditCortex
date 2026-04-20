import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Load your GROQ_API_KEY from your .env file
load_dotenv()

class CreditOrchestrator:
    def __init__(self):
        print("Initializing the AI Chief Credit Officer (Powered by Gemini)...")
        
        # We use LLaMA 3 70B for deep reasoning and strict formatting compliance.
        # Temperature is kept at 0 to prevent creative hallucinations in banking decisions.
        self.llm = ChatGroq(
            temperature=0,
            model_name="llama-3.3-70b-versatile", 
            max_tokens=1500
        )

    def build_system_prompt(self):
        """The master prompt that dictates the AI's behavior and formatting rules."""
        system_template = """You are an expert Chief Credit Officer for a regulated banking institution.

    Your task is to generate a professional CREDIT APPRAISAL MEMO.

    ----------------------------------------
    STRICT RULES:
    ----------------------------------------

    1. The FINAL DECISION is already made: {decision}
    2. You MUST NOT contradict this decision.
    3. Do NOT use vague language like "may indicate" or "monitor".
    4. Be clear, decisive, and business-focused.

    ----------------------------------------
    STRUCTURE:
    ----------------------------------------

    - Executive Summary
    - Quantitative Risk Analysis
    - Regulatory & Policy Compliance
    - Final Recommendation

    ----------------------------------------

    BORROWER PROFILE:
    {borrower_profile}

    QUANTITATIVE RISK:
    Predicted Default Risk: {risk_score}%
    SHAP Signals:
    {shap_signals}

    REGULATORY CONTEXT:
    {retrieved_rules}

    ----------------------------------------

    IMPORTANT:
    - Final Recommendation MUST clearly state: {decision}
    - Justify the decision using risk + policy
    - DO NOT modify or recompute any numeric values.
    - Use only provided numbers exactly.
    """

        
        return ChatPromptTemplate.from_messages([
            ("system", system_template),
            ("user", "Please generate the Credit Appraisal Memo based on the provided inputs.")
        ])

    def build_decision_prompt(self):
        system_template ="""
        You are an expert Chief Credit Officer for a regulated banking institution.

        Your task is to analyze a loan application using:
        1. Mathematical Risk Signals (ML output)
        2. Regulatory Rules (provided context)

        ----------------------------------------
        OUTPUT FORMAT (STRICT)
        ----------------------------------------

        You MUST return ONLY a valid JSON object.

        DO NOT include:
        - markdown
        - explanations
        - headings
        - text before or after JSON

        ONLY return JSON.

        ----------------------------------------

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

        DECISION RULES:

        1. If risk_score > 50% OR severe signals (DPD ≥ 60, CIBIL < 650, high FOIR > 60%)
        → final_decision = "REJECT"
        → confidence_level = "HIGH"

        2. If risk_score < 5% AND strong profile (CIBIL > 700, low FOIR < 40%, no delinquencies)
        → final_decision = "APPROVE"
        → confidence_level = "HIGH"

        3. Otherwise:
        → final_decision = "REVIEW"
        → confidence_level = "MEDIUM"

        4. policy_violation = true ONLY if explicit regulatory rule is violated
        5. requires_manual_review = true ONLY if decision = REVIEW

        ----------------------------------------

        INPUT DATA:

        BORROWER PROFILE:
        {borrower_profile}

        QUANTITATIVE RISK:
        Predicted Default Risk: {risk_score}%
        SHAP Signals:
        {shap_signals}

        REGULATORY CONTEXT:
        {retrieved_rules}
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

        # parse JSON safely
        import json
        try:
            return json.loads(response)
        except:
            return {"final_decision": "REVIEW"}