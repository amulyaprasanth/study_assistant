import json
from src.study_assistant.schemas import FlashcardResponse, MCQResponse, RevisionResponse
from src.study_assistant import logger, CustomException

def generate_summary(llm, docs):
    context = "\n\n".join([d.page_content for d in docs])

    prompt = f"""
 You are an expert academic tutor.

Your task is to convert the given content into clear, structured, exam-ready notes.

Instructions:
- Focus on key concepts, definitions, and important explanations
- Keep it concise but complete
- Use bullet points and headings
- Highlight formulas, key terms, and important facts
- Avoid unnecessary details

Content:
{context}

Output format:
- Title
- Key Concepts (bulleted)
- Important Definitions
- Key Points for Revision

    
    """

    return llm.invoke(prompt).content


def generate_mcqs(llm, docs):
    context = "\n\n".join([d.page_content for d in docs])

    prompt = f"""
You are an expert exam paper setter.

Create 5 high-quality multiple choice questions.

Content:
{context}

Return ONLY valid JSON:

{{
  "questions": [
    {{
      "question": "...",
      "options": ["A", "B", "C", "D"],
      "answer": "A",
      "explanation": "..."
    }}
  ]
}}
"""

    response = llm.invoke(prompt).content

    try:
        data = json.loads(response)
        validated = MCQResponse(**data)
        return validated.questions

    except Exception as e:
        print("MCQ Parsing Error:", e)
        return []

def generate_flashcards(llm, docs):
    context = "\n\n".join([d.page_content for d in docs])

    prompt = f"""
Convert into flashcards.

Content:
{context}

Return ONLY valid JSON:

{{
  "flashcards": [
    {{
      "question": "...",
      "answer": "..."
    }}
  ]
}}
"""

    response = llm.invoke(prompt).content

    try:
        import json
        import re

        cleaned = re.sub(r"```json|```", "", response).strip()
        data = json.loads(cleaned)

        validated = FlashcardResponse(**data)
        return validated.flashcards

    except Exception as e:
        print("Flashcard Error:", e)
        return []


def generate_revision_notes(llm, docs):
    context = "\n\n".join([d.page_content for d in docs])

    prompt = f"""
Create a revision guide.

Content:
{context}

Return ONLY valid JSON:

{{
  "title": "...",
  "key_concepts": ["..."],
  "definitions": ["..."],
  "formulas": ["..."],
  "exam_points": ["..."]
}}
"""

    response = llm.invoke(prompt).content

    try:
        import json
        import re

        cleaned = re.sub(r"```json|```", "", response).strip()
        data = json.loads(cleaned)

        validated = RevisionResponse(**data)
        return validated

    except Exception as e:
        print("Revision Error:", e)
        return None
