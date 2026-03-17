import streamlit as st
import requests
import time

# 1. PAGE SETUP
st.set_page_config(page_title="AI Research Assistant", layout="wide")

# Initialize session state for the document name
if "doc_name" not in st.session_state:
    st.session_state.doc_name = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# 2. SIDEBAR (File Upload)
with st.sidebar:
    st.title("📁 Document Upload")
    uploaded_file = st.file_uploader("Upload a Research Paper (PDF)", type="pdf")

    if uploaded_file and st.button("Process Document"):
        with st.spinner("Uploading and indexing..."):
            # This matches the @app.post("/upload") route
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
            try:
                response = requests.post("http://127.0.0.1:8000/upload", files=files)
                if response.status_code == 200:
                    data = response.json()
                    # Store the filename returned by the backend
                    st.session_state.doc_name = data.get("filename")
                    st.success(f"Indexed {data.get('total_chunks')} chunks!")
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Could not connect to Backend: {e}")

# 3. MAIN CHAT AREA
st.title("🔬 AI Research Assistant")
st.markdown("---")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. CHAT INPUT
if prompt := st.chat_input("Ask a question about the PDF..."):
    # Display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call the Backend /ask route
    if st.session_state.doc_name:
        with st.chat_message("assistant"):
            try:
                # This matches the @app.get("/ask") route
                params = {
                    "query": prompt, 
                    "doc_name": st.session_state.doc_name
                }
                response = requests.get("http://127.0.0.1:8000/ask", params=params)
                
                if response.status_code == 200:
                    answer_data = response.json()
                    matches = answer_data.get("matches", [])
                    
                    # Combine matches into a readable response
                    full_response = "I found these relevant sections:\n\n" + "\n\n---\n\n".join(matches)
                    st.markdown(full_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                else:
                    st.error("Backend failed to find an answer.")
            except Exception as e:
                st.error(f"Connection Error: {e}")
    else:
        st.warning("Please upload and process a PDF in the sidebar first!")
