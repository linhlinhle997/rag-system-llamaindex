import os
import time

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
API_URL = os.getenv("BACKEND_URL")


def show(selectbox_key):
    st.title("📄 RAG File Uploader & Query System")

    # File Upload Section
    st.subheader("📂 Upload Files")
    uploaded_files = st.file_uploader(
        "Select files to upload",
        accept_multiple_files=True,
        type=["txt", "csv", "png", "jpg", "pdf"],
    )

    if st.button("Upload"):
        if uploaded_files:
            with st.spinner("Uploading files..."):
                response = upload_files(uploaded_files)

            if "error" in response:
                st.error(response["error"])
            else:
                st.success("✅ Files uploaded successfully!")
                st.subheader("Uploaded Files:")
                for file in response["upload_files"]:
                    st.write(f"📌 **{file['filename']}** - `{file['path']}`")
        else:
            st.warning("⚠️ Please select at least one file before uploading.")

    # Query Section
    st.subheader("🔍 Ask a Question")
    query_text = st.text_input("Enter your question:")

    if st.button("Search"):
        if query_text:
            with st.spinner("Processing your query..."):
                start_time = time.time()
                response = query_rag(query_text)
                end_time = time.time()
                processing_time = end_time - start_time

            st.info(f"⏳ Processing time: {processing_time:.2f} seconds")

            if "error" in response:
                st.error(response["error"])
            else:
                st.subheader("📖 Answer:")
                st.write(response.get("answer", "No answer found."))

                st.subheader("📚 Source Information:")
                for source in response.get("sources", []):
                    with st.expander(f"🧐 Confidence Score: {source['score']:.2f}"):
                        st.write(source["text"])
                        st.write(f"🔗 Source: {source['source']}")
        else:
            st.warning("⚠️ Please enter a question before searching.")

    st.markdown("---")

    # File Delete Section
    st.subheader("🗑️ Delete Uploaded Files")
    if st.button("Delete Files"):
        with st.spinner("Deleting files..."):
            response = delete_files(uploaded_files)

        if "error" in response:
            st.error(response["error"])
        else:
            st.success("✅ Files deleted successfully!")

    st.markdown("---")


def upload_files(files):
    """Uploads files to the backend and returns the response."""
    files_data = [("files", (file.name, file, file.type)) for file in files]
    response = requests.post(f"{API_URL}/rag/upload_file", files=files_data)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Failed to upload files."}


def delete_files(files):
    """Deletes files from the backend and returns the response."""
    response = requests.delete(f"{API_URL}/rag/delete_files")
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Failed to delete files."}


def query_rag(query_text):
    """Sends a query to the RAG system and returns the response."""
    response = requests.get(f"{API_URL}/rag/query?query_text={query_text}")
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Failed to fetch data from the server."}
