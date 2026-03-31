import streamlit as st
import requests

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

st.title("🔐 Login")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Changed label to Email because FastAPI 'EmailStr' requires email format
email = st.text_input("Email")
password = st.text_input("Password", type="password")

if st.button("Login"):
    if email and password:
        try:
            # Connect to your FastAPI backend
            response = requests.post(
                "http://127.0.0.1:8000/login",
                json={"email": email, "password": password}
            )
            
            if response.status_code == 200:
                data = response.json()
                st.session_state.logged_in = True
                # Store the MongoDB user_id in session state to use later for uploads
                st.session_state.user_id = data.get("user_id") 
                st.session_state.email = email
                
                # Persist login in URL
                st.query_params["auth"] = "true"
                
                st.success("Login successful 🎉")
                st.switch_page("app.py")
            else:
                # Show the exact error from FastAPI (e.g. "Invalid credentials")
                st.error(response.json().get("detail", "Login failed"))
                
        except requests.exceptions.ConnectionError:
            st.error("Connection error. Make sure your FastAPI backend is running!")
    else:
        st.warning("Please enter both email and password.")

st.markdown("---")
st.write("Don't have an account?")

if st.button("Signup here"):
    st.switch_page("pages/signup.py")