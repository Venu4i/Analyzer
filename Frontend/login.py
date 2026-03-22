import streamlit as st
import json
import os

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
        st.success("Login successful 🎉")
        st.switch_page("app.py")  # redirect to home
    else:
        st.error("Invalid credentials")