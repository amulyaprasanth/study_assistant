from pydantic import BaseModel
from typing import List

# ---------------- MCQ ----------------
class MCQ(BaseModel):
    question: str
    options: List[str]
    answer: str
    explanation: str

class MCQResponse(BaseModel):
    questions: List[MCQ]


# ---------------- FLASHCARDS ----------------
class Flashcard(BaseModel):
    question: str
    answer: str

class FlashcardResponse(BaseModel):
    flashcards: List[Flashcard]


# ---------------- REVISION ----------------
class RevisionResponse(BaseModel):
    title: str
    key_concepts: List[str]
    definitions: List[str]
    formulas: List[str]
    exam_points: List[str]
