import streamlit as st
import requests

# 1. PAGE SETUP
st.set_page_config(page_title="AI Research Assistant", layout="wide")

hide_pages = """
<style>
[data-testid="stSidebarNav"] { display: none; }
</style>
"""
st.markdown(hide_pages, unsafe_allow_html=True)

if "user_id" not in st.session_state:
    st.session_state.user_id = None 
if "doc_name" not in st.session_state: st.session_state.doc_name = None
if "messages" not in st.session_state: st.session_state.messages = []

# 2. SIDEBAR (File Upload & Global Summary)
with st.sidebar:
    st.title("📁 Document Upload")
    uploaded_file = st.file_uploader("Upload a Research Paper (PDF)", type="pdf")

    if uploaded_file and st.button("Process Document"):
        with st.spinner("Indexing and Generating Summary... This takes ~15 seconds."):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
            
            # --- THE FIX IS HERE ---
            # We attach the user_id from the login session to the request parameters
            params = {"user_id": st.session_state.user_id} 
            print(f"DEBUG: Uploading with params: {params} and file: {uploaded_file.name}")
            
            try:
                # Add params=params to the post request!
                response = requests.post("http://127.0.0.1:8000/upload", params=params, files=files)
                
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.doc_name = data.get("filename")
                    st.session_state.messages = [] # Clear old chat on new upload
                    st.success(f"Successfully indexed: {st.session_state.doc_name}")
                else:
                    st.error(f"Upload Failed: {response.text}")
            except Exception as e:
                st.error(f"Connection Error: {e}")
    st.markdown("---")
    
    # NEW: Dedicated button for fetching the pre-computed summary
    if st.session_state.doc_name:
        if st.button("📝 Fetch Full Paper Summary"):
            with st.spinner("Retrieving summary..."):
                try:
                    params = {"user_id": st.session_state.user_id}
                    res = requests.get(f"http://127.0.0.1:8000/get-summary?doc_name={st.session_state.doc_name}", params = params)
                    if res.status_code == 200:
                        summary_text = res.json().get("summary")
                        # Add summary to chat history as an assistant message
                        st.session_state.messages.append({"role": "assistant", "content": f"**Full Paper Summary:**\n\n{summary_text}"})
                        st.rerun()
                    else:
                        st.error("Summary not found. Please re-upload.")
                except Exception as e:
                    st.error(f"Error fetching summary: {e}")
                    
    st.markdown("---")
    if st.button("Logout"):
        st.query_params.clear()
        st.session_state.clear()
        st.switch_page("pages/login.py")
# 3. MAIN CHAT AREA
st.title("🔬 AI Research Assistant")
st.markdown("---")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. CHAT INPUT (Specific Q&A)
if prompt := st.chat_input("Ask a specific question about the PDF..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if st.session_state.doc_name:
        with st.chat_message("assistant"):
            with st.spinner("Gemini is analyzing specific sections..."):
                try:
                    params = {"query": prompt, "doc_name": st.session_state.doc_name, "user_id": st.session_state.user_id}
                    response = requests.get("http://127.0.0.1:8000/analyze", params=params)
                    
                    if response.status_code == 200:
                        data = response.json()
                        answer = data.get("answer")
                        citations = data.get("citations", [])
                        
                        st.markdown(answer)
                        
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