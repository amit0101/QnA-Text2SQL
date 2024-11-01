from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid
from model.rag_model import answer_question

app = FastAPI()

# In-memory store to keep session history
session_store = {}

class QuestionRequest(BaseModel):
    question: str
    session_id: str

class AnswerResponse(BaseModel):
    answer: str
    collection_count: int

@app.post("/ask_question", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    session_id = request.session_id
    question = request.question

    if not session_id or not question:
        raise HTTPException(status_code=400, detail="Invalid input")

    # Get the answer using the RAG model
    answer, collection_count = answer_question(question, session_id)
    return AnswerResponse(answer=answer, collection_count=collection_count)

@app.post("/start_new_conversation")
async def start_new_conversation():
    # Generate a new session ID and clear any existing memory
    session_id = str(uuid.uuid4())
    session_store[session_id] = []
    return {"session_id": session_id, "message": "New conversation started and memory cleared"}
