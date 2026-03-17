import os
import shutil
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.engine import get_cited_answer
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

    safe_filename = file.filename.replace(" ", "_")
    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 1. Parse & Chunk
        raw_data = smart_parse_pdf(file_path)
        final_chunks = create_text_chunks(raw_data)
        
        # 2. Vectorize and save to FAISS
        # We use the filename as the index name so you can have multiple docs
        index_success = vectorize_and_save(final_chunks, index_name=safe_filename)

        # 3. Cleanup PDF
        if os.path.exists(file_path):
            os.remove(file_path)

        return {
            "filename": safe_filename,
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
    """
    New Route: Query the FAISS index with a user question
    """
    try:
        from processor import model # Import model for query embedding
        import faiss
        import pickle

        # 1. Load the specific index and metadata
        index = faiss.read_index(f"vector_store/{doc_name}.index")
        with open(f"vector_store/{doc_name}.pkl", "rb") as f:
            chunks = pickle.load(f) 
            
        # 2. Embed the user's question
        query_vector = model.encode([query]).astype('float32')
        
        # 3. Search for top 3 matches
        D, I = index.search(query_vector, k=3)
        
        results = [chunks[i] for i in I[0]]
        return {"query": query, "matches": results}
    except Exception as e:
        raise HTTPException(status_code=404, detail="Index not found or search failed.")


@app.get("/analyze")
async def analyze(query: str, doc_name: str):
    """
    The endpoint your Streamlit frontend will call.
    Example: /analyze?query=What is the result?&doc_name=faiss_research
    """
    result = get_cited_answer(query, doc_name)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)