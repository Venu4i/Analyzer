import os
from backend.parser import smart_parse_pdf
from backend.processor import ingest_to_vector_store

# 1. Parse
data = smart_parse_pdf("sample_paper.pdf")
# 2. Embed
status = ingest_to_vector_store(data)
print(status)

# 3. Check if files exist
if os.path.exists("data/index/faiss_research/index.faiss"):
    print("✅ FAISS Index files found on disk!")