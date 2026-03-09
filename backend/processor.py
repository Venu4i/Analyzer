from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle
import os

# Load a lightweight, high-quality model (runs locally)
model = SentenceTransformer('all-MiniLM-L6-v2')

def create_text_chunks(extracted_data):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=150,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    final_chunks = []
    for item in extracted_data:
        texts = splitter.split_text(item["content"])
        for text in texts:
            final_chunks.append({
                "chunk_text": text.strip(),
                "metadata": item["metadata"]
            })
    return final_chunks

def vectorize_and_save(chunks, index_name="research_index"):
    """
    Converts chunks to vectors and saves a FAISS index + Metadata locally.
    """
    if not chunks:
        return False

    # 1. Extract just the text for embedding
    texts = [c['chunk_text'] for c in chunks]
    
    # 2. Generate Embeddings (Numerical representations)
    embeddings = model.encode(texts)
    embeddings = np.array(embeddings).astype('float32')

    # 3. Create FAISS Index (L2 distance for similarity)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    # 4. Save the Index and the original chunks (Metadata) to disk
    # We save these in a 'vector_store' folder
    os.makedirs("vector_store", exist_ok=True)
    faiss.write_index(index, f"vector_store/{index_name}.index")
    
    with open(f"vector_store/{index_name}.pkl", "wb") as f:
        pickle.dump(chunks, f)

    return True