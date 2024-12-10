import streamlit as st
import time

st.set_page_config(page_title="Chat", page_icon=":material/home:", layout="wide")


st.logo("Assets/dummy_logo.png")

hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Hide default Streamlit components
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Initialize session state variables
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# Logout function
def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()

# Login form
def login_form():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "user1234":
            st.success("Logged in successfully!")
            st.session_state.logged_in = True
            st.session_state.username = username
            st.rerun()  # Reload the page to update UI
        else:
            st.error("Invalid username or password")

# Main page logic
if st.session_state.logged_in:
    # Sidebar: Profile and Logout
    with st.sidebar:
        col1, col2 = st.columns(2)
        with col1:
            st.image("Assets/userprofile.png",width=80)
        with col2:
            if st.button("Logout", key="logout", help="Click to log out", type="primary"):
                logout()

    # Main content
    st.header(f"Welcome, :blue[{st.session_state.username}]...!")
    
else:
    login_form()
