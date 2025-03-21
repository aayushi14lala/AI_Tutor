import openai
import streamlit as st
import os

def upload_files_to_assistant(client, uploaded_files):
    file_ids = []
    file_paths = []

    for uploaded_file in uploaded_files:
        if uploaded_file is not None:
            file_path = os.path.join(os.getcwd(), uploaded_file.name)

            try:
                response = client.files.create(
                    file=(uploaded_file.name, uploaded_file.read()),
                    purpose="assistants"
                )
                file_ids.append(response.id)
                file_paths.append(file_path)
            except Exception as e:
                st.error(f"File upload failed: {e}")

    print("Uploaded file paths:", file_paths)
    return file_ids, file_paths


def attach_files_to_assistant(client, file_ids, assistant_id):
    attached_files = []

    for file_id in file_ids:
        try:
            response = client.beta.assistants.update(
                assistant_id,
                file_ids=[file_id]
            )
            attached_files.append(response)
        except Exception as e:
            st.error(f"Error attaching file {file_id}: {e}")

    return attached_files


def check_and_upload_files(client, assistant_id):
    # Retrieve assistant details to get the list of attached files
    try:
        assistant = client.beta.assistants.retrieve(assistant_id)
        files_info = assistant.file_ids if hasattr(assistant, "file_ids") else []
    except Exception as e:
        st.error(f"Error retrieving assistant files: {e}")
        files_info = []

    if not files_info:
        st.warning("No Files Included, Upload Educational Material")
        uploaded_files = st.file_uploader("Choose PDF files", type="pdf", accept_multiple_files=True)

        if st.button("Upload and Attach Files"):
            if uploaded_files:
                try:
                    file_ids, file_paths = upload_files_to_assistant(client, uploaded_files)

                    attached_files_info = attach_files_to_assistant(client, file_ids, assistant_id)

                    if not attached_files_info:
                        st.warning("No files were attached. Loading default data...")
                    else:
                        st.success(f"{len(attached_files_info)} files successfully attached.")
                except Exception as e:
                    st.error(f"An error occurred while attaching files: {e}")
            else:
                st.warning("Please select at least one file to upload.")
    
    return files_info
