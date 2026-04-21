import os
import re
import unicodedata
from dataclasses import dataclass
from typing import Dict, List, Optional

import pandas as pd
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from pydantic import BaseModel, Field
load_dotenv()


class ApplicantFinancials(BaseModel):
    loan_amnt: Optional[float] = Field(
        default=None,
        description="Total loan amount requested in raw rupees. Remove currency symbols and commas. Convert Lakhs/Crores to numbers.",
    )
    annual_inc: Optional[float] = Field(
        default=None,
        description="Annual income, revenue, or turnover in raw rupees. Prefer annual labels. If absent, derive from monthly income x 12.",
    )
    cibil_score: Optional[float] = Field(
        default=None,
        description="The applicant's CIBIL, bureau, Experian, or Equifax score. Return the 3-digit score only.",
    )
    cheque_bounce_count_6m: Optional[float] = Field(
        default=0.0,
        description="Cheque bounce, inward return, or failed NACH/ECS mandate count in the last 6 months.",
    )
    avg_monthly_balance: Optional[float] = Field(
        default=None,
        description="Average Monthly Balance (AMB) maintained in the bank account in raw rupees.",
    )
    foir: Optional[float] = Field(
        default=None,
        description="Fixed Obligation to Income Ratio as a percentage without the percent sign.",
    )
    gst_to_bank_variance_pct: Optional[float] = Field(
        default=0.0,
        description="Variance between GST turnover and bank credits as a percentage without the percent sign.",
    )
    business_vintage_years: Optional[float] = Field(
        default=None,
        description="Business operating history in years.",
    )
    max_dpd_12m: Optional[float] = Field(
        default=0.0,
        description="Maximum DPD in the last 12 months.",
    )
    recent_enquiries_6m: Optional[float] = Field(
        default=0.0,
        description="Hard enquiries in the last 6 months.",
    )


@dataclass
class ExtractionCandidate:
    value: float
    source: str
    confidence: float
    snippet: str


@dataclass
class DocumentTextCandidate:
    source: str
    raw_text: str
    normalized_text: str
    extracted_dict: Dict[str, Optional[float]]
    missing: List[str]
    score: float


