📑 PDF Analyzer: Multi-Tenant AI Research Assistant
PDF Analyzer is a production-grade, full-stack RAG (Retrieval-Augmented Generation) system engineered for deep-dive analysis of academic research papers. Upgraded from a standard vector-search app into a multi-tenant SaaS architecture, it features a novel Dual-Pipeline RAG design to solve the standard limitations of document chat: providing both instant holistic summaries and highly precise, cited answers in isolated user workspaces.

🚀 Key Features
🔐 Secure Multi-Tenancy: Built-in Authentication (Signup/Login) backed by MongoDB. Every user gets a completely isolated vector workspace and summary database.

⚡ Dual-Pipeline Architecture: * The "Shotgun" (Global Summary): Processes the entire document upon upload to generate and cache a comprehensive overview instantly.

The "Sniper" (Vector Q&A): Uses FAISS to pull highly specific, chunked contexts for accurate, cited Q&A.

🧠 Gemini 2.5 Intelligence: Leverages Gemini 2.5 Flash for blazing-fast massive document synthesis and Gemini 2.5 Pro for complex, context-aware reasoning.

🔄 Persistent Sessions: Custom Streamlit URL-parameter state management ensures users stay logged in and maintain their workspace even after hard browser refreshes.

🎯 Grounded Citations: Every specific answer includes exact source tags referencing the exact page and chunk of text used to prevent hallucinations.

🛠 Tech Stack
Layer	Technology	Role
Frontend	Streamlit	Interactive UI, Session Persistence & File Uploads
Backend	FastAPI	RESTful API, Auth routing, & System Orchestration
Database	MongoDB	Source of truth for User Credentials & Global Summaries
Parsing	PyMuPDF (fitz)	Deep PDF layout & text extraction
Embeddings	Sentence-Transformers	Local all-MiniLM-L6-v2 vectorization
Vector DB	FAISS	High-performance local indexing (Isolated per user)
LLMs	Gemini 2.5 Pro & Flash	Context reasoning (Pro) & Full Document Synthesis (Flash)
🔄 The Dual-Pipeline Workflow
Authentication: User signs up/logs in via Streamlit. FastAPI verifies credentials against MongoDB and issues a persistent user_id.

Ingestion & Routing: User uploads a PDF. The backend sanitizes the file and routes it to an isolated vector_store/{user_id}/ directory.

Smart Parsing: PyMuPDF extracts text, which is split into optimal chunks via RecursiveCharacterTextSplitter.

The Split Pipeline:

Path A (Summary): The entire text array is sent to Gemini 2.5 Flash to generate a massive global summary, which is instantly saved to MongoDB linked to the user_id.

Path B (Vectors): Text chunks are embedded into 384-dimensional vectors using sentence-transformers and saved to the user's localized FAISS index.

Interactive Analysis: * User can click "Fetch Summary" to instantly read the cached overview from MongoDB (Zero wait time).

User can ask specific questions in chat: Queries are embedded, matched in FAISS, and answered by Gemini 2.5 Pro with exact citations.

💻 Installation & Setup
1. Clone the Repository
Bash
git clone https://github.com/your-username/pdf-analyzer.git
cd pdf-analyzer
2. Set up the Virtual Environment
Create the environment:

Bash
python -m venv venv
Activate on Windows:

Bash
venv\Scripts\activate
Activate on Mac/Linux:

Bash
source venv/bin/activate
3. Install Dependencies
Bash
pip install -r requirements.txt
4. Configure Environment Variables
Create a .env file in the root directory. You will need a Google Gemini API key and a MongoDB connection string (Local or Atlas).

Code snippet
GOOGLE_API_KEY=your_gemini_api_key_here
MONGO_URI=mongodb://localhost:27017/  # Or your MongoDB Atlas SRV string
PORT=8000
5. Run the Application (Requires Two Terminals)
Terminal 1: Start the Backend (FastAPI)

Bash
python -m uvicorn main:app --reload --port 8000
Terminal 2: Start the Frontend (Streamlit)

Bash
python -m streamlit run app.py
📦 Requirements (requirements.txt)
Ensure your requirements.txt includes the following verified versions to avoid dependency conflicts:

Plaintext
# Web Framework
fastapi
uvicorn
python-multipart

# Database
pymongo

# PDF Processing & Chunking
pymupdf
langchain-text-splitters

# AI & Vector Database
google-generativeai
sentence-transformers
faiss-cpu
numpy

# Environment & Utilities
python-dotenv
requests
pydantic[email]

# Frontend
streamlit