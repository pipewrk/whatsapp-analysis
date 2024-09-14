import tiktoken
from pathlib import Path
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from WAAnalysis.config import MD_DIR

# -------------------------------
# Tokenizer and Embedding Model
# -------------------------------

# Initialize tokenizer (use appropriate encoding)
tokenizer = tiktoken.get_encoding("cl100k_base")

# Define the chunk size and overlap based on your analysis
CHUNK_SIZE = 642
CHUNK_OVERLAP = 321

# Ollama server details
OLLAMA_SERVER_URL = "http://localhost:11434/"

# -------------------------------
# Chunking and FAISS Setup
# -------------------------------

def process_and_store_embeddings(md_dir, faiss_index_path):
    """Processes markdown files, computes embeddings, and stores them in a FAISS index."""
    
    # Load markdown files from MD_DIR
    loader = DirectoryLoader(md_dir, glob="*.md")
    documents = loader.load()

    # Initialize text splitter with the chunk size and overlap
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )

    # Split the documents into chunks 
    chunked_docs = text_splitter.split_documents(documents)

    # Initialize Ollama embedding model
    embedding_model = OllamaEmbeddings(model="nomic-embed-text:latest")
    
    # Create FAISS index and store the chunk embeddings
    vectorstore = FAISS.from_documents(chunked_docs, embedding_model)

    # Save the FAISS index locally
    faiss_index_file = Path(faiss_index_path)
    vectorstore.save_local(faiss_index_file.stem)
    print(f"FAISS index saved to {faiss_index_file.stem}")

# -------------------------------
# Main Execution
# -------------------------------

if __name__ == "__main__":
    # Path to store the FAISS index
    FAISS_INDEX_PATH = "./faiss_index"

    # Run the ingestion pipeline
    process_and_store_embeddings(MD_DIR, FAISS_INDEX_PATH)
