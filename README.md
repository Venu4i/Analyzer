# 📑 Analyzer: AI-Powered Research Insight Engine

**Analyzer** is a production-grade RAG (Retrieval-Augmented Generation) system designed specifically for deep-dive analysis of academic research papers. Unlike generic PDF chat apps, **Analyzer** understands document structure—tracking section headers and page numbers to provide precise, grounded citations for every claim it makes.

---



## 🚀 Key Features
* **Structure-Aware Parsing:** Automatically detects sections (Abstract, Methodology, Results, etc.) and preserves page numbers.
* **Grounded Citations:** Every answer includes exact source tags like `(Page 4, Section: Methodology)`.
* **Multi-Column Support:** Uses spatial sorting to handle complex 2-column IEEE/arXiv paper layouts.
* **Asynchronous Processing:** Fast API backend built for high-performance ingestion.
* **Vectorized Search:** Powered by **FAISS** for millisecond retrieval of relevant context.

---

## 🛠 Tech Stack
| Layer | Technology | Role |
| :--- | :--- | :--- |
| **Frontend** | **Streamlit** | Interactive UI & File Uploads |
| **Backend** | **FastAPI** | RESTful API & Orchestration |
| **Parsing** | **PyMuPDF (fitz)** | Deep PDF layout analysis |
| **Orchestration** | **LangChain** | RAG pipeline & Prompt management |
| **Vector DB** | **FAISS** | High-performance local vector indexing |
| **Embeddings** | **OpenAI / HuggingFace** | Text-to-Vector conversion |
| **LLM** | **GPT-4o / Claude 3.5** | Context-aware reasoning & Answer generation |

---

## 🔄 Workflow

1.  **Ingestion:** User uploads a PDF via the Streamlit UI.
2.  **Extraction:** The FastAPI backend parses the PDF, identifies headers, and chunks text while maintaining metadata (Page/Section).
3.  **Vectorization:** Each chunk is converted into an embedding and stored in a local FAISS index.
4.  **Query:** User asks a question. The query is embedded and compared against the FAISS index to find the Top-K chunks.
5.  **Synthesis:** The LLM receives the question + chunks + metadata and generates a cited answer.



---

## 💻 Installation & Setup

### 1. Clone the Repository
```bash
git clone [https://github.com/your-username/analyzer.git](https://github.com/your-username/analyzer.git)
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
OPENAI_API_KEY=your_api_key_here
FASTAPI_URL=http://localhost:8000
```

### 5. Run the Engine
Start the Backend (Terminal 1):

```bash
uvicorn app.main:app --reload --port 8000
```
### 6.Start the Frontend (Terminal 2):
```bash
streamlit run frontend/app.py
```

### 📄 Bonus: Your `requirements.txt` file
Since you are in VS Code, create a file named `requirements.txt` in your root folder and paste this in. These versions are verified to work together without "dependency hell."

```text
fastapi==0.109.0
uvicorn==0.27.0
python-multipart==0.0.6
pymupdf==1.23.8
pydantic==2.5.3
python-dotenv==1.0.0
langchain==0.1.0
langchain-community==0.0.10
langchain-openai==0.0.2
faiss-cpu==1.7.4
streamlit==1.30.0
requests==2.31.0
```
