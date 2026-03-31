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

st.title("📝 Signup")

# Changed label to Email because FastAPI 'EmailStr' requires email format
new_email = st.text_input("Create Email")
new_pass = st.text_input("Create Password", type="password")

if st.button("Signup"):
    if new_email and new_pass:
        try:
            # Connect to your FastAPI backend
            response = requests.post(
                "http://127.0.0.1:8000/signup",
                json={"email": new_email, "password": new_pass}
            )
            
            if response.status_code == 200:
                st.success("Account created successfully 🎉")
                # Optional: You could automatically log them in here, but we'll stick to your flow
            else:
                # Show exact error from FastAPI (e.g. "Email already registered" or invalid format)
                st.error(response.json().get("detail", "Signup failed"))
                
        except requests.exceptions.ConnectionError:
            st.error("Connection error. Make sure your FastAPI backend is running!")
    else:
        st.warning("Please enter both an email and password.")

st.markdown("---")
st.write("Already have an account?")

if st.button("Login here"):
    st.switch_page("pages/login.py")