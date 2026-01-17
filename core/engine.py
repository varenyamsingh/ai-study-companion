import os
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
# Using the updated Chroma package for 2026
from langchain_chroma import Chroma 

def get_vectorstore(pdf_path):
    storage_dir = "./chroma_db"
    
    # 1. Initialize local embeddings (Zero Cost, No API Key needed)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # 2. Check if the database exists to save time/resources
    if os.path.exists(storage_dir) and os.listdir(storage_dir):
        print("📁 Loading existing Knowledge Base from disk...")
        return Chroma(persist_directory=storage_dir, embedding_function=embeddings)

    # 3. If no DB exists, process the PDF
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"❌ Error: {pdf_path} not found in project directory.")

    print(f"🆕 Creating new Knowledge Base from: {pdf_path}")
    
    # Load using PyMuPDF (fast and robust)
    loader = PyMuPDFLoader(pdf_path)
    documents = loader.load()
    
    # Split documents into chunks for better AI context
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    split_docs = splitter.split_documents(documents)
    
    print(f"🧠 Creating local embeddings for {len(split_docs)} chunks...")
    
    # Create the vector database
    vectorstore = Chroma.from_documents(
        documents=split_docs, 
        embedding=embeddings, 
        persist_directory=storage_dir
    )
    
    print("✅ Knowledge Base created successfully!")
    return vectorstore