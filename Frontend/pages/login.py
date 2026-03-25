import streamlit as st
import json
import os

st.set_page_config(page_title="AI Research Assistant", layout="wide")

hide_pages = """
<style>
[data-testid="stSidebarNav"] {
    display: none;
}
</style>
"""
st.markdown(hide_pages, unsafe_allow_html=True)

hide_sidebar = """
<style>
/* Hide entire sidebar */
[data-testid="stSidebar"] {
    display: none;
}

/* Remove the little toggle arrow */
[data-testid="collapsedControl"] {
    display: none;
}
</style>
"""
st.markdown(hide_sidebar, unsafe_allow_html=True)
USER_DB = "users.json"

def load_users():
    if os.path.exists(USER_DB):
        with open(USER_DB, "r") as f:
            return json.load(f)
    return {}

st.title("🔐 Login")

users = load_users()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

username = st.text_input("Username")
password = st.text_input("Password", type="password")


if st.button("Login"):
    if username in users and users[username] == password:
        st.session_state.logged_in = True
        st.session_state.username = username
        
        # Persist login in URL
        st.query_params["auth"] = "true"
        
        st.success("Login successful 🎉")
        st.switch_page("app.py")
    else:
        st.error("Invalid credentials")

st.markdown("---")
st.write("Don't have an account?")

if st.button("Signup here"):
    st.switch_page("pages/signup.py")