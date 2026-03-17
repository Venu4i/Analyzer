import os
import faiss
import pickle
import re
import numpy as np
from processor import model  # reuse same embedding model
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# Gemini setup
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
llm = genai.GenerativeModel("gemini-2.5-flash")  # stable + fast

def get_cited_answer(query: str, doc_name: str):
    try:
        # 1. Clean filename
        clean_doc = re.sub(r'[^a-zA-Z0-9.]', '_', doc_name)
        if not clean_doc.endswith(".pdf"):
            clean_doc += ".pdf"

        index_path = f"vector_store/{clean_doc}.index"
        pkl_path = f"vector_store/{clean_doc}.pkl"

        if not os.path.exists(index_path) or not os.path.exists(pkl_path):
            return {"error": f"Files not found: {clean_doc}"}

        # 2. Load FAISS + chunks
        index = faiss.read_index(index_path)
        with open(pkl_path, "rb") as f:
            chunks = pickle.load(f)

        # 3. Embed query
        query_vector = model.encode([query]).astype('float32')

        # 4. Search
        D, I = index.search(query_vector, k=3)

        results = [chunks[i] for i in I[0] if i < len(chunks)]

        if not results:
            return {"error": "No relevant results found"}

        # 5. Build context
        context = "\n\n".join([r["chunk_text"][:500] for r in results])

        # 6. Prompt for Gemini
        prompt = f"""
You are a research assistant.

Answer the question based ONLY on the context below.

Context:
{context}

Question:
{query}

Give a clear and concise answer.
"""

        response = llm.generate_content(prompt)

        # 7. Format citations
        citations = []
        for r in results:
            citations.append({
                "text": r["chunk_text"],
                "page": r["metadata"].get("page", "N/A"),
                "section": r["metadata"].get("section", "N/A")
            })

        return {
            "answer": response.text,
            "citations": citations
        }

    except Exception as e:
        print(f"Engine Error: {str(e)}")
        return {"error": str(e)}