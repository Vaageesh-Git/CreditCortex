import os
import io
import pandas as pd
from unstructured.partition.pdf import partition_pdf
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

class CognitiveGateway:
    def __init__(self):
        print("Initializing Document Understanding Model & Privacy Engines...")
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()

    def mask_pii(self, text: str) -> str:
        """Scans text for PII (Names, Emails, Phone Numbers) and masks it."""
        results = self.analyzer.analyze(
            text=text, 
            entities=["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", "CREDIT_CARD"], 
            language='en'
        )
        anonymized_result = self.anonymizer.anonymize(text=text, analyzer_results=results)
        return anonymized_result.text

    def process_document(self, file_path: str, tabular_output_path: str, text_output_path: str):
        """
        Extracts, categorizes, masks, and SAVES the elements to disk 
        so downstream pipelines can read them.
        """
        print(f"\nProcessing Document: {file_path}")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Raw PDF not found at {file_path}")

        elements = partition_pdf(
            filename=file_path,
            strategy="hi_res", 
            infer_table_structure=True 
        )

        tabular_data_html = []
        unstructured_text = []

        # 1. Route and Mask
        for element in elements:
            element_type = type(element).__name__
            
            if element_type == "Table":
                tabular_data_html.append(element.metadata.text_as_html)
            elif element_type in ["Text", "NarrativeText", "Title"]:
                clean_text = self.mask_pii(element.text)
                unstructured_text.append(clean_text)

        # 2. Save Text for RAG (Track B)
        os.makedirs(os.path.dirname(text_output_path), exist_ok=True)
        with open(text_output_path, "w", encoding="utf-8") as f:
            f.write("\n\n".join(unstructured_text))
        print(f"-> Masked text saved to: {text_output_path}")

        # 3. Save Tabular Data for ML (Track A)
        os.makedirs(os.path.dirname(tabular_output_path), exist_ok=True)
        if tabular_data_html:
            try:
                # Wrap the HTML string in io.StringIO to prevent Pandas from treating it as a file path
                html_buffer = io.StringIO(tabular_data_html[0])
                dfs = pd.read_html(html_buffer)
                
                if dfs:
                    dfs[0].to_csv(tabular_output_path, index=False)
                    print(f"-> Extracted tables saved to: {tabular_output_path}")
            except Exception as e:
                print(f"-> Error converting extracted HTML table to CSV: {e}")
        else:
            print("-> Warning: No tabular data found in this document.")

        return tabular_data_html, unstructured_text