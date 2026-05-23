import os
import tempfile
import warnings

import streamlit as st

from src.study_assistant.vectorstore import VectorDB
from src.study_assistant.data_ingestion import DataIngestion
from src.study_assistant.tasks import (
    generate_summary,
    generate_mcqs,
    generate_flashcards,
    generate_revision_notes
)
from src.study_assistant.llm import LLM

warnings.filterwarnings("ignore")

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Study Assistant",
    layout="wide"
)

st.title("📚 AI Study Assistant")

# ---------------- SESSION STATE ----------------
if "llm" not in st.session_state:
    st.session_state["llm"] = LLM().get_llm()

if "vectorstore" not in st.session_state:
    st.session_state["vectorstore"] = VectorDB()

if "data_ingestion" not in st.session_state:
    st.session_state["data_ingestion"] = DataIngestion()

if "docs_loaded" not in st.session_state:
    st.session_state["docs_loaded"] = False

# QUIZ STATE
if "quiz" not in st.session_state:
    st.session_state["quiz"] = None
    st.session_state["current_q"] = 0
    st.session_state["score"] = 0
    st.session_state["answered"] = False

# ---------------- FILE UPLOAD ----------------
uploaded_files = st.file_uploader(
    "Upload files",
    type=["pdf", "docx", "png", "jpg", "jpeg"],
    accept_multiple_files=True
)

col1, col2 = st.columns(2)

# ---------------- PROCESS FILES ----------------
with col1:
    if st.button("🚀 Process Files"):

        if not uploaded_files:
            st.warning("Please upload files first.")

        else:
            all_docs = []

            with st.spinner("Processing files..."):

                for uploaded_file in uploaded_files:
                    try:
                        suffix = os.path.splitext(uploaded_file.name)[1]

                        with tempfile.NamedTemporaryFile(
                            delete=False,
                            suffix=suffix
                        ) as tmp_file:

                            tmp_file.write(uploaded_file.getbuffer())
                            temp_path = tmp_file.name

                        docs = st.session_state[
                            "data_ingestion"
                        ].load_doc(temp_path)

                        all_docs.extend(docs)

                        os.remove(temp_path)

                        st.success(f"{uploaded_file.name} processed")

                    except Exception as e:
                        st.error(f"Error processing {uploaded_file.name}: {e}")

                st.session_state["vectorstore"].add_documents(all_docs)
                st.session_state["docs_loaded"] = True

                st.success(
                    f"✅ Added {len(all_docs)} documents to vector database"
                )

# ---------------- RESET VECTOR DB ----------------
with col2:
    if st.button("🗑 Reset Vector DB"):

        st.session_state["vectorstore"].reset_vectorstore()
        st.session_state["docs_loaded"] = False

        st.success("Vector database reset successfully")

# ---------------- TASK TABS ----------------
if st.session_state["docs_loaded"]:

    st.divider()

    tab1, tab2, tab3, tab4 = st.tabs([
        "🧠 Summary",
        "🧩 Quiz",
        "🗂 Flashcards",
        "⚡ Revision"
    ])

    # ---------------- SUMMARY ----------------
    with tab1:
        st.subheader("Generate Summary")

        if st.button("Generate Summary"):
            with st.spinner("Generating summary..."):
                docs = st.session_state["vectorstore"].retrieve(
                    "main concepts and explanations"
                )

                result = generate_summary(
                    st.session_state["llm"], docs
                )

                st.markdown(result)

    # ---------------- QUIZ ----------------
    with tab2:
        st.subheader("🧩 Interactive Quiz")

        if st.button("Generate Quiz"):
            with st.spinner("Generating quiz..."):
                docs = st.session_state["vectorstore"].retrieve(
                    "important definitions and exam questions"
                )

                quiz = generate_mcqs(
                    st.session_state["llm"], docs
                )

                if not quiz:
                    st.error("Failed to generate quiz")
                else:
                    st.session_state["quiz"] = quiz
                    st.session_state["current_q"] = 0
                    st.session_state["score"] = 0
                    st.session_state["answered"] = False

        # SHOW QUIZ
        if st.session_state["quiz"]:
            quiz = st.session_state["quiz"]
            idx = st.session_state["current_q"]

            if idx < len(quiz):
                q = quiz[idx]

                st.write(f"### Q{idx + 1}: {q.question}")

                selected = st.radio(
                    "Choose your answer:",
                    q.options,
                    key=f"q_{idx}"
                )

                if st.button("Submit Answer"):

                    if selected == q.answer:
                        st.success("✅ Correct!")
                        st.session_state["score"] += 1
                    else:
                        st.error(f"❌ Wrong! Correct: {q.answer}")

                    st.info(f"💡 {q.explanation}")
                    st.session_state["answered"] = True

                if st.session_state["answered"]:
                    if st.button("Next Question"):
                        st.session_state["current_q"] += 1
                        st.session_state["answered"] = False

                st.progress((idx + 1) / len(quiz))

            else:
                st.success("🎉 Quiz Completed!")
                st.write(
                    f"Score: {st.session_state['score']} / {len(quiz)}"
                )

                if st.button("Restart Quiz"):
                    st.session_state["quiz"] = None

    # ---------------- FLASHCARDS ----------------
    with tab3:
        st.subheader("Generate Flashcards")

        if st.button("Generate Flashcards"):
            with st.spinner("Generating flashcards..."):
                docs = st.session_state["vectorstore"].retrieve(
                    "key facts and short concepts"
                )

                cards = generate_flashcards(
                    st.session_state["llm"], docs
                )

                if not cards:
                    st.error("Failed to generate flashcards")
                else:
                    for c in cards:
                        st.write(f"**Q:** {c.question}")
                        st.write(f"**A:** {c.answer}")
                        st.divider()

    # ---------------- REVISION ----------------
    with tab4:
        st.subheader("Generate Revision Notes")

        if st.button("Generate Revision"):
            with st.spinner("Generating revision..."):
                docs = st.session_state["vectorstore"].retrieve(
                    "important concepts and key exam topics"
                )

                rev = generate_revision_notes(
                    st.session_state["llm"], docs
                )

                if not rev:
                    st.error("Failed to generate revision")
                else:
                    st.title(rev.title)

                    st.subheader("Key Concepts")
                    for x in rev.key_concepts:
                        st.write(f"- {x}")

                    st.subheader("Definitions")
                    for x in rev.definitions:
                        st.write(f"- {x}")

                    st.subheader("Formulas")
                    for x in rev.formulas:
                        st.write(f"- {x}")

                    st.subheader("Exam Points")
                    for x in rev.exam_points:
                        st.write(f"- {x}")

else:
    st.info("👆 Upload and process files to start using the AI features.")
