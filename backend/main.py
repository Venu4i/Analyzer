import os
import shutil
import uvicorn
import re
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from parser import smart_parse_pdf
from processor import create_text_chunks, vectorize_and_save
from engine import get_cited_answer, generate_global_summary

load_dotenv()
app = FastAPI(title="Analyzer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = os.path.abspath("data/uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs("vector_store", exist_ok=True)


from pymongo import MongoClient

# 1. Connect to MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["research_assistant"]
summaries_collection = db["summaries"]

def save_summary(filename, summary_text):
    """Saves or updates the summary in MongoDB."""
    summaries_collection.update_one(
        {"filename": filename},
        {"$set": {"summary": summary_text}},
        upsert=True # Creates it if it doesn't exist, updates if it does
    )

@app.post("/upload")
def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files supported.")

    clean_filename = re.sub(r'[^a-zA-Z0-9.]', '_', file.filename)
    if not clean_filename.endswith(".pdf"): clean_filename += ".pdf"
    file_path = os.path.join(UPLOAD_DIR, clean_filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        raw_data = smart_parse_pdf(file_path)
        final_chunks = create_text_chunks(raw_data)
        vectorize_and_save(final_chunks, index_name=clean_filename)

        # Generate and save the global summary immediately upon upload
        summary_text = generate_global_summary(final_chunks)
        save_summary(clean_filename, summary_text)

        if os.path.exists(file_path): os.remove(file_path)

        return {"filename": clean_filename, "status": "Success"}
        
    except Exception as e:
        if os.path.exists(file_path): os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analyze")
def analyze(query: str, doc_name: str):
    """Handles specific Q&A queries via FAISS."""
    result = get_cited_answer(query, doc_name)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result

@app.get("/get-summary")
def get_summary(doc_name: str):
    """Fetches the pre-computed summary from MongoDB."""
    clean_doc = re.sub(r'[^a-zA-Z0-9.]', '_', doc_name)
    if not clean_doc.endswith(".pdf"): clean_doc += ".pdf"
    
    # Query MongoDB for the document
    db_record = summaries_collection.find_one({"filename": clean_doc})
    
    if db_record and "summary" in db_record:
        return {"summary": db_record["summary"]}
                
    raise HTTPException(status_code=404, detail="Summary not found in Database.")