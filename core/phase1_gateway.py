import pandas as pd
from unstructured.partition.pdf import partition_pdf
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

class CognitiveGateway:
    def __init__(self):
        print("Initializing Document Understanding Model & Privacy Engines...")
        # Initialize Microsoft Presidio for local PII masking
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()

    def mask_pii(self, text: str) -> str:
        """Scans text for PII (Names, Emails, Phone Numbers) and masks it."""
        results = self.analyzer.analyze(text=text, entities=["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", "CREDIT_CARD"], language='en')
        anonymized_result = self.anonymizer.anonymize(text=text, analyzer_results=results)
        return anonymized_result.text

    def process_document(self, file_path: str):
        """The DUM: Extracts and categorizes elements using layout mapping."""
        print(f"\nProcessing: {file_path}")
        
        # 'unstructured' uses ML layout parsing to find tables and text separately
        elements = partition_pdf(
            filename=file_path,
            strategy="hi_res", # Uses layout-aware ML models
            infer_table_structure=True 
        )

        tabular_data = []
        unstructured_text = []

        # The Semantic Router Node
        for element in elements:
            element_type = type(element).__name__
            
            if element_type == "Table":
                # Route to Track A (ML Math)
                tabular_data.append(element.metadata.text_as_html)
            elif element_type in ["Text", "NarrativeText", "Title"]:
                # Mask PII and Route to Track B (RAG Logic)
                clean_text = self.mask_pii(element.text)
                unstructured_text.append(clean_text)

        return tabular_data, unstructured_text

# --- Execution ---
if __name__ == "__main__":
    gateway = CognitiveGateway()
    
    # Mocking the execution for demonstration:
    print("\n--- Pipeline Ready ---")
    print("1. Awaiting PDF Upload.")
    print("2. DUM will separate Financial Tables from Business Narratives.")
    print("3. PII Node will scrub sensitive entities locally.")
    print("4. Router will push data to Track A (CSV) and Track B (Text).")