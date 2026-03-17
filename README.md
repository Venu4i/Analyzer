# 📑 Analyzer: AI-Powered Research Insight Engine

**Analyzer** is a production-grade RAG (Retrieval-Augmented Generation) system designed specifically for deep-dive analysis of academic research papers. Unlike generic PDF chat apps, **Analyzer** understands document structure—tracking section headers and page numbers to provide precise, grounded citations for every claim it makes.

---

## 🚀 Key Features
* **Structure-Aware Parsing:** Automatically detects sections (Abstract, Methodology, etc.) and preserves page numbers using font-size analysis.
* **Grounded Citations:** Every answer includes exact source tags like `Page 4, Section: Methodology`.
* **Multi-Column Support:** Uses spatial sorting logic to handle complex 2-column IEEE/ACM/arXiv paper layouts accurately.
* **Gemini-Powered Intelligence:** Leverages **Gemini 2.5 Flash** for high-speed, long-context reasoning.
* **Vectorized Search:** Powered by **FAISS** for millisecond retrieval of relevant context.

---

## 🛠 Tech Stack
| Layer | Technology | Role |
| :--- | :--- | :--- |
| **Frontend** | **Streamlit** | Interactive UI & File Uploads |
| **Backend** | **FastAPI** | RESTful API & System Orchestration |
| **Parsing** | **PyMuPDF (fitz)** | Deep PDF layout & font-size analysis |
| **Embeddings** | **HuggingFace** | Local `all-MiniLM-L6-v2` conversion |
| **Vector DB** | **FAISS** | High-performance local L2-distance indexing |
| **LLM** | **Google Gemini 2.5 Flash** | Context-aware reasoning & Answer generation |

---

## 🔄 Workflow

1. **Ingestion:** User uploads a PDF via the Streamlit UI. The backend sanitizes the filename using regex.
2. **Smart Parsing:** `PyMuPDF` parses the document, identifying headers by font weight/size and sorting text blocks by column coordinates.
3. **Vectorization:** `RecursiveCharacterTextSplitter` chunks text (1000 chars, 150 overlap). These are embedded into 384-dimensional vectors via `SentenceTransformer`.
4. **Storage:** Vectors are stored in `.index` files and metadata (text/pages) in `.pkl` files within the `vector_store/` directory.
5. **Semantic Search:** User queries are embedded and compared against the FAISS index using L2 distance to find the Top-3 matches.
6. **Synthesis:** Gemini 2.5 Flash processes the prompt (Context + Query) and generates a cited response.

---

## 💻 Installation & Setup

### 1. Clone the Repository
```bash
git clone [https://github.com/Venu4i/Analyzer.git]
cd analyzer
```

### 2. Setting up virtual environment
# Create the environment
```bash
python -m venv venv/
```

# Activate on Windows
```bash
venv\Scripts\activate
```

# Activate on Mac/Linux
```bash
source venv/bin/activate
```

### 3.Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a .env file in the root directory:
```bash
GEMINI_API_KEY=your_api_key_here
#FASTAPI_URL=http://localhost:8000
PORT=8000
```

### 5. Run the Engine
Start the Backend (Terminal 1):

```bash
uvicorn app.main:app --reload --port 8000
```
### 6.Start the Frontend (Terminal 2):
```bash
cd frontend
python -m streamlit run app.py
```

### 📄 Bonus: Your `requirements.txt` file
Since you are in VS Code, create a file named `requirements.txt` in your root folder and paste this in. These versions are verified to work together without "dependency hell."

```text
# Web Framework
fastapi==0.109.0
uvicorn==0.27.0
python-multipart==0.0.6

# PDF Processing
pymupdf==1.23.8
langchain-text-splitters>=1.1.1

# AI & Vector Database
google-generativeai
sentence-transformers
faiss-cpu==1.7.4
numpy

# Environment & Utilities
python-dotenv==1.0.0
requests==2.31.0

# Frontend
streamlit==1.30.0
```
