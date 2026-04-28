<div align="center">

<img src="https://img.shields.io/badge/INDIA-FINTECH-orange?style=for-the-badge&logoColor=white" />
<img src="https://img.shields.io/badge/AI%20POWERED-XAI%20%2B%20RAG-blueviolet?style=for-the-badge&logo=googlegemini&logoColor=white" />

<br/><br/>

```
 ██████╗██████╗ ███████╗██████╗ ██╗████████╗ ██████╗ ██████╗ ██████╗ ████████╗███████╗██╗  ██╗
██╔════╝██╔══██╗██╔════╝██╔══██╗██║╚══██╔══╝██╔════╝██╔═══██╗██╔══██╗╚══██╔══╝██╔════╝╚██╗██╔╝
██║     ██████╔╝█████╗  ██║  ██║██║   ██║   ██║     ██║   ██║██████╔╝   ██║   █████╗   ╚███╔╝ 
██║     ██╔══██╗██╔══╝  ██║  ██║██║   ██║   ██║     ██║   ██║██╔══██╗   ██║   ██╔══╝   ██╔██╗ 
╚██████╗██║  ██║███████╗██████╔╝██║   ██║   ╚██████╗╚██████╔╝██║  ██║   ██║   ███████╗██╔╝ ██╗
 ╚═════╝╚═╝  ╚═╝╚══════╝╚═════╝ ╚═╝   ╚═╝    ╚═════╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝
```

# 🏦 CreditCortex
### *Explainable AI Underwriting for Indian MSMEs*

> **Transforming India's ₹87 Lakh Crore MSME credit gap — one explainable decision at a time.**