class CognitiveGateway:
    REQUIRED_FIELDS = ("loan_amnt", "annual_inc", "cibil_score")
    PERCENTAGE_FIELDS = {"foir", "gst_to_bank_variance_pct"}
    COUNT_FIELDS = {"cheque_bounce_count_6m", "max_dpd_12m", "recent_enquiries_6m"}
    EXACT_LABEL_PATTERNS = {
        "loan_amnt": [
            r"loan amount requested",
            r"amount requested",
            r"loan amount",
        ],
        "annual_inc": [
            r"annual income(?:\s*\(itr\))?",
            r"gross annual income",
            r"annual turnover",
            r"annual revenue",
            r"income details\s*e\s*annual income",
        ],
        "cibil_score": [
            r"cibil\s*score(?:\s*\(mock\))?",
            r"\bcibil\b",
            r"bureau\s*score",
            r"credit\s*score\s*average",
            r"credit\s*score",
            r"mock\s*score",
        ],
        "avg_monthly_balance": [
            r"average monthly balance",
            r"avg monthly balance",
            r"\bamb\b",
            r"average balance",
        ],
        "foir": [
            r"fixed obligation to income ratio",
            r"\bfoir\b",
        ],
        "gst_to_bank_variance_pct": [
            r"gst\s*(?:vs|to)?\s*bank variance",
            r"vs bank variance",
            r"bank variance",
        ],
        "business_vintage_years": [
            r"business vintage(?:\s*\(years\))?",
            r"business vintage",
            r"vintage\s*\(years\)",
        ],
        "max_dpd_12m": [
            r"max dpd(?:\s*\(12\s*months?\))?",
            r"dpd\s*\(12m\)",
            r"dpd\s*\(12\s*months?\)",
        ],
        "recent_enquiries_6m": [
            r"recent enquiries\s*\(6m\)",
            r"recent enquiries\s*\(6\s*months?\)",
            r"recent enquiries",
        ],
        "cheque_bounce_count_6m": [
            r"cheque bounce count(?:\s*\(last 6 months\))?",
            r"cheque bounce count",
            r"cheque bounce\s*\(6m\)",
            r"cheque bounce",
        ],
    }
    MONTHLY_INCOME_PATTERNS = [
        r"monthly gross income",
        r"monthly net take-home",
        r"monthly net income",
        r"monthly income",
        r"net take-home",
    ]

    def __init__(self):
        print("Initializing LLM-Driven Semantic Extraction Gateway...")
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()
        self.llm = None
        self.structured_llm = None

        try:
            self.llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0)
            self.structured_llm = self.llm.with_structured_output(ApplicantFinancials)
        except Exception as exc:
            print(f"WARNING: LLM fallback disabled in Phase 1 gateway: {exc}")

    def mask_pii(self, text: str) -> str:
        """Mask sensitive identifiers while preserving financial narrative for logs/UI."""
        results = self.analyzer.analyze(
            text=text,
            entities=["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", "CREDIT_CARD"],
            language="en",
            score_threshold=0.4,
            allow_list=[
                "CIBIL",
                "Income",
                "EMI",
                "Tenure",
                "FOIR",
                "DPD",
                "GST",
                "Balance",
                "Amount Requested",
            ],
        )

        anonymized_result = self.anonymizer.anonymize(
            text=text,
            analyzer_results=results,
        )
        return anonymized_result.text

    @staticmethod
    def normalize_ocr_text(text: str) -> str:
        text = unicodedata.normalize("NFKC", text)
        replacements = {
            "\r": " ",
            "\n": " ",
            "\t": " ",
            "\u00a0": " ",
            "—": " - ",
            "–": " - ",
        }
        for old, new in replacements.items():
            text = text.replace(old, new)

        text = re.sub(r"[•●▪◦]+", " ", text)
        text = re.sub(r"\bEMls\b", "EMIs", text, flags=re.IGNORECASE)
        text = re.sub(r"\bEMl\b", "EMI", text, flags=re.IGNORECASE)
        text = re.sub(r"\bCheq\b", "Cheque", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*\|\s*", " | ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    @staticmethod
    def _find_label_contexts(
        text: str,
        label_patterns: List[str],
        before_window: int = 36,
        after_window: int = 120,
    ) -> List[Dict[str, object]]:
        contexts: List[Dict[str, object]] = []
        for pattern in label_patterns:
            for match in re.finditer(pattern, text, flags=re.IGNORECASE):
                start = max(0, match.start() - before_window)
                end = min(len(text), match.end() + after_window)
                contexts.append(
                    {
                        "label": match.group(0),
                        "before": text[start:match.start()],
                        "after": text[match.end():end],
                        "context": text[start:end],
                        "position": match.start(),
                    }
                )
        contexts.sort(key=lambda item: int(item["position"]))
        return contexts

    @staticmethod
    def _extract_number(token: str) -> Optional[float]:
        match = re.search(r"\d+(?:\.\d+)?", token)
        if not match:
            return None
        return float(match.group(0))

    def _parse_amount_token(self, token: str, field_name: str, segment: str) -> Optional[float]:
        compact = token.lower()
        compact = re.sub(r"(?i)\b(?:rs\.?|inr)\b", "", compact)
        compact = compact.replace("₹", "").replace(" ", "")

        multiplier = 1.0
        if re.search(r"crores?", compact):
            multiplier = 10000000.0
        elif re.search(r"lakhs?|lacs?", compact):
            multiplier = 100000.0

        compact = re.sub(r"crores?|lakhs?|lacs?", "", compact)

        had_rupee_noise_prefix = bool(re.match(r"^2[%=]", compact))
        compact = re.sub(r"^[=~:]+", "", compact)
        if had_rupee_noise_prefix:
            compact = compact[1:]
        compact = re.sub(r"^[%=~:]+", "", compact)

        match = re.search(r"\d[\d,]*(?:\.\d+)?", compact)
        if not match:
            return None

        primary_token = match.group(0)
        try:
            primary_value = float(primary_token.replace(",", "")) * multiplier
        except ValueError:
            return None

        if had_rupee_noise_prefix:
            return primary_value

        if re.match(r"^2\d{1,2},\d{2},\d{3}(?:\.\d+)?$", primary_token):
            alternate_value = float(primary_token[1:].replace(",", "")) * multiplier
            segment_lower = segment.lower()

            if "monthly" in segment_lower and 10000 <= alternate_value <= 1000000 and primary_value > 1000000:
                return alternate_value

            if "annual" in segment_lower and 50000 <= alternate_value <= 10000000 and primary_value > 10000000:
                return alternate_value

            if field_name == "loan_amnt" and 10000 <= alternate_value <= 10000000 and primary_value > 10000000:
                return alternate_value

        return primary_value

    def _extract_first_amount(self, segment: str, field_name: str) -> Optional[float]:
        token_patterns = [
            r"(?i)(?:₹|rs\.?|inr)?\s*(?:2[%=])?\s*[=%~]?\s*\d{1,2},\d{2},\d{3}(?:\.\d+)?(?:\s*(?:lakhs?|lacs?|crores?))?",
            r"(?i)(?:₹|rs\.?|inr)?\s*(?:2[%=])?\s*[=%~]?\s*\d{1,3}(?:,\d{3})+(?:\.\d+)?(?:\s*(?:lakhs?|lacs?|crores?))?",
            r"(?i)(?:₹|rs\.?|inr)?\s*(?:2[%=])?\s*[=%~]?\s*\d+(?:\.\d+)?\s*(?:lakhs?|lacs?|crores?)",
            r"(?i)(?:₹|rs\.?|inr)?\s*(?:2[%=])?\s*[=%~]?\s*\d+(?:\.\d+)?",
        ]

        matches = []
        seen_spans = set()
        for pattern in token_patterns:
            for match in re.finditer(pattern, segment):
                span = (match.start(), match.end())
                if span in seen_spans:
                    continue
                seen_spans.add(span)
                matches.append((match.start(), match.group(0)))

        for _, token in sorted(matches, key=lambda item: item[0]):
            value = self._parse_amount_token(token, field_name, segment)
            if value is not None and self._is_valid_value(field_name, value):
                return value
        return None

    def _extract_first_percentage(self, segment: str) -> Optional[float]:
        for pattern in [r"\d+(?:\.\d+)?\s*%", r"\d+(?:\.\d+)?"]:
            match = re.search(pattern, segment)
            if match:
                value = self._extract_number(match.group(0))
                if value is not None:
                    return value
        return None

    def _extract_first_count(self, segment: str) -> Optional[float]:
        match = re.search(r"\b\d+(?:\.\d+)?\b", segment)
        if not match:
            return None
        return float(match.group(0))

    def _extract_first_score(self, segment: str) -> Optional[float]:
        for match in re.finditer(r"\b\d{3}\b", segment):
            value = float(match.group(0))
            if 300 <= value <= 900:
                return value
        return None

    def _extract_first_years(self, segment: str) -> Optional[float]:
        match = re.search(r"\d+(?:\.\d+)?", segment)
        if not match:
            return None
        return float(match.group(0))

    @staticmethod
    def _nearest_match(matches: List[re.Match], anchor_index: int) -> Optional[re.Match]:
        if not matches:
            return None
        return min(
            matches,
            key=lambda match: (
                abs(match.start() - anchor_index),
                0 if match.start() <= anchor_index else 1,
            ),
        )

    def _extract_nearest_percentage(self, context: str, anchor_index: int) -> Optional[float]:
        percent_matches = list(re.finditer(r"\d+(?:\.\d+)?\s*%", context))
        chosen_match = self._nearest_match(percent_matches, anchor_index)
        if chosen_match:
            return self._extract_number(chosen_match.group(0))

        number_matches = list(re.finditer(r"\b\d+(?:\.\d+)?\b", context))
        chosen_match = self._nearest_match(number_matches, anchor_index)
        if chosen_match:
            return self._extract_number(chosen_match.group(0))
        return None

    def _extract_nearest_score(self, context: str, anchor_index: int) -> Optional[float]:
        score_matches = [
            match
            for match in re.finditer(r"\b\d{3}\b", context)
            if 300 <= float(match.group(0)) <= 900
        ]
        chosen_match = self._nearest_match(score_matches, anchor_index)
        if not chosen_match:
            return None
        return float(chosen_match.group(0))

    def _extract_cibil_candidate(self, text: str) -> Optional[ExtractionCandidate]:
        contexts = self._find_label_contexts(
            text,
            self.EXACT_LABEL_PATTERNS["cibil_score"],
            before_window=140,
            after_window=110,
        )

        contextual_patterns = [
            r"(?i)cibil.{0,80}(?:score|mock score|bureau score)[^\d]{0,20}(\d{3})",
            r"(?i)(?:score|mock score|bureau score)[^\d]{0,20}(\d{3}).{0,120}\bcibil\b",
            r"(?i)cibil[^\d]{0,20}(\d{3})",
        ]

        for ctx in contexts:
            context_text = str(ctx["context"])
            after_value = self._extract_first_score(str(ctx["after"]))
            after_value = self._normalize_field_value("cibil_score", after_value)
            if self._is_valid_value("cibil_score", after_value):
                return ExtractionCandidate(
                    value=after_value,
                    source="regex:cibil_score:after-label",
                    confidence=0.96,
                    snippet=context_text,
                )

            for pattern in contextual_patterns:
                match = re.search(pattern, context_text)
                if not match:
                    continue
                value = self._normalize_field_value("cibil_score", float(match.group(1)))
                if self._is_valid_value("cibil_score", value):
                    return ExtractionCandidate(
                        value=value,
                        source="regex:cibil_score:contextual",
                        confidence=0.84,
                        snippet=context_text,
                    )

        return None

    def _normalize_field_value(self, field_name: str, value: Optional[float]) -> Optional[float]:
        if value is None:
            return None

        if field_name in self.PERCENTAGE_FIELDS and 0 < value <= 1:
            value = value * 100
        elif field_name in self.PERCENTAGE_FIELDS and 100 < value <= 1000 and (value / 10) <= 100:
            value = value / 10

        if field_name in self.COUNT_FIELDS or field_name == "cibil_score":
            return float(int(round(value)))

        return float(round(value, 2))

    def _is_valid_value(self, field_name: str, value: Optional[float]) -> bool:
        if value is None:
            return False

        if field_name == "loan_amnt":
            return 1000 <= value <= 1000000000
        if field_name == "annual_inc":
            return 10000 <= value <= 10000000000
        if field_name == "cibil_score":
            return 300 <= value <= 900
        if field_name == "avg_monthly_balance":
            return value == 0 or 100 <= value <= 100000000
        if field_name == "foir":
            return 0 <= value <= 100
        if field_name == "gst_to_bank_variance_pct":
            return 0 <= value <= 100
        if field_name == "business_vintage_years":
            return 0 <= value <= 100
        if field_name == "max_dpd_12m":
            return 0 <= value <= 999
        if field_name in {"recent_enquiries_6m", "cheque_bounce_count_6m"}:
            return 0 <= value <= 200
        return True

    def _extract_field_from_labels(
        self,
        text: str,
        field_name: str,
        kind: str,
        include_context: bool = False,
    ) -> Optional[ExtractionCandidate]:
        before_window = 36
        after_window = 120
        if field_name == "foir":
            before_window = 72
            after_window = 96
        elif field_name == "cibil_score":
            before_window = 140
            after_window = 110

        contexts = self._find_label_contexts(
            text,
            self.EXACT_LABEL_PATTERNS[field_name],
            before_window=before_window,
            after_window=after_window,
        )
        extractor_map = {
            "amount": lambda segment: self._extract_first_amount(segment, field_name),
            "percentage": self._extract_first_percentage,
            "count": self._extract_first_count,
            "score": self._extract_first_score,
            "years": self._extract_first_years,
        }
        extractor = extractor_map[kind]

        for ctx in contexts:
            if field_name != "foir":
                after_value = extractor(ctx["after"])
                after_value = self._normalize_field_value(field_name, after_value)
                if self._is_valid_value(field_name, after_value):
                    return ExtractionCandidate(
                        value=after_value,
                        source=f"regex:{field_name}:after-label",
                        confidence=0.96 if field_name in self.REQUIRED_FIELDS else 0.93,
                        snippet=ctx["context"],
                    )

            if include_context:
                anchor_index = len(str(ctx["before"]))
                if field_name == "foir":
                    context_value = self._extract_nearest_percentage(str(ctx["context"]), anchor_index)
                elif field_name == "cibil_score":
                    context_value = self._extract_nearest_score(str(ctx["context"]), anchor_index)
                else:
                    context_value = extractor(str(ctx["context"]))
                context_value = self._normalize_field_value(field_name, context_value)
                if self._is_valid_value(field_name, context_value):
                    return ExtractionCandidate(
                        value=context_value,
                        source=f"regex:{field_name}:near-label",
                        confidence=0.82,
                        snippet=ctx["context"],
                    )

        return None

    def _derive_annual_income(self, text: str) -> Optional[ExtractionCandidate]:
        for pattern in self.MONTHLY_INCOME_PATTERNS:
            contexts = self._find_label_contexts(text, [pattern], before_window=16, after_window=80)
            for ctx in contexts:
                monthly_income = self._extract_first_amount(ctx["after"], "annual_inc")
                monthly_income = self._normalize_field_value("annual_inc", monthly_income)
                if monthly_income is None:
                    continue

                annual_income = self._normalize_field_value("annual_inc", monthly_income * 12)
                if self._is_valid_value("annual_inc", annual_income):
                    return ExtractionCandidate(
                        value=annual_income,
                        source="derived:monthly-income-x12",
                        confidence=0.72,
                        snippet=ctx["context"],
                    )
        return None

    def _run_deterministic_extraction(self, text: str) -> Dict[str, ExtractionCandidate]:
        candidates: Dict[str, ExtractionCandidate] = {}

        direct_annual = self._extract_field_from_labels(text, "annual_inc", "amount")
        if direct_annual:
            candidates["annual_inc"] = direct_annual
        else:
            derived_annual = self._derive_annual_income(text)
            if derived_annual:
                candidates["annual_inc"] = derived_annual

        extraction_plan = [
            ("loan_amnt", "amount", False),
            ("avg_monthly_balance", "amount", False),
            ("foir", "percentage", True),
            ("gst_to_bank_variance_pct", "percentage", False),
            ("business_vintage_years", "years", False),
            ("max_dpd_12m", "count", False),
            ("recent_enquiries_6m", "count", False),
            ("cheque_bounce_count_6m", "count", False),
        ]

        for field_name, kind, include_context in extraction_plan:
            candidate = self._extract_field_from_labels(
                text=text,
                field_name=field_name,
                kind=kind,
                include_context=include_context,
            )
            if candidate:
                candidates[field_name] = candidate

        cibil_candidate = self._extract_cibil_candidate(text)
        if cibil_candidate:
            candidates["cibil_score"] = cibil_candidate

        return candidates

    @staticmethod
    def _applicant_fields() -> List[str]:
        return list(ApplicantFinancials.model_fields.keys())

    def _needs_llm_fallback(self, deterministic: Dict[str, ExtractionCandidate]) -> bool:
        for field_name in self._applicant_fields():
            if field_name not in deterministic:
                return True
            if deterministic[field_name].confidence < 0.85:
                return True
        return False

    def _run_llm_fallback(self, normalized_text: str) -> Dict[str, Optional[float]]:
        if self.structured_llm is None:
            return {}

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You extract structured financial fields from OCR text for Indian loan underwriting.

Rules:
- Use only label-supported values from the document. Do not guess.
- Prefer the value nearest the correct label.
- OCR noise may introduce characters such as '=', '~', '%' or a leading '2' in place of the rupee symbol.
- For loan_amnt and annual_inc, return raw rupee numbers, not lakhs/crores text.
- Prefer annual income/revenue labels. Only derive annual_inc from monthly income when annual income is absent.
- For cibil_score, return the 3-digit bureau score near labels like CIBIL, bureau score, credit score, or mock score.
- For foir and gst_to_bank_variance_pct, return percentage numbers without the percent sign.
- If a field is not reliably present, return null for that field.""",
                ),
                ("user", "Extract structured applicant financials from this OCR text:\n\n{text}"),
            ]
        )

        try:
            extraction_chain = prompt | self.structured_llm
            extracted_data = extraction_chain.invoke({"text": normalized_text})
        except Exception as exc:
            print(f"WARNING: Phase 1 LLM fallback failed, using deterministic extraction only: {exc}")
            return {}

        llm_dict: Dict[str, Optional[float]] = {}
        for field_name, raw_value in extracted_data.model_dump().items():
            normalized_value = self._normalize_field_value(field_name, raw_value)
            llm_dict[field_name] = normalized_value if self._is_valid_value(field_name, normalized_value) else None
        return llm_dict

    def _reconcile_extractions(
        self,
        deterministic: Dict[str, ExtractionCandidate],
        llm_values: Dict[str, Optional[float]],
    ) -> Dict[str, Optional[float]]:
        final_values: Dict[str, Optional[float]] = {}

        for field_name in self._applicant_fields():
            deterministic_candidate = deterministic.get(field_name)
            llm_value = llm_values.get(field_name)

            if deterministic_candidate and self._is_valid_value(field_name, deterministic_candidate.value):
                if deterministic_candidate.confidence >= 0.9 or llm_value is None:
                    final_values[field_name] = deterministic_candidate.value
                    continue

            if self._is_valid_value(field_name, llm_value):
                final_values[field_name] = llm_value
                continue

            if deterministic_candidate and self._is_valid_value(field_name, deterministic_candidate.value):
                final_values[field_name] = deterministic_candidate.value
                continue

            final_values[field_name] = None

        return final_values

    def extract_structured_data(self, raw_text: str):
        normalized_text = self.normalize_ocr_text(raw_text)
        deterministic_candidates = self._run_deterministic_extraction(normalized_text)
        llm_values = self._run_llm_fallback(normalized_text) if self._needs_llm_fallback(deterministic_candidates) else {}
        extracted_dict = self._reconcile_extractions(deterministic_candidates, llm_values)
        missing = [field for field in self.REQUIRED_FIELDS if extracted_dict.get(field) is None]
        return extracted_dict, normalized_text, missing

    @staticmethod
    def _has_meaningful_text(text: str) -> bool:
        stripped = text.strip()
        if len(stripped) < 80:
            return False
        alpha_chars = sum(char.isalpha() for char in stripped)
        return alpha_chars >= 40

    def _extract_text_with_pypdf(self, file_path: str) -> Optional[str]:
        try:
            from pypdf import PdfReader
        except Exception:
            return None

        try:
            reader = PdfReader(file_path)
            pages = [(page.extract_text() or "").strip() for page in reader.pages]
            text = "\n".join(page for page in pages if page).strip()
            return text if self._has_meaningful_text(text) else None
        except Exception as exc:
            print(f"WARNING: PyPDF extraction failed for {file_path}: {exc}")
            return None

    def _extract_text_with_pdfplumber(self, file_path: str) -> Optional[str]:
        try:
            import pdfplumber
        except Exception:
            return None

        try:
            with pdfplumber.open(file_path) as pdf:
                pages = [(page.extract_text() or "").strip() for page in pdf.pages]
            text = "\n".join(page for page in pages if page).strip()
            return text if self._has_meaningful_text(text) else None
        except Exception as exc:
            print(f"WARNING: pdfplumber extraction failed for {file_path}: {exc}")
            return None

    def _extract_text_with_unstructured(self, file_path: str) -> Optional[str]:
        try:
            from unstructured.partition.pdf import partition_pdf
        except Exception as exc:
            print(f"WARNING: unstructured PDF extraction unavailable for {file_path}: {exc}")
            return None

        try:
            elements = partition_pdf(filename=file_path, strategy="hi_res")
            text = " ".join(str(element) for element in elements).strip()
            return text if self._has_meaningful_text(text) else None
        except Exception as exc:
            print(f"WARNING: unstructured hi_res extraction failed for {file_path}: {exc}")
            return None

    def _score_document_candidate(
        self,
        source: str,
        raw_text: str,
        extracted_dict: Dict[str, Optional[float]],
        missing: List[str],
    ) -> float:
        non_null_count = sum(value is not None for value in extracted_dict.values())
        required_present = len(self.REQUIRED_FIELDS) - len(missing)

        source_bonus = {
            "pypdf": 8,
            "pdfplumber": 6,
            "unstructured_hi_res": 2,
        }.get(source, 0)

        keyword_bonus = 0
        lowered = raw_text.lower()
        for token in ("amount requested", "monthly gross income", "cibil", "foir"):
            if token in lowered:
                keyword_bonus += 2

        noise_penalty = 0
        noise_penalty += len(re.findall(r"\bEMls\b", raw_text, flags=re.IGNORECASE)) * 3
        noise_penalty += len(re.findall(r"(?:=|%|~)\d{1,2},\d{2},\d{3}", raw_text)) * 2
        noise_penalty += len(re.findall(r"\b2[%=]\d", raw_text)) * 2

        return (required_present * 100) + (non_null_count * 10) + source_bonus + keyword_bonus - noise_penalty

    def _build_document_candidate(self, source: str, raw_text: Optional[str]) -> Optional[DocumentTextCandidate]:
        if not raw_text or not self._has_meaningful_text(raw_text):
            return None

        extracted_dict, normalized_text, missing = self.extract_structured_data(raw_text)
        score = self._score_document_candidate(source, raw_text, extracted_dict, missing)

        return DocumentTextCandidate(
            source=source,
            raw_text=raw_text,
            normalized_text=normalized_text,
            extracted_dict=extracted_dict,
            missing=missing,
            score=score,
        )

    def _select_best_text_candidate(self, file_path: str) -> DocumentTextCandidate:
        candidates: List[DocumentTextCandidate] = []
        seen_texts = set()

        for source, extractor in (
            ("pypdf", self._extract_text_with_pypdf),
            ("pdfplumber", self._extract_text_with_pdfplumber),
        ):
            raw_text = extractor(file_path)
            if not raw_text:
                continue

            normalized_key = self.normalize_ocr_text(raw_text)
            if normalized_key in seen_texts:
                continue
            seen_texts.add(normalized_key)

            candidate = self._build_document_candidate(source, raw_text)
            if candidate:
                candidates.append(candidate)

        if candidates:
            best_native = max(candidates, key=lambda candidate: candidate.score)
            if not best_native.missing:
                print(f"-> Selected native PDF text source: {best_native.source}")
                return best_native

        unstructured_text = self._extract_text_with_unstructured(file_path)
        if unstructured_text:
            normalized_key = self.normalize_ocr_text(unstructured_text)
            if normalized_key not in seen_texts:
                candidate = self._build_document_candidate("unstructured_hi_res", unstructured_text)
                if candidate:
                    candidates.append(candidate)

        if not candidates:
            raise RuntimeError("No readable text could be extracted from the PDF.")

        best_candidate = max(candidates, key=lambda candidate: candidate.score)
        print(
            "-> Text source scores:",
            {candidate.source: candidate.score for candidate in candidates},
        )
        print(f"-> Selected text source: {best_candidate.source}")
        return best_candidate

    def process_document(self, file_path: str, tabular_output_path: str, text_output_path: str):
        print(f"\nProcessing Document: {file_path}")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Raw PDF not found at {file_path}")

        best_candidate = self._select_best_text_candidate(file_path)
        extracted_dict = best_candidate.extracted_dict
        masked_text = self.mask_pii(best_candidate.normalized_text)
        missing = best_candidate.missing

        os.makedirs(os.path.dirname(text_output_path), exist_ok=True)
        with open(text_output_path, "w", encoding="utf-8") as file_handle:
            file_handle.write(masked_text)

        os.makedirs(os.path.dirname(tabular_output_path), exist_ok=True)
        pd.DataFrame([extracted_dict]).to_csv(tabular_output_path, index=False)

        gateway_status = {"status": "HALTED" if missing else "SUCCESS", "missing": missing}

        print(f"-> Deterministic + validated extraction output: {extracted_dict}")
        if missing:
            print(f"-> Gateway halted. Missing critical fields: {missing}")
        print(f"-> Pipeline Complete. Features saved to {tabular_output_path}")

        return gateway_status, masked_text
