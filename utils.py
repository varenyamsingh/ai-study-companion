import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()

def process_pdf_to_vectorstore(pdf_path, storage_directory="./study_db"):
    """
    Takes a PDF path, splits the text, and saves it into a local ChromaDB.
    """
    
    # STEP 1: Load the PDF
    # PyPDFLoader reads the file and creates a list of 'Document' objects (one per page)
    print(f"📄 Loading PDF: {pdf_path}...")
    loader = PyPDFLoader(pdf_path)
    raw_documents = loader.load()

    # STEP 2: Split the text into chunks
    # We use 'Recursive' splitting because it tries to keep paragraphs and sentences together.
    # chunk_size: 1000 characters is a good balance for Gemini.
    # chunk_overlap: 200 chars ensures that if a concept is split, both chunks have part of it.
    print(" Splitting text into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True # Helps us track exactly where the info came from
    )
    docs = text_splitter.split_documents(raw_documents)

    # STEP 3: Create Embeddings using Gemini
    # This turns your text into mathematical vectors.
    print("🧠 Generating Gemini embeddings and saving to database...")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

    # STEP 4: Store in ChromaDB
    # This creates a folder on your computer (study_db) to keep the data forever.
    vectorstore = Chroma.from_documents(
        documents=docs, 
        embedding=embeddings,
        persist_directory=storage_directory
    )
    
    print(f"✅ Success! Knowledge base saved at {storage_directory}")
    return vectorstore