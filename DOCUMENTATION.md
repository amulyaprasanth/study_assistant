# StudyMind AI — Hackathon Documentation

> **An AI-powered study assistant that transforms raw study material into structured learning tools using Retrieval-Augmented Generation (RAG).**

---

## Table of Contents

1. [Problem Statement](#1-problem-statement)
2. [Solution Overview](#2-solution-overview)
3. [Architecture Diagram](#3-architecture-diagram)
4. [Component Breakdown](#4-component-breakdown)
5. [Data Flow](#5-data-flow)
6. [Tech Stack](#6-tech-stack)
7. [API Reference](#7-api-reference)
8. [Key Design Decisions](#8-key-design-decisions)
9. [Setup & Running Locally](#9-setup--running-locally)
10. [Future Roadmap](#10-future-roadmap)

---

## 1. Problem Statement

Students spend a disproportionate amount of time re-reading notes and textbooks rather than actively testing their knowledge. Manually creating summaries, flashcards, and practice questions from dense study material is time-consuming and inconsistent.

**StudyMind AI** solves this by automatically converting uploaded documents into structured, exam-ready study tools in seconds.

---

## 2. Solution Overview

Users upload their PDF or DOCX study material. The system:

1. Parses and chunks the document
2. Embeds the chunks into a FAISS vector store
3. Retrieves the most relevant context for each task
4. Sends the context to a LLaMA 3 LLM (via Groq) with a task-specific prompt
5. Returns structured, validated output to the frontend

The result is a full study toolkit — summary, quiz, flashcards, and revision notes — generated from the user's own material.

---

## 3. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                          USER BROWSER                               │
│                                                                     │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │              React + TypeScript Frontend (Vite)             │   │
│   │                                                             │   │
│   │  ┌──────────┐  ┌─────────┐  ┌───────────┐  ┌──────────┐   │   │
│   │  │  Upload  │  │ Summary │  │   Quiz    │  │Flashcards│   │   │
│   │  │Component │  │  Tab    │  │   Tab     │  │   Tab    │   │   │
│   │  └──────────┘  └─────────┘  └───────────┘  └──────────┘   │   │
│   │                                          ┌──────────────┐  │   │
│   │                                          │ Revision Tab │  │   │
│   │                                          └──────────────┘  │   │
│   │                        api.ts (fetch client)               │   │
│   └──────────────────────────┬──────────────────────────────────┘   │
└──────────────────────────────│──────────────────────────────────────┘
                               │  HTTP REST (JSON)
                               │  POST /upload
                               │  GET  /summary | /quiz | /flashcards | /revision
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     FastAPI Backend  (port 8000)                    │
│                                                                     │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │                      api.py  (Routes)                       │   │
│   │  /upload  /reset  /status  /summary  /quiz  /flashcards     │   │
│   │  /revision                                                  │   │
│   └──────────┬──────────────────────────────────────────────────┘   │
│              │                                                      │
│    ┌─────────▼──────────┐      ┌──────────────────────────────┐    │
│    │   DataIngestion    │      │         VectorDB             │    │
│    │  (data_ingestion.py)│      │      (vectorstore.py)        │    │
│    │                    │      │                              │    │
│    │  PyPDFLoader       │      │  HuggingFace Embeddings      │    │
│    │  Docx2txtLoader    │─────▶│  all-MiniLM-L6-v2            │    │
│    │                    │ docs │                              │    │
│    │  RecursiveChar     │      │  FAISS In-Memory Index       │    │
│    │  TextSplitter      │      │  (add / retrieve / reset)    │    │
│    │  chunk=1000        │      └──────────────┬───────────────┘    │
│    │  overlap=120       │                     │ top-k docs          │
│    └────────────────────┘                     │                    │
│                                               ▼                    │
│                                  ┌────────────────────────┐        │
│                                  │      tasks.py          │        │
│                                  │                        │        │
│                                  │  generate_summary()    │        │
│                                  │  generate_mcqs()       │        │
│                                  │  generate_flashcards() │        │
│                                  │  generate_revision()   │        │
│                                  │                        │        │
│                                  │  _extract_json()       │        │
│                                  └───────────┬────────────┘        │
│                                              │ prompt + context     │
│                                              ▼                     │
│                                  ┌────────────────────────┐        │
│                                  │        llm.py          │        │
│                                  │   ChatGroq             │        │
│                                  │   llama-3.1-8b-instant │        │
│                                  └───────────┬────────────┘        │
│                                              │                     │
└──────────────────────────────────────────────│─────────────────────┘
                                               │  HTTPS API call
                                               ▼
                               ┌───────────────────────────┐
                               │       Groq Cloud API      │
                               │   LLaMA 3.1 8B Instant    │
                               │   (inference endpoint)    │
                               └───────────────────────────┘


  ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
  ALTERNATE UI (standalone, no React required)

  ┌──────────────────────────────────────────────────────────────┐
  │              Streamlit App  (app.py)                         │
  │  File uploader → same DataIngestion → VectorDB → tasks.py   │
  └──────────────────────────────────────────────────────────────┘
```

---

## 4. Component Breakdown

### Frontend (`studyAssistant/`)

| File             | Role                                                            |
| ---------------- | --------------------------------------------------------------- |
| `App.tsx`        | Root component; manages `docsLoaded` state and tab navigation   |
| `api.ts`         | Typed fetch wrappers for all backend endpoints                  |
| `Upload.tsx`     | File picker, calls `POST /upload`, triggers `onLoaded` callback |
| `Summary.tsx`    | Calls `GET /summary`, renders markdown-formatted notes          |
| `Quiz.tsx`       | Calls `GET /quiz`, renders interactive MCQ with score tracking  |
| `Flashcards.tsx` | Calls `GET /flashcards`, renders flip-card style Q&A            |
| `Revision.tsx`   | Calls `GET /revision`, renders structured revision guide        |

### Backend (`backend/`)

| File                | Role                                                         |
| ------------------- | ------------------------------------------------------------ |
| `api.py`            | FastAPI application; all REST routes; CORS enabled           |
| `app.py`            | Streamlit application; same AI pipeline, browser-based UI    |
| `llm.py`            | Initializes `ChatGroq` with `llama-3.1-8b-instant`           |
| `vectorstore.py`    | FAISS wrapper — add documents, semantic retrieval, reset     |
| `data_ingestion.py` | Loads PDF/DOCX, splits into 1000-char chunks (120 overlap)   |
| `tasks.py`          | Prompt templates + LLM calls + JSON extraction for each task |
| `schemas.py`        | Pydantic models: `MCQ`, `Flashcard`, `RevisionResponse`      |

---

## 5. Data Flow

### Document Ingestion

```
User uploads file
       │
       ▼
POST /upload (multipart/form-data)
       │
       ▼
Save to temp file
       │
       ▼
DataIngestion.load_doc()
  ├── PyPDFLoader  (PDF)
  └── Docx2txtLoader (DOCX)
       │
       ▼
RecursiveCharacterTextSplitter
  chunk_size=1000, overlap=120
       │
       ▼
List[Document] (LangChain)
       │
       ▼
VectorDB.add_documents()
  └── HuggingFace Embeddings → FAISS index
       │
       ▼
docs_loaded = True
```

### Task Generation (e.g., Quiz)

```
GET /quiz
    │
    ▼
VectorDB.retrieve("important definitions and exam questions", k=5)
    │  semantic similarity search
    ▼
Top-5 relevant document chunks
    │
    ▼
tasks.generate_mcqs(llm, docs)
    │  builds prompt with context
    ▼
ChatGroq → LLaMA 3.1 8B Instant
    │  returns JSON string
    ▼
_extract_json()  (handles markdown fences, prose wrapping)
    │
    ▼
MCQResponse (Pydantic validation)
    │
    ▼
List[MCQItem] → JSON response to frontend
```

---

## 6. Tech Stack

### Backend

| Technology            | Version | Purpose                         |
| --------------------- | ------- | ------------------------------- |
| Python                | 3.10+   | Runtime                         |
| FastAPI               | latest  | REST API framework              |
| Uvicorn               | latest  | ASGI server                     |
| LangChain             | latest  | RAG orchestration               |
| langchain-groq        | latest  | Groq LLM integration            |
| langchain-huggingface | latest  | HuggingFace embeddings          |
| FAISS (faiss-cpu)     | latest  | Vector similarity search        |
| Sentence Transformers | latest  | `all-MiniLM-L6-v2` embeddings   |
| Pydantic              | v2      | Data validation & schemas       |
| PyPDF                 | latest  | PDF parsing                     |
| Docx2txt              | latest  | DOCX parsing                    |
| Streamlit             | latest  | Alternate standalone UI         |
| python-dotenv         | latest  | Environment variable management |

### Frontend

| Technology | Version | Purpose                 |
| ---------- | ------- | ----------------------- |
| React      | 19      | UI framework            |
| TypeScript | ~6.0    | Type safety             |
| Vite       | 8       | Build tool & dev server |
| Fetch API  | native  | HTTP client             |

### AI / Cloud

| Technology           | Purpose                                 |
| -------------------- | --------------------------------------- |
| Groq Cloud API       | Ultra-fast LLM inference                |
| LLaMA 3.1 8B Instant | Language model for all generation tasks |
| `all-MiniLM-L6-v2`   | Sentence embeddings for semantic search |

---

## 7. API Reference

Base URL: `http://localhost:8000`

### `GET /status`

Returns API health and whether documents are loaded.

**Response:**

```json
{
  "message": "API is running",
  "docs_loaded": true
}
```

---

### `POST /upload`

Upload one or more PDF or DOCX files.

**Request:** `multipart/form-data` with field `files`

**Response:**

```json
{
  "message": "Added 42 document chunks to vector database.",
  "docs_loaded": true
}
```

---

### `POST /reset`

Clears the in-memory FAISS vector store.

**Response:**

```json
{
  "message": "Vector database reset successfully",
  "docs_loaded": false
}
```

---

### `GET /summary`

Generates structured exam-ready notes.

**Response:**

```json
{
  "summary": "## Key Concepts\n- ..."
}
```

---

### `GET /quiz`

Generates 5 multiple choice questions.

**Response:**

```json
[
  {
    "question": "What is ...",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "answer": "A",
    "explanation": "Because ..."
  }
]
```

---

### `GET /flashcards`

Generates 8 flashcard Q&A pairs.

**Response:**

```json
[
  {
    "question": "Define ...",
    "answer": "It is ..."
  }
]
```

---

### `GET /revision`

Generates a structured revision guide.

**Response:**

```json
{
  "title": "Topic Title",
  "key_concepts": ["..."],
  "definitions": ["..."],
  "formulas": ["..."],
  "exam_points": ["..."]
}
```

---

## 8. Key Design Decisions

### RAG over full-document prompting

Rather than sending the entire document to the LLM, we embed and retrieve only the top-k most relevant chunks per task. This keeps prompts within token limits, reduces cost, and improves answer relevance.

### FAISS in-memory store

FAISS runs entirely in-process with no external database dependency. This makes the project zero-infrastructure — ideal for a hackathon demo. The tradeoff is that the index is lost on server restart, which is acceptable for a session-based use case.

### Groq + LLaMA 3.1 8B Instant

Groq's inference hardware delivers near-instant responses even for structured generation tasks. LLaMA 3.1 8B is small enough to be fast but capable enough to produce well-structured JSON outputs reliably.

### Pydantic-validated LLM outputs

All LLM responses are parsed and validated through Pydantic models (`MCQResponse`, `FlashcardResponse`, `RevisionResponse`). This prevents malformed data from reaching the frontend and makes the API contract explicit.

### Robust JSON extraction (`_extract_json`)

LLMs sometimes wrap JSON in markdown code fences or add prose. The `_extract_json` utility handles all common cases — raw JSON, fenced blocks, and JSON buried in text — making the pipeline resilient to LLM formatting quirks.

### Dual UI (FastAPI + Streamlit)

The project ships with two UIs: a production-grade React frontend communicating via REST, and a Streamlit app for quick standalone demos. Both share the exact same AI pipeline code.

---

## 9. Setup & Running Locally

### Requirements

- Python 3.10+
- Node.js 18+
- Groq API key → [console.groq.com](https://console.groq.com)

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

Create `backend/.env`:

```env
GROQ_API_KEY=your_key_here
```

Run FastAPI:

```bash
uvicorn api:app --reload --port 8000
```

Or run Streamlit:

```bash
streamlit run app.py
```

### Frontend

```bash
cd studyAssistant
npm install
npm run dev
# → http://localhost:5173
```

---

## 10. Future Roadmap

| Feature                    | Description                                          |
| -------------------------- | ---------------------------------------------------- |
| 🔐 User authentication     | Session-based document isolation per user            |
| 💾 Persistent vector store | Save/load FAISS index to disk between sessions       |
| 🖼 Image/diagram support   | OCR pipeline for image-based study material          |
| 💬 Chat Q&A mode           | Conversational interface over uploaded documents     |
| 📊 Progress tracking       | Track quiz scores and revision history over time     |
| 🌐 Multi-language support  | Summarization and quiz generation in other languages |
| ☁️ Cloud deployment        | Docker + cloud hosting for public access             |

---

_Built for hackathon — StudyMind AI © 2025_
