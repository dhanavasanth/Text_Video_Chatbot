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

# Configure Gemini API
GEMINI_API_KEY = os.getenv("gemini_api_key")  # Replace with your API key
if not GEMINI_API_KEY:
    st.error("Gemini API key is missing. Please provide it.")
    st.stop()
genai.configure(api_key=GEMINI_API_KEY)

# Check login status
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("Please login to continue")
    st.stop()

# Header and Instructions
st.header(":green[Video Analysis Chatbot]")
st.write("Upload a video, and interact with the AI to analyze it!")
st.write("-----")

# Sidebar for Video Upload
with st.sidebar:
    uploaded_video = st.file_uploader(
        "Upload your video",
        type=["mp4", "mkv","webm","avi","mov"]
    )
    if uploaded_video:
        # Save video to session state
        st.session_state["uploaded_video"] = uploaded_video
        if st.button("Submit"):
            st.toast(f"Video '{uploaded_video.name}' uploaded successfully!")
            st.session_state["video_ready"] = False  # Mark as not processed

# Validate Video Upload
if "uploaded_video" not in st.session_state or not st.session_state["uploaded_video"]:
    st.warning("No video uploaded! Please upload a video and click Submit.")
    st.stop()

# Process Video
video_file = st.session_state["uploaded_video"]

# Save video file temporarily
video_path = f"temp_{video_file.name}"
with open(video_path, "wb") as f:
    f.write(video_file.getbuffer())

# Upload video to Gemini API (if not already processed)
if not st.session_state.get("video_ready", False):
    gemini_video_file = genai.upload_file(video_path)

    # Wait for processing
    while gemini_video_file.state.name == "PROCESSING":
        with st.spinner("Processing video... Please wait."):
            time.sleep(10)
            gemini_video_file = genai.get_file(gemini_video_file.name)

    if gemini_video_file.state.name == "FAILED":
        st.error("Video processing failed. Please try again.")
        st.stop()

    # Mark video as ready for chat interaction
    st.session_state["gemini_video_file"] = gemini_video_file
    st.session_state["video_ready"] = True

#Chat Interaction
if "video_messages" not in st.session_state:
    st.session_state["video_messages"] = [
        {"role": "assistant", "content": "How can I help you analyze this video?"}
    ]

# Display chat messages
for msg in st.session_state["video_messages"]:
    st.chat_message(msg["role"]).write(msg["content"])

# Handle user input
if user_input := st.chat_input("Ask a question about the video (e.g., summarize, create quiz):"):
    # Temporary "thinking" response
    st.session_state["video_messages"].append({"role": "assistant", "content": "Processing your request..."})

    # Generate response using Gemini
    gemini_video_file = st.session_state["gemini_video_file"]


    with st.spinner("The assistant is thinking..."):

        model = genai.GenerativeModel(model_name="gemini-1.5-pro")
        response = model.generate_content(
            [gemini_video_file, user_input],
            request_options={"timeout": 600}
        )

    # Save the conversation
    st.session_state["video_messages"].append({"role": "user", "content": user_input})
    st.session_state["video_messages"].append({"role": "assistant", "content": response.text})

    # Display the assistant's response
    st.chat_message("assistant").write(response.text)

    st.rerun()



