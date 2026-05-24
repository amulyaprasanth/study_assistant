import os
import tempfile
import warnings
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.study_assistant.vectorstore import VectorDB
from src.study_assistant.data_ingestion import DataIngestion
from src.study_assistant.tasks import (
    generate_summary,
    generate_mcqs,
    generate_flashcards,
    generate_revision_notes,
)
from src.study_assistant.llm import LLM

warnings.filterwarnings("ignore")

NO_DOCS_MSG = "No documents loaded"

# ---------- App state (populated on startup) ----------
state: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize heavy singletons once the event loop is running."""
    state["llm"] = LLM().get_llm()
    state["vectorstore"] = VectorDB()
    state["data_ingestion"] = DataIngestion()
    state["docs_loaded"] = False
    yield
    # cleanup (if needed) goes here


app = FastAPI(title="Study Assistant API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://wisdomxai.netlify.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Response models ----------
class StatusResponse(BaseModel):
    message: str
    docs_loaded: bool


class MCQItem(BaseModel):
    question: str
    options: List[str]
    answer: str
    explanation: str


class FlashcardItem(BaseModel):
    question: str
    answer: str


class RevisionNotes(BaseModel):
    title: str
    key_concepts: List[str]
    definitions: List[str]
    formulas: List[str]
    exam_points: List[str]


# ---------- Routes ----------

@app.get("/status", response_model=StatusResponse)
def get_status():
    return {"message": "API is running", "docs_loaded": state["docs_loaded"]}


@app.post("/upload", response_model=StatusResponse)
async def upload_files(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    all_docs = []
    errors = []

    for uploaded_file in files:
        suffix = os.path.splitext(uploaded_file.filename)[1].lower()

        if suffix not in [".pdf", ".docx"]:
            errors.append(
                f"{uploaded_file.filename}: unsupported type (use pdf or docx)")
            continue

        tmp_path = None
        try:
            content = await uploaded_file.read()

            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(content)
                tmp_path = tmp.name

            docs = state["data_ingestion"].load_doc(tmp_path)
            all_docs.extend(docs)

        except Exception as e:
            errors.append(f"{uploaded_file.filename}: {str(e)}")

        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)

    if all_docs:
        state["vectorstore"].add_documents(all_docs)
        state["docs_loaded"] = True

    msg = f"Added {len(all_docs)} document chunks to vector database."
    if errors:
        msg += " Errors: " + "; ".join(errors)

    return {"message": msg, "docs_loaded": state["docs_loaded"]}


@app.post("/reset", response_model=StatusResponse)
def reset_vectorstore():
    state["vectorstore"].reset_vectorstore()
    state["docs_loaded"] = False
    return {"message": "Vector database reset successfully", "docs_loaded": False}


@app.get("/summary")
def get_summary():
    if not state["docs_loaded"]:
        raise HTTPException(status_code=400, detail=NO_DOCS_MSG)
    docs = state["vectorstore"].retrieve("main concepts and explanations")
    result = generate_summary(state["llm"], docs)
    return {"summary": result}


@app.get("/quiz", response_model=List[MCQItem])
def get_quiz():
    if not state["docs_loaded"]:
        raise HTTPException(status_code=400, detail=NO_DOCS_MSG)
    docs = state["vectorstore"].retrieve(
        "important definitions and exam questions")
    questions = generate_mcqs(state["llm"], docs)
    if not questions:
        raise HTTPException(status_code=500, detail="Failed to generate quiz")
    return [q.model_dump() for q in questions]


@app.get("/flashcards", response_model=List[FlashcardItem])
def get_flashcards():
    if not state["docs_loaded"]:
        raise HTTPException(status_code=400, detail=NO_DOCS_MSG)
    docs = state["vectorstore"].retrieve("key facts and short concepts")
    cards = generate_flashcards(state["llm"], docs)
    if not cards:
        raise HTTPException(
            status_code=500, detail="Failed to generate flashcards")
    return [c.model_dump() for c in cards]


@app.get("/revision", response_model=RevisionNotes)
def get_revision():
    if not state["docs_loaded"]:
        raise HTTPException(status_code=400, detail=NO_DOCS_MSG)
    docs = state["vectorstore"].retrieve(
        "important concepts and key exam topics")
    rev = generate_revision_notes(state["llm"], docs)
    if not rev:
        raise HTTPException(
            status_code=500, detail="Failed to generate revision notes")
    return rev.model_dump()
