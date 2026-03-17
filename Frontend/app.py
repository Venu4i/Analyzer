import streamlit as st
import requests

# 1. PAGE SETUP
st.set_page_config(page_title="AI Research Assistant", layout="wide")

if "doc_name" not in st.session_state:
    st.session_state.doc_name = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# 2. SIDEBAR (File Upload)
with st.sidebar:
    st.title("📁 Document Upload")
    uploaded_file = st.file_uploader("Upload a Research Paper (PDF)", type="pdf")

    if uploaded_file and st.button("Process Document"):
        with st.spinner("Indexing your paper..."):
            # Sends file to the Backend /upload
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
            try:
                response = requests.post("http://127.0.0.1:8000/upload", files=files)
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.doc_name = data.get("filename")
                    st.success(f"Successfully indexed: {st.session_state.doc_name}")
                else:
                    st.error(f"Upload Failed: {response.text}")
            except Exception as e:
                st.error(f"Connection Error: {e}")

# 3. MAIN CHAT AREA
st.title("🔬 AI Research Assistant")
st.markdown("---")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. CHAT INPUT (Connects to YOUR LlamaIndex Engine)
if prompt := st.chat_input("Ask a question about the PDF..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if st.session_state.doc_name:
        with st.chat_message("assistant"):
            with st.spinner("Gemini is analyzing..."):
                try:
                    # CRITICAL CHANGE: We now call /analyze (Your Engine)
                    params = {
                        "query": prompt, 
                        "doc_name": st.session_state.doc_name
                    }
                    response = requests.get("http://127.0.0.1:8000/analyze", params=params)
                    
                    if response.status_code == 200:
                        data = response.json()
                        answer = data.get("answer")
                        citations = data.get("citations", [])
                        
                        # Display the AI's smart answer
                        st.markdown(answer)
                        
                        # Professional Citation Dropdown
                        if citations:
                            with st.expander("📚 View Sources & Citations"):
                                for i, cite in enumerate(citations):
                                    st.write(f"**[{i+1}] Page {cite['page']} - Section: {cite['section']}**")
                                    st.caption(cite['text'][:300] + "...")
                        
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                    else:
                        st.error("Engine failed to generate a response.")
                except Exception as e:
                    st.error(f"Connection Error: {e}")
    else:
        st.warning("Please upload a PDF in the sidebar first!")