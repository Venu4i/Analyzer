import faiss
import pickle
import numpy as np
import os
from sentence_transformers import SentenceTransformer

# 1. Load the same model used during upload
print("Loading Embedding Model...")
model = SentenceTransformer('all-MiniLM-L6-v2')

def search_index(query, doc_name, k=3):
    # Paths to your saved vector data
    index_path = os.path.join("vector_store", f"{doc_name}.index")
    pkl_path = os.path.join("vector_store", f"{doc_name}.pkl")

    if not os.path.exists(index_path) or not os.path.exists(pkl_path):
        print(f"Error: Index for '{doc_name}' not found in vector_store.")
        return

    # 2. Load FAISS index and Chunk metadata
    index = faiss.read_index(index_path)
    with open(pkl_path, "rb") as f:
        chunks = pickle.load(f)

    # 3. Convert user query into a vector
    print(f"\nSearching for: '{query}'")
    query_vector = model.encode([query]).astype('float32')

    # 4. Perform Search
    # D = Distances, I = Indices of the closest matches
    D, I = index.search(query_vector, k)

    print(f"\n--- Top {k} Matches ---")
    for i, idx in enumerate(I[0]):
        match = chunks[idx]
        score = D[0][i]
        print(f"\n[Match {i+1}] (Distance Score: {score:.4f})")
        print(f"Page: {match['metadata']['page']} | Section: {match['metadata']['section']}")
        print(f"Text snippet: {match['chunk_text'][:200]}...")
        print("-" * 30)

if __name__ == "__main__":
    filename = "Researchpaper1.pdf" 
    
    user_query = input("Enter your question about the paper: ")
    search_index(user_query, filename)