import os
import shutil
import uvicorn
import re  # Added for filename cleaning
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from engine import get_cited_answer
from dotenv import load_dotenv

from parser import smart_parse_pdf
from processor import create_text_chunks, vectorize_and_save

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

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    # 1. Clean filename
    clean_filename = re.sub(r'[^a-zA-Z0-9.]', '_', file.filename)
    
    # Ensure .pdf is at the end (logic for safety)
    if not clean_filename.endswith(".pdf"):
        clean_filename += ".pdf"

    file_path = os.path.join(UPLOAD_DIR, clean_filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        raw_data = smart_parse_pdf(file_path)
        final_chunks = create_text_chunks(raw_data)
        
        index_success = vectorize_and_save(final_chunks, index_name=clean_filename)

        if os.path.exists(file_path):
            os.remove(file_path)

        return {
            "filename": clean_filename,
            "status": "Success",
            "vectorized": index_success,
            "total_chunks": len(final_chunks)
        }
        
    except Exception as e:
        if os.path.exists(file_path): os.remove(file_path)
        print(f"Server Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ask")
async def ask_question(query: str, doc_name: str):
    try:
        from processor import model 
        import faiss
        import pickle

        # 1. Clean name and ensure .pdf is present
        clean_doc = re.sub(r'[^a-zA-Z0-9.]', '_', doc_name)
        if not clean_doc.endswith(".pdf"):
            clean_doc += ".pdf"
        
        index_path = f"vector_store/{clean_doc}.index"
        pkl_path = f"vector_store/{clean_doc}.pkl"

        if not os.path.exists(index_path):
            raise FileNotFoundError(f"Could not find index file: {index_path}")

        index = faiss.read_index(index_path)
        with open(pkl_path, "rb") as f:
            chunks = pickle.load(f) 
            
        query_vector = model.encode([query]).astype('float32')
        D, I = index.search(query_vector, k=3)
        results = [chunks[i] for i in I[0]]
        
        return {"query": query, "matches": results}
    except Exception as e:
        print(f"Ask Error: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/analyze")
async def analyze(query: str, doc_name: str):
    try:
        result = get_cited_answer(query, doc_name)

        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])

        return result

    except Exception as e:
        print(f"Analyze Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)