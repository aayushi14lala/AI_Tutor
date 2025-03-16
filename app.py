# Built-in modules
import os
import time

# Third-party modules
import streamlit as st
from PIL import Image
from openai import OpenAI

# Local modules
import api_handler
from api_handler import send_query_get_response
from chat_gen import generate_html
from file_upload import check_and_upload_files

# Load Logos
logo = Image.open('logo.png')

# Layout Header
c1, c2 = st.columns([0.9, 3.2])
with c1:
    st.image(logo, width=120)
with c2:
    st.title('EduMentor : An AI-Enhanced Tutoring System')

# AI Tutor Description
st.markdown("## AI Tutor Description")
st.markdown("""
EduMentor leverages Retrieval-Augmented Generation (RAG) to provide accurate, context-aware responses to educational queries.
""")

# OpenAI API Key Handling
api_key = st.secrets.get("OPENAI_API_KEY", None) or st.text_input('Enter your OpenAI API Key', type='password')

if api_key:
    client = OpenAI(api_key=api_key)
    assistant_id = 'asst_SoUAlPBIF3KomZqPaqkEPgio'

    # Cache File Check to Improve Performance
    @st.cache_data(ttl=300)  # Cache data for 5 minutes
    def get_uploaded_files():
        return check_and_upload_files(client, assistant_id)

    files_info = get_uploaded_files()
    st.markdown(f'Number of files uploaded in the assistant: :blue[{len(files_info)}]')

    # Sidebar
    st.sidebar.header('EduMentor: AI-Tutor')
    st.sidebar.image(logo, width=120)
    st.sidebar.caption('Made by D')

    # File Deletion with UI Update
    if st.sidebar.button('Delete All Files from Assistant'):
        with st.spinner("Deleting files..."):
            assistant_files_response = client.beta.assistants.files.list(assistant_id=assistant_id)
            assistant_files = assistant_files_response.data

            for file in assistant_files:
                client.beta.assistants.files.delete(assistant_id=assistant_id, file_id=file.id)

            st.sidebar.success("All files deleted successfully.")
            st.experimental_rerun()  # Refresh UI

    # Chat History Download
    if st.sidebar.button('Generate Chat History'):
        html_data = generate_html(st.session_state.messages)
        st.sidebar.download_button(label="Download Chat History as HTML", data=html_data,
                                   file_name="chat_history.html", mime="text/html")

    # Chat Interface
    st.subheader('Q&A record with AI-Tutor 📜')
    st.caption('You can download chat history from the sidebar.')

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"], unsafe_allow_html=True)

    # Debounce User Input to Avoid Rapid Calls
    prompt = st.chat_input("Ask a question to the AI tutor")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar='👨🏻‍🏫'):
            message_placeholder = st.empty()
            with st.spinner('Thinking...'):
                try:
                    response = send_query_get_response(client, prompt, assistant_id)
                except Exception as e:
                    response = f"Error: {str(e)}"
            
            message_placeholder.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

else:
    st.warning("Please enter your OpenAI API Key to use EduMentor.")
