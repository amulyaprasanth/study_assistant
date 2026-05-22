import os
import streamlit as st
import tempfile
import warnings
warnings.filterwarnings('ignore')

from src.study_assistant.data_ingestion import DataIngestion

st.set_page_config(page_title="Study Assistant", layout="wide")

st.title("Study Assistant")

if "data_ingestion" not in st.session_state:
    st.session_state["data_ingestion"] = DataIngestion()

uploaded_files = st.file_uploader(
    "Upload files",
    type=["pdf", "docx", "png", "jpg", "jpeg"],
    accept_multiple_files=True
)

all_docs = []

# BUTTON
if st.button("Process Files"):

    if not uploaded_files:
        st.warning("Please upload files first.")

    else:
        with st.spinner("Processing files..."):

            for uploaded_file in uploaded_files:

                # Get extension
                suffix = os.path.splitext(uploaded_file.name)[1]

                # Save temporarily
                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=suffix
                ) as tmp_file:

                    tmp_file.write(uploaded_file.getbuffer())
                    temp_path = tmp_file.name

                # Load documents
                docs = st.session_state["data_ingestion"].load_doc(temp_path)

                all_docs.extend(docs)

                st.success(
                    f"{uploaded_file.name} loaded successfully "
                    f"({len(docs)} documents)"
                )