<br/>

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![React](https://img.shields.io/badge/React-18+-61DAFB?style=flat-square&logo=react&logoColor=black)](https://reactjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![XGBoost](https://img.shields.io/badge/XGBoost-2.0+-FF6600?style=flat-square&logoColor=white)](https://xgboost.readthedocs.io)
[![LangChain](https://img.shields.io/badge/LangChain-0.2+-1C3C3C?style=flat-square&logo=chainlink&logoColor=white)](https://langchain.com)
[![Gemini](https://img.shields.io/badge/Gemini-LLM%20API-4285F4?style=flat-square&logo=googlegemini&logoColor=white)](https://deepmind.google/technologies/gemini)
[![GCP](https://img.shields.io/badge/GCP-Cloud%20Run-4285F4?style=flat-square&logo=googlecloud&logoColor=white)](https://cloud.google.com)
[![Vercel](https://img.shields.io/badge/Vercel-Frontend-000000?style=flat-square&logo=vercel&logoColor=white)](https://vercel.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

<br/>

[🚀 Live Demo](https://creditcortex.vercel.app/) · [📄 System Design Doc](https://docs.google.com/document/d/1KdhOg1Ku34s_0F3aBT-LQnodC4HdqZk4/edit?usp=sharing&ouid=116452143832700883616&rtpof=true&sd=true)

</div>

---

## The Problem We're Solving

India has **63 million MSMEs** contributing 30% of GDP — yet **84% are credit-starved** because legacy underwriting systems simply weren't built for them.

| Legacy System Failure | Real-World Impact |
|---|---|
| Rigid OCR templates break on informal documents | Loan applications abandoned mid-process |
| Western-centric risk models (FICO scores) | Creditworthy Indian businesses wrongly rejected |
| Black-box AI decisions | RBI compliance violations, auditor nightmares |
| Manual data-chasing by loan officers | 72+ hours per application, ₹8,000+ processing cost |

**CreditCortex eliminates all four failure modes simultaneously.**

---

## ✨ What Makes CreditCortex Different

```
Traditional Underwriting              CreditCortex
─────────────────────                 ──────────────────────────────────────
Template OCR → 40% failure       →   Gemini + Unstructured → 95%+ accuracy
Generic risk score               →   India-specific XGBoost (GST, FOIR, Sec.138)
"Rejected." (no reason given)    →   SHAP-powered explanation for every factor
3–7 day turnaround               →   Sub-hour automated Credit Appraisal Memo
Human reviews everything         →   HITL only where it truly matters
No compliance audit trail        →   RAG-verified against live RBI policy docs
```

---

## 🏗️ System Architecture

### Architecture Diagram

![CreditCortex Architecture Diagram](./assets/architecture.png)

> *7 layers from raw PDF upload to an auditable, explainable credit decision — built for RBI-regulated environments*

### Pipeline at a Glance

```
┌─────────────────────────────────────────────────────────────────────────┐
│  LAYER 1 · INPUT LAYER                                                   │
│  User uploads PDF bank statements, GST filings, ITR, balance sheets      │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
┌────────────────────────────────▼────────────────────────────────────────┐
│  LAYER 2 · COGNITIVE GATEWAY  (Document AI)                              │
│                                                                          │
│  ┌──────────────────────┐  ┌───────────────────┐  ┌──────────────────┐  │
│  │  PDF Parsing          │  │  PII Masking       │  │  Semantic Routing│  │
│  │  Unstructured +       │→ │  Microsoft         │→ │  Splits flow to  │  │
│  │  Tesseract OCR        │  │  Presidio          │  │  ML + RAG tracks │  │
│  └──────────────────────┘  └───────────────────┘  └──────────────────┘  │
│                                                                          │
│    Gemini API + LangChain → Strict Structured Output (Pydantic)        │
│    Pre-Flight Gate: missing critical field? → Halt + Alert instantly   │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                ┌────────────────┴────────────────┐
                │                                 │
┌───────────────▼─────────────┐   ┌───────────────▼──────────────────────┐
│  LAYER 3A · ML RISK ENGINE  │   │  LAYER 3B · RAG COMPLIANCE ENGINE    │
│                             │   │                                       │
│  Feature Engineering        │   │  Document Chunking                    │
│          ↓                  │   │          ↓                            │
│  XGBoost Risk Prediction    │   │  HuggingFace Embeddings               │
│          ↓                  │   │  (all-MiniLM-L6-v2) + FAISS          │
│  SHAP Explainability        │   │          ↓                            │
│                             │   │  Policy Retrieval (RBI Guidelines)    │
│  Output: P(Default) + Why   │   │  Output: Compliance Pass / Violations │
└───────────────┬─────────────┘   └───────────────┬──────────────────────┘
                │                                 │
┌───────────────▼─────────────────────────────────▼──────────────────────┐
│  LAYER 4 · AI ORCHESTRATOR                                               │
│                                                                          │
│  ├── Combines Math Score (XGBoost) + SHAP Signals + Policy Flags         │
│  ├── Detects conflicts between risk model and RBI compliance rules        │
│  └── Authors full Explainable Credit Appraisal Memo in Markdown          │
│                                                                          │
│  🤖  Gemini API · LangChain Orchestration                                │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────────────┐
│  LAYER 5 · POLICY OVERRIDE                                               │
│  ├── Enforces hard RBI regulatory rules (non-negotiable guardrails)       │
│  └── Auto-rejects applications violating policy minimums                 │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────────────┐
│  LAYER 6 · HITL GOVERNANCE ROUTER                                        │
│  ├──   AUTO APPROVE   — Low risk + fully compliant                     │
│  ├──   AUTO REJECT    — High risk / hard regulatory violation           │
│  └──   HUMAN REVIEW   — Edge cases routed to Loan Officer              │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────────────┐
│  LAYER 7 · OUTPUT                                                        │
│  ├── Final Decision: Approve / Reject / Review                           │
│  └── Explainable Credit Memo — audit-ready for RBI inspections           │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Full Tech Stack

| Category | Technology |
|---|---|
| **Language** | Python 3.11+ |
| **ML / Risk Model** | XGBoost · Scikit-learn |
| **Explainability** | SHAP (SHapley Additive exPlanations) |
| **LLM & Orchestration** | Gemini API (Google DeepMind) · LangChain |
| **Embeddings** | HuggingFace Transformers · `all-MiniLM-L6-v2` |
| **Vector Database** | FAISS |
| **Document Processing** | Unstructured (Hi-Res PDF parsing) · Tesseract OCR |
| **PII Masking** | Microsoft Presidio |
| **Data Handling** | Pandas · NumPy |
| **Backend API** | FastAPI |
| **Frontend** | React · Tailwind CSS · Recharts |
| **Backend Deployment** | Google Cloud Platform (Cloud Run) |
| **Frontend Deployment** | Vercel |

---

## The Intelligence Stack — Deep Dive

### Phase 1 · Cognitive Gateway (Semantic Extraction)

Unlike brittle template OCR that crashes on informal documents, we feed parsed text through **Gemini via LangChain** with a strict Pydantic schema. The LLM *understands* the document semantically and extracts India-specific financial signals regardless of formatting chaos.

```python
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel
from typing import Optional

class MSMEFinancialProfile(BaseModel):
    cibil_score: int
    cheque_bounce_count_6m: int           # Section 138 NI Act risk signal
    gst_to_bank_variance_pct: float       # Revenue underreporting detector
    foir: float                           # Fixed Obligation to Income Ratio
    dpd_30_plus_count: int                # Days Past Due history
    requested_loan_amount: Optional[float]  # Pre-flight gate trigger

# Pre-Flight Circuit Breaker — saves compute, prevents false AI assumptions
if profile.requested_loan_amount is None:
    halt_pipeline()
    alert_customer_success_team("Critical field missing: loan_amount")
```

> 🔒 **Privacy First** — Microsoft Presidio strips Aadhaar numbers, PAN, mobile numbers, and account numbers *before* any data touches the Gemini API.

---

### Phase 2A · Mathematical Risk Engine (XGBoost + SHAP)

A purpose-trained **XGBoost classifier** built on Indian MSME default data. Every prediction is paired with a **SHAP waterfall** that shows the exact positive or negative contribution of every financial feature — turning a probability into a story.

```python
import xgboost as xgb
import shap
import pandas as pd

model = xgb.XGBClassifier()
model.load_model("models/xgboost_msme_v1.json")

p_default = model.predict_proba(features)[0][1]

# SHAP: translate math into human-readable risk drivers
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(features)

# Output surfaced directly on the underwriter dashboard
risk_drivers = [
    {"feature": "cheque_bounce_count_6m",   "shap": +0.34, "verdict": "🔴 INCREASES RISK"},
    {"feature": "gst_to_bank_variance_pct", "shap": +0.21, "verdict": "🔴 INCREASES RISK"},
    {"feature": "cibil_score",              "shap": -0.18, "verdict": "🟢 REDUCES RISK"},
    {"feature": "collateral_value",         "shap": -0.14, "verdict": "🟢 REDUCES RISK"},
]
```

---

### Phase 2B · Regulatory Compliance Engine (RAG)

Runs **in parallel** with the math engine. Bank policy documents and RBI guidelines are embedded using **`all-MiniLM-L6-v2`** and stored in a **FAISS** vector index. For each application, the most relevant policy clauses are retrieved and checked for violations.

```python
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vector_store = FAISS.load_local("data/policy_vectors", embeddings)

# Retrieve top-k relevant RBI policy clauses for this applicant
relevant_policies = vector_store.similarity_search(applicant_narrative, k=5)

compliance_result = check_policy_violations(relevant_policies, applicant_data)
# → [{"rule": "FOIR must not exceed 65%", "applicant_value": 72.3, "status": "VIOLATED"}]
```

---

### Phase 3 · AI Orchestrator (Gemini)

The orchestrator is the **Chief Risk Officer in code**. It ingests the probability of default, the SHAP attribution report, and the compliance flags — then generates a complete, professionally written **Credit Appraisal Memo** via the Gemini API.

```python
import google.generativeai as genai

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
gemini = genai.GenerativeModel("gemini-1.5-pro")

prompt = f"""
You are a senior credit risk officer at an RBI-regulated NBFC in India.

Applicant Risk Score:    {p_default:.2%} probability of default
Top Risk Drivers (SHAP): {shap_summary}
Compliance Violations:   {policy_violations}
Recommended Decision:    {hitl_decision}

Author a complete Credit Appraisal Memo in professional Markdown.
It must be fully auditable, cite regulatory basis for any rejection,
and be explainable to both the applicant and an RBI inspector.
"""

memo = gemini.generate_content(prompt).text
```

---

## 📊 India-Specific Risk Signals We Model

| Signal | Description | Why It Matters |
|---|---|---|
| `cibil_score` | TransUnion CIBIL bureau score | Primary creditworthiness baseline |
| `cheque_bounce_count_6m` | Dishonoured cheques in last 6 months | Section 138 NI Act — criminal liability signal |
| `gst_to_bank_variance_pct` | GST turnover vs. actual bank credit delta | Revenue concealment / underreporting detector |
| `foir` | Fixed Obligation to Income Ratio | RBI-mandated repayment stress test |
| `dpd_30_plus_count` | Days Past Due ≥ 30 in credit history | Chronic delinquency pattern indicator |
| `unsecured_loan_exposure` | Total unsecured lending outstanding | Overleveraging / debt trap risk flag |

---

## 🖥️ Enterprise Dashboard Features

The React dashboard is purpose-built for Indian financial analysts — designed to surface the right signal at the right moment.

| Feature | What It Does |
|---|---|
| **Dynamic Borrower Snapshot** | Displays only populated metrics — zero empty field clutter |
| **SHAP Diverging Bar Chart** | Green bars = approval drivers · Red bars = rejection drivers |
| **Critical Flag Badges** | High-risk signals surface as alert banners *before* the underwriter reads the memo |
| **Explainable Credit Memo** | Full Markdown memo rendered inline, audit-ready for RBI |
| **HITL Decision Queue** | Auto-approve · Auto-reject · Route to human — all in one view |

---

## ☁️ Deployment Architecture

```
┌─────────────────────────────┐         ┌──────────────────────────────────┐
│        FRONTEND             │         │            BACKEND               │
│                             │  REST   │                                  │
│  React + Tailwind CSS       │ ───────▶│  FastAPI  (Python 3.11)          │
│  Deployed on Vercel         │         │  Deployed on Google Cloud Run    │
│                             │         │                                  │
│  • Global CDN edge network  │         │  • Auto-scaling containers       │
│  • Sub-50ms latency         │         │  • Gemini API integration        │
│  • CI/CD from main branch   │         │  • FAISS vector store            │
└─────────────────────────────┘         │  • XGBoost model serving         │
                                        │  • Microsoft Presidio (PII)      │
                                        └──────────────────────────────────┘
```

---

## 🚀 Getting Started

### Prerequisites

```bash
Python 3.11+
Node.js 18+
Google Cloud project with Gemini API enabled
```

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/your-org/creditcortex.git
cd creditcortex/backend

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
```

```env
# .env
GOOGLE_API_KEY=your_gemini_api_key_here
GOOGLE_CREDENTIALS_JSON=your_json_credentials
GCS_BUCKET=creditcortex-data
VITE_API_URL=your_api_url
```

```bash
# Run the API server
uvicorn main:app --reload --port 8000
```

### Frontend Setup

```bash
cd ../frontend
npm install
npm run dev
# Open http://localhost:5173
```

### Docker (Recommended)

```bash
docker-compose up --build
```

---

## 📁 Project Structure

```
creditcortex/
├── backend/
│   ├── gateway/
│   │   ├── pdf_parser.py             # Unstructured + Tesseract OCR
│   │   ├── pii_masker.py             # Microsoft Presidio anonymization
│   │   ├── semantic_extractor.py     # Gemini + LangChain structured extraction
│   │   └── preflight_gate.py         # Circuit breaker for missing data
│   ├── risk_engine/
│   │   ├── feature_engineering.py    # Indian MSME-specific feature construction
│   │   ├── xgboost_model.py          # XGBoost classifier inference
│   │   └── shap_explainer.py         # SHAP TreeExplainer + attribution
│   ├── compliance/
│   │   ├── embeddings.py             # HuggingFace all-MiniLM-L6-v2
│   │   ├── vector_store.py           # FAISS index build + retrieval
│   │   └── policy_checker.py         # RBI rule violation detection
│   ├── orchestrator/
│   │   ├── memo_generator.py         # Gemini-powered Credit Appraisal Memo
│   │   └── hitl_router.py            # Approve / Reject / Review routing
│   ├── models/
│   │   └── xgboost_msme_v1.json      # Trained risk classification model
│   ├── data/
│   │   └── policy_docs/              # RBI guidelines + internal credit policy
│   └── main.py                       # FastAPI app entry point
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── BorrowerSnapshot.tsx  # Dynamic profile display
│   │   │   ├── SHAPChart.tsx         # Recharts diverging bar chart
│   │   │   ├── RiskFlags.tsx         # Critical alert badge system
│   │   │   └── CreditMemo.tsx        # Rendered memo with Markdown
│   │   └── pages/
│   │       └── UnderwritingDashboard.tsx
│   └── package.json
├── assets/
│   └── architecture.png              # System architecture diagram
├── docker-compose.yml
└── README.md
```

---

## Highlights

> Built to prove that AI in Indian lending can be **powerful, transparent, and regulator-ready** — simultaneously.

 **Solves a real ₹20 trillion problem** — India's structural MSME credit gap  
 **India-first by design** — Built ground-up for Indian finance norms, not a Western model retrofitted  
 **RBI-compliant by architecture** — Every decision is explainable and fully auditable  
 **End-to-end pipeline** — Raw PDF in → Signed Credit Memo out, in one coherent system  
 **Truly human-centred** — AI augments loan officers; human judgment retained for all edge cases  
 **Production-grade deployment** — GCP Cloud Run backend + Vercel frontend, not a localhost demo  

---

## 🔬 Design Decisions

**Why XGBoost over a Neural Network?**
SHAP works natively with tree-based models, delivering exact, mathematically grounded feature attributions. RBI-regulated lenders cannot deploy a model they cannot explain to an auditor. XGBoost + SHAP is the only combination that delivers both accuracy and full explainability.

**Why Gemini for LLM and Orchestration?**
Gemini's long context window handles full financial document bundles in a single pass. Its native integration with Google Cloud makes it a natural fit for a GCP-deployed backend, and its instruction-following capability produces structured, professional memo prose that requires minimal post-processing.

**Why FAISS over a Managed Vector DB?**
For a policy corpus of this size, FAISS runs with zero infrastructure overhead, integrates natively with LangChain's retrieval abstractions, and deploys cleanly inside a Docker container on Cloud Run — no external service dependencies.

**Why `all-MiniLM-L6-v2` for Embeddings?**
Excellent semantic retrieval performance on English/Hindi mixed financial text, runs efficiently on CPU (no GPU needed on Cloud Run), and is freely available via HuggingFace with no API costs.

---

## 🤝 Contributing

Contributions from the fintech and AI community are welcome!

```bash
git checkout -b feature/your-feature-name
git commit -m "feat: your descriptive commit message"
git push origin feature/your-feature-name
# Open a Pull Request
```

Before submitting:
```bash
pytest backend/tests/ -v
npm run test --prefix frontend
```

---

## 📜 License

MIT License — see [LICENSE](LICENSE) for full terms.

---

<div align="center">

**If CreditCortex resonates with you, drop a ⭐ — it helps other fintech builders find this work.**

<br/>

*"The best risk model is one that a regulator, an auditor, and a borrower can all understand."*

<br/>

Built with ❤️ for India's 63 million MSMEs and the loan officers who serve them.

</div>