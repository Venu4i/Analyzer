import os
import faiss
import pickle
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import StorageContext, VectorStoreIndex, ServiceContext
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.core.query_engine import CitationQueryEngine
from dotenv import load_dotenv

load_dotenv()

# Get the API key from environment
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in .env file!")

# Initialize the LLM with the explicit key
llm = GoogleGenAI(model="models/gemini-2.5-pro", api_key=api_key)
embed_model = HuggingFaceEmbedding(model_name="all-MiniLM-L6-v2")

def get_cited_answer(query: str, doc_name: str):
    """
    Loads the FAISS index created by your teammates and 
    uses Gemini to generate an answer with citations.
    """
    # Define paths based on your teammates' folder structure
    index_path = f"data/index/{doc_name}/index.faiss"
    pkl_path = f"data/index/{doc_name}/index.pkl"

    if not os.path.exists(index_path):
        return {"error": "Index not found. Please upload and process the PDF first."}

    # 2. Load the LangChain-style FAISS index into LlamaIndex
    faiss_index = faiss.read_index(index_path)
    vector_store = FaissVectorStore(faiss_index=faiss_index)
    
    # Create storage context
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    # 3. Create the Index object
    # We pass the embed_model so LlamaIndex knows how to vectorize your query
    index = VectorStoreIndex.from_vector_store(
        vector_store, 
        storage_context=storage_context,
        embed_model=embed_model
    )

    # 4. The Citation Engine (Your Key Feature)
    query_engine = CitationQueryEngine.from_args(
        index,
        llm=llm,
        similarity_top_k=3,
        citation_chunk_size=512, 
    )

    response = query_engine.query(query)
    
    # Return structured data for the UI
    return {
        "answer": str(response),
        "sources": [
            {
                "text": node.node.get_content(),
                "page": node.node.metadata.get("page", "N/A"),
                "section": node.node.metadata.get("section", "N/A")
            } for node in response.source_nodes
        ]
    }