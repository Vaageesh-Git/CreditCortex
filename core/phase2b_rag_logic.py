import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

class RAGComplianceEngine:
    def __init__(self, vector_dir="core/vector_store/"):
        self.vector_dir = vector_dir
        os.makedirs(self.vector_dir, exist_ok=True)
        print("Loading local embedding model...")
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.vector_db = None

    def ingest_policy_documents(self, pdf_path: str, index_name: str = "rbi_policies"):
        """Runs offline. Ingests a regulatory PDF, chunks it, and saves the vectors."""
        print(f"--- INITIATING POLICY INGESTION PIPELINE ---")
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"Policy document not found at {pdf_path}")

        print("1. Reading PDF Document...")
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()

        print("2. Chunking Document into Semantic Blocks...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800, 
            chunk_overlap=150,
            separators=["\n\n", "\n", ".", " ", ""]
        )
        chunks = text_splitter.split_documents(documents)

        print(f"3. Embedding {len(chunks)} chunks and saving to FAISS Vector DB...")
        self.vector_db = FAISS.from_documents(chunks, self.embeddings)

        save_path = os.path.join(self.vector_dir, index_name)
        self.vector_db.save_local(save_path)
        print(f"SUCCESS: Knowledge Graph saved to {save_path}\n")

    def load_knowledge_graph(self, index_name: str = "rbi_policies"):
        """Loads the saved vector database into memory for lightning-fast retrieval."""
        load_path = os.path.join(self.vector_dir, index_name)
        if not os.path.exists(load_path):
            raise RuntimeError("Vector database not found. Run ingestion first.")
            
        self.vector_db = FAISS.load_local(
            load_path, 
            self.embeddings, 
            allow_dangerous_deserialization=True
        )

    def evaluate_compliance(self, borrower_profile_text: str, top_k: int = 3):
        """The production function. Searches the policies based on the borrower's request."""
        if self.vector_db is None:
            self.load_knowledge_graph()

        search_query = f"What are the eligibility limits, requirements, and priority sector rules for: {borrower_profile_text}"
        
        retrieved_docs = self.vector_db.similarity_search(search_query, k=top_k)
        
        policy_context = ""
        for i, doc in enumerate(retrieved_docs):
            page_num = doc.metadata.get('page', 'Unknown')
            policy_context += f"[Citation {i+1} | Page {page_num}]: {doc.page_content}\n\n"
            
        return policy_context

# --- Execution Simulation ---
if __name__ == "__main__":
    engine = RAGComplianceEngine()
    
    POLICY_DOC_PATH = "system_data/policy_data/RBI_Loan_Guidelines.pdf"
    
    # Toggle this flag to simulate the deployment environment
    IS_POLICY_UPDATE_DAY = False 
    
    if IS_POLICY_UPDATE_DAY:
        try:
            engine.ingest_policy_documents(POLICY_DOC_PATH)
        except FileNotFoundError as e:
            print(e)
    else:
        print("--- REAL-TIME COMPLIANCE CHECK ---")
        
        masked_borrower_profile = "MSME business in Renewable Energy sector seeking 45 Lakhs for solar panel manufacturing. GSTIN verified."
        
        try:
            retrieved_rules = engine.evaluate_compliance(masked_borrower_profile)
            
            print(f"Borrower Profile:\n{masked_borrower_profile}\n")
            print("Retrieved Regulatory Context (To be sent to Orchestrator LLM):")
            print(retrieved_rules)
            
        except RuntimeError as e:
            print(f"API Error: {e}")