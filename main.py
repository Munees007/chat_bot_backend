from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from chatbot import get_best_match
from pydantic import BaseModel
from typing import List,Dict
from firebase import fetch_chatbot_data, add_chatbot_entry, update_chatbot_entry, delete_chatbot_entry,add_questions_to_firebase

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Allow all origins (Change this to specific frontend URL in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

class QuestionData(BaseModel):
    questions: Dict[str, str]  # Languages as keys, question text as values
    answer: Dict[str, str]  # Languages as keys, answer text as values


# API to receive JSON and store it in Firebase
@app.post("/chatbot/add-questions")
async def add_questions(data:List[QuestionData]):
    try:
        add_questions_to_firebase([q.model_dump() for q in data])
        return {"message": "All questions added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding questions: {str(e)}")
# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Chatbot API is running"}


# Get chatbot response
@app.get("/chatbot")
def chatbot_response(user_input: str, lang: str = "en"):
    print(f"Received user input: {user_input}")
    best_question, confidence, answer = get_best_match(user_input, lang)
    print(f"Best match: {best_question}, Confidence: {confidence}, Answer: {answer}")
    return {"best_question": best_question, "confidence": confidence, "answer": answer}

# Fetch all chatbot data
@app.get("/chatbot/data")
def get_chatbot_data():
    return fetch_chatbot_data()

# Add a new chatbot entry
@app.post("/chatbot/add")
def add_entry(question: dict, answer: dict):
    return add_chatbot_entry(question, answer)

# Update an existing chatbot entry
@app.put("/chatbot/update/{entry_id}")
def update_entry(entry_id: str, question: dict, answer: dict):
    return update_chatbot_entry(entry_id, question, answer)

# Delete a chatbot entry
@app.delete("/chatbot/delete/{entry_id}")
def delete_entry(entry_id: str):
    return delete_chatbot_entry(entry_id)
