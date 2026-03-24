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


def save_users(users):
    with open(USER_DB, "w") as f:
        json.dump(users, f)


st.title("📝 Signup")

users = load_users()

new_user = st.text_input("Create Username")
new_pass = st.text_input("Create Password", type="password")

if st.button("Signup"):
    if new_user in users:
        st.error("User already exists")
    else:
        users[new_user] = new_pass
        save_users(users)
        st.success("Account created successfully 🎉")
        st.switch_page("pages/login.py")

st.markdown("---")
st.write("Already have an account?")

if st.button("Login here"):
    st.switch_page("pages/login.py")
