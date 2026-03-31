import os
import faiss
import pickle
import re
import numpy as np
from dotenv import load_dotenv
import google.generativeai as genai

# Import your local embedding model
from processor import model 

load_dotenv()

# Gemini setup
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
llm_qa = genai.GenerativeModel("gemini-2.5-flash")     # Best for precise Q&A
llm_sum = genai.GenerativeModel("gemini-2.5-flash")  # Best for massive text chunks

def get_cited_answer(query: str, doc_name: str):
    """The 'Sniper': Uses FAISS to find exact chunks for Q&A."""
    try:
        clean_doc = re.sub(r'[^a-zA-Z0-9.]', '_', doc_name)
        if not clean_doc.endswith(".pdf"):
            clean_doc += ".pdf"

        index_path = f"vector_store/{clean_doc}.index"
        pkl_path = f"vector_store/{clean_doc}.pkl"

        if not os.path.exists(index_path) or not os.path.exists(pkl_path):
            return {"error": f"Files not found: {clean_doc}"}

        # Load FAISS & chunks
        index = faiss.read_index(index_path)
        with open(pkl_path, "rb") as f:
            chunks = pickle.load(f)

        # Vector Search
        query_vector = model.encode([query]).astype('float32')
        D, I = index.search(query_vector, k=3) # Top 3 chunks

        results = [chunks[i] for i in I[0] if i < len(chunks)]
        if not results:
            return {"error": "No relevant results found"}

        # Build context
        context = "\n\n".join([r["chunk_text"] for r in results])

        prompt = f"""
        You are an expert academic research assistant.
        Answer the question based ONLY on the context below. 
        If the answer is not in the context, say "I cannot find the answer in the provided text."
        
        Context:
        {context}

        Question:
        {query}
        """

        response = llm_qa.generate_content(prompt)

        citations = [
            {
                "text": r["chunk_text"],
                "page": r.get("metadata", {}).get("page", "N/A"),
                "section": r.get("metadata", {}).get("section", "N/A")
            } for r in results
        ]

        return {
            "answer": response.text,
            "citations": citations
        }

    except Exception as e:
        print(f"Engine Q&A Error: {str(e)}")
        return {"error": f"Failed to generate answer: {str(e)}"}

def generate_global_summary(chunks: list):
    """The 'Shotgun': Bypasses FAISS to summarize the entire paper at once."""
    try:
        # Stitch all text together (Limit to ~150k chars for safety)
        full_text = "\n".join([c['chunk_text'] for c in chunks])[:150000]

        prompt = f"""
        You are an expert research reviewer. 
        Provide a professional, highly detailed summary of the following research paper.
        Use Markdown formatting. Structure it with:
        - **Main Objective**
        - **Key Methodology**
        - **Significant Findings**
        - **Conclusion**
        
        PAPER TEXT:
        {full_text}
        """

        response = llm_sum.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Global Summary Error: {str(e)}")
        return "Summary generation failed."