import streamlit as st
import google.generativeai as genai
import time
from Home import *
from dotenv import load_dotenv
import os

load_dotenv()  # take environment variables from .env.

st.logo("Assets/dummy_logo.png")

hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

import streamlit as st

# Check login status
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("Please login to continue")
    st.stop()

if "logged_in" in st.session_state or st.session_state.logged_in:
    st.header(":green[Chat] with you document's")
    st.write("Upload your document(s) and ask questions about them.")
    st.write("-----")

#on side bar upload

with st.sidebar:
    user_files = st.file_uploader(
    "Upload your PDF documents",
    type=["pdf"],
    accept_multiple_files=True
    )
    if user_files:
        # Save the files in session state
        st.session_state["uploaded_files"] = user_files
        if st.button("Submit"):
            st.toast(f"{len(user_files)} document(s) uploaded successfully!")


# Validate file upload
if "uploaded_files" not in st.session_state or not st.session_state["uploaded_files"]:
    st.warning("No files uploaded! Please upload some files.")
    st.stop()

# Get the uploaded files
uploaded_files = st.session_state["uploaded_files"]
uploaded_file_paths = []

# Save files temporarily and collect paths
for file in uploaded_files:
    temp_path = f"temp_{file.name}"
    with open(temp_path, "wb") as f:
        f.write(file.getbuffer())
    uploaded_file_paths.append(temp_path)

# Initialize chat messages
if "doc_messages" not in st.session_state:
    st.session_state["doc_messages"] = [{"role": "assistant", "content": "How can I help you?"}]

# Display chat messages
for msg in st.session_state["doc_messages"]:
    st.chat_message(msg["role"]).write(msg["content"])

# Handle user input
if prompt := st.chat_input("Ask your question about the document(s):"):
    # Ensure API key exists
    api_key = os.getenv("gemini_api_key") 
    if not api_key:
        st.info("Please provide your Gemini API key.")
        st.stop()

    # Show the "thinking" spinner
    with st.spinner("The assistant is thinking..."):
        # Configure API and load model
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")

        # Upload PDFs to the Gemini API
        uploaded_samples = [genai.upload_file(path) for path in uploaded_file_paths]

        # Generate a response using the PDF context
        response = model.generate_content([prompt] + uploaded_samples)

    # Save the conversation
    st.session_state["doc_messages"].append({"role": "user", "content": prompt})
    st.session_state["doc_messages"].append({"role": "assistant", "content": response.text})

    # Display the assistant's response
    st.chat_message("assistant").write(response.text)

    st.rerun()
