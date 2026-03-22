import streamlit as st
import json
import os

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
        st.info("Go to Login page 👉")