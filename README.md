# 📚 StudyMind AI

An AI-powered study assistant that transforms your PDFs and notes into summaries, flashcards, quizzes, and revision guides — powered by LLaMA 3 via Groq and a RAG pipeline.

---

## 🚀 Features

| Feature                 | Description                                                                |
| ----------------------- | -------------------------------------------------------------------------- |
| 📄 **Document Upload**  | Upload PDF and DOCX files                                                  |
| 🧠 **AI Summarization** | Structured, exam-ready notes from your content                             |
| 🧩 **MCQ Quiz**         | Auto-generated multiple choice questions with explanations                 |
| 🗂 **Flashcards**       | Key Q&A pairs for quick revision                                           |
| ⚡ **Revision Notes**   | Structured guide with key concepts, definitions, formulas, and exam points |
| 🔍 **RAG-powered Q&A**  | Context-aware retrieval using FAISS vector search                          |

---

## 🛠️ Tech Stack

**Frontend**

- React 19 + TypeScript
- Vite
- Custom CSS

**Backend — FastAPI (primary)**

- FastAPI + Uvicorn
- FAISS (in-memory vector store)
- HuggingFace Embeddings (`all-MiniLM-L6-v2`)
- LangChain (RAG pipeline)
- Groq API — LLaMA 3.1 8B Instant

**Backend — Streamlit (alternate UI)**

- Streamlit app (`app.py`) for standalone use without the React frontend

**AI / ML**

- Retrieval-Augmented Generation (RAG)
- Sentence Transformers for semantic embeddings
- Pydantic-validated structured LLM outputs

---

## 📁 Project Structure

```
Study Assistant/
├── backend/
│   ├── api.py                  # FastAPI app (used by React frontend)
│   ├── app.py                  # Streamlit app (standalone UI)
│   ├── requirements.txt
│   ├── .env                    # API keys (not committed)
│   └── src/study_assistant/
│       ├── llm.py              # Groq LLM initialization
│       ├── vectorstore.py      # FAISS vector DB wrapper
│       ├── data_ingestion.py   # PDF/DOCX loader + text splitter
│       ├── tasks.py            # Summary, MCQ, flashcard, revision generators
│       ├── schemas.py          # Pydantic response models
│       └── __init__.py
└── studyAssistant/             # React + TypeScript frontend
    ├── src/
    │   ├── api.ts              # API client (fetch wrappers)
    │   ├── App.tsx             # Root component with tab navigation
    │   └── components/
    │       ├── Upload.tsx
    │       ├── Summary.tsx
    │       ├── Quiz.tsx
    │       ├── Flashcards.tsx
    │       └── Revision.tsx
    └── package.json
```

---

## ⚙️ Setup & Installation

### Prerequisites

- Python 3.10+
- Node.js 18+
- A [Groq API key](https://console.groq.com/)

### 1. Clone the repository

```bash
git clone https://github.com/your-username/studymind-ai.git
cd "Study Assistant"
```

### 2. Backend setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
```

Create a `.env` file in the `backend/` directory:

```env
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Run the backend

**FastAPI (for React frontend):**

```bash
uvicorn api:app --reload --port 8000
```

**Streamlit (standalone):**

```bash
streamlit run app.py
```

### 4. Frontend setup

```bash
cd studyAssistant
npm install
npm run dev
```

The React app runs at `http://localhost:5173` and connects to the FastAPI backend at `http://localhost:8000`.

---

## 🔑 Environment Variables

| Variable       | Description                          |
| -------------- | ------------------------------------ |
| `GROQ_API_KEY` | Your Groq API key for LLaMA 3 access |

---

## 📡 API Endpoints

| Method | Endpoint      | Description                         |
| ------ | ------------- | ----------------------------------- |
| `GET`  | `/status`     | Check API health and doc load state |
| `POST` | `/upload`     | Upload PDF/DOCX files               |
| `POST` | `/reset`      | Clear the vector database           |
| `GET`  | `/summary`    | Generate a structured summary       |
| `GET`  | `/quiz`       | Generate 5 MCQs with answers        |
| `GET`  | `/flashcards` | Generate 8 flashcards               |
| `GET`  | `/revision`   | Generate structured revision notes  |

---

## 📄 License

This project is licensed under the MIT License.
