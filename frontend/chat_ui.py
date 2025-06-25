# frontend/chat_ui.py
import streamlit as st
import requests

FLASK_API_URL = "http://127.0.0.1:5000"

def login_user(username, password):
    try:
        res = requests.post(f"{FLASK_API_URL}/api/auth/login", json={"username": username, "password": password})
        res.raise_for_status()
        data = res.json()
        st.session_state.token = data['token']
        st.session_state.role = data['role']
        st.session_state.username = data['username']
        st.session_state.logged_in = True
        st.session_state.messages = [{"role": "assistant", "content": f"ආයුබෝවන් {st.session_state.username}! ඔබගේ `{st.session_state.role}` ගිණුමෙන් මා හා සම්බන්ධ විය හැක."}]
        st.rerun()
    except requests.exceptions.HTTPError as e:
        st.error(f"Login failed: {e.response.json().get('message', 'Unknown error')}")
    except Exception as e:
        st.error(f"An error occurred: {e}")

def logout():
    for key in list(st.session_state.keys()):
        if key not in ['theme']:
            del st.session_state[key]
    st.rerun()

# --- Main App Logic ---

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    # --- Login Form ---
    st.title("HR Agent - Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            login_user(username, password)
else:
    # --- Chat Interface ---
    st.sidebar.title(f"Welcome, {st.session_state.username}")
    st.sidebar.caption(f"Role: {st.session_state.role.capitalize()}")
    st.sidebar.button("Logout", on_click=logout)

    st.title("HR නිවාඩු කළමනාකරණ සහායක 🤖")

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Handle user input
    if prompt := st.chat_input("ඔබගේ ඉල්ලීම මෙහි ටයිප් කරන්න..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Call the backend with the token
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        api_payload = {"message": prompt, "history": st.session_state.messages}
        
        try:
            with st.spinner("..."):
                response = requests.post(f"{FLASK_API_URL}/api/chat", json=api_payload, headers=headers)
                response.raise_for_status()
                assistant_message = response.json().get("response")
                st.session_state.messages.append({"role": "assistant", "content": assistant_message})
                st.rerun()
        except Exception as e:
            st.error(f"Error communicating with the agent: {e}")