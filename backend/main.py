import os
import shutil
import uvicorn
import re
import faiss
import pickle
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv

# Existing project imports
from engine import get_cited_answer
from parser import smart_parse_pdf
from engine import get_cited_answer, generate_global_summary
from processor import create_text_chunks, vectorize_and_save, model

load_dotenv()
app = FastAPI(title="Analyzer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories
UPLOAD_DIR = os.path.abspath("data/uploads")
VECTOR_STORE_DIR = os.path.abspath("vector_store")
os.makedirs(UPLOAD_DIR, exist_ok=True)

from pymongo import MongoClient

# 1. Connect to MongoDB
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["Analyzer"]
summaries_collection = db["summaries"]
users_collection = db["users"]

def save_summary(filename: str, summary_text: str, user_id: str):
    """Saves the summary in MongoDB linked to the specific user."""
    summaries_collection.update_one(
        {"filename": filename, "user_id": user_id}, 
        {"$set": {"summary": summary_text}},
        upsert=True 
    )

# --- SCHEMAS ---
class UserAuth(BaseModel):
    email: EmailStr
    password: str

# --- AUTH CONTROLLERS ---

@app.post("/signup")
def signup(user: UserAuth):
    user_exists = users_collection.find_one({"email": user.email})
    if user_exists:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Store user (Recommended: Hash password in production)
    result =  users_collection.insert_one(user.dict())
    return {"status": "Success", "user_id": str(result.inserted_id)}

@app.post("/login")
def login(user: UserAuth):
    db_user =  users_collection.find_one({"email": user.email, "password": user.password})
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return {"status": "Success", "user_id": str(db_user["_id"])}

@app.post("/logout")
def logout(user_id: str):
    return {"status": "Success", "message": f"User {user_id} logged out locally."}

# --- FILE & VECTOR CONTROLLERS ---

@app.post("/upload")
def upload_pdf(user_id: str, file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files supported.")

    clean_filename = re.sub(r'[^a-zA-Z0-9.]', '_', file.filename)
    if not clean_filename.endswith(".pdf"):
        clean_filename += ".pdf"

    # Create user-specific vector path
    user_path = os.path.join(VECTOR_STORE_DIR, user_id)
    os.makedirs(user_path, exist_ok=True)
    
    file_path = os.path.join(UPLOAD_DIR, f"{user_id}_{clean_filename}")
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        raw_data = smart_parse_pdf(file_path)
        final_chunks = create_text_chunks(raw_data)
        
        # Save index into vector_store/{user_id}/{filename}
        index_success = vectorize_and_save(final_chunks, index_name=f"{user_id}/{clean_filename}")

        # Generate and save the global summary immediately upon upload
        summary_text = generate_global_summary(final_chunks)
        
        # --- FIX 1: ADDED user_id TO THE FUNCTION CALL HERE ---
        save_summary(clean_filename, summary_text, user_id)
        
        return {
            "filename": clean_filename,
            "status": "Success",
            "vectorized": index_success,
            "user_id": user_id
        }
        
    except Exception as e:
        if os.path.exists(file_path): os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Upload Error: {str(e)}")

@app.get("/ask")
def ask_question(query: str, doc_name: str, user_id: str):
    try:
        clean_doc = re.sub(r'[^a-zA-Z0-9.]', '_', doc_name)
        if not clean_doc.endswith(".pdf"):
            clean_doc += ".pdf"
        
        # Look inside user-specific folder
        index_path = os.path.join(VECTOR_STORE_DIR, user_id, f"{clean_doc}.index")
        pkl_path = os.path.join(VECTOR_STORE_DIR, user_id, f"{clean_doc}.pkl")

        if not os.path.exists(index_path):
            raise HTTPException(status_code=404, detail="Index not found for this user.")

        index = faiss.read_index(index_path)
        with open(pkl_path, "rb") as f:
            chunks = pickle.load(f) 
            
        query_vector = model.encode([query]).astype('float32')
        D, I = index.search(query_vector, k=3)
        results = [chunks[i] for i in I[0]]
        
        return {"query": query, "matches": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/delete-file")
def delete_file(user_id: str, doc_name: str):
    try:
        clean_doc = re.sub(r'[^a-zA-Z0-9.]', '_', doc_name)
        if not clean_doc.endswith(".pdf"):
            clean_doc += ".pdf"
            
        index_path = os.path.join(VECTOR_STORE_DIR, user_id, f"{clean_doc}.index")
        pkl_path = os.path.join(VECTOR_STORE_DIR, user_id, f"{clean_doc}.pkl")

        deleted = False
        for p in [index_path, pkl_path]:
            if os.path.exists(p):
                os.remove(p)
                deleted = True
        
        if not deleted:
            raise HTTPException(status_code=404, detail="File not found in vector space.")

        return {"status": "Success", "message": f"Deleted {doc_name} for user {user_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analyze")
def analyze(query: str, doc_name: str, user_id: str):
    try:
        result = get_cited_answer(query, doc_name, user_id=user_id)
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- FIX 2: MOVED THIS ROUTE ABOVE THE MAIN BLOCK ---
@app.get("/get-summary")
def get_summary(doc_name: str, user_id: str):
    clean_doc = re.sub(r'[^a-zA-Z0-9.]', '_', doc_name)
    if not clean_doc.endswith(".pdf"): clean_doc += ".pdf"
    
    # Fetch from Mongo using BOTH filename and user_id
    db_record = summaries_collection.find_one({"filename": clean_doc, "user_id": user_id})
    
    if db_record and "summary" in db_record:
        return {"summary": db_record["summary"]}
                
    raise HTTPException(status_code=404, detail="Summary not found in Database.")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)