import firebase_admin
from firebase_admin import credentials, db
import os
import json

firebase_config_json = os.getenv("FIREBASE_CONFIG");
# firebase_config_json = open("chat_bot.json",mode="r",encoding="utf-8").read();

if not firebase_config_json:
    raise RuntimeError("Firebase configuration is missing!")

# Parse the JSON string
firebase_config = json.loads(firebase_config_json)

# Initialize Firebase app with service account key
cred = credentials.Certificate(firebase_config)  # Replace with your file path
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://campus-connect-5ef22-default-rtdb.asia-southeast1.firebasedatabase.app/"  # Replace with your database URL
})

# Fetch chatbot data from Firebase (returning as a list)
def fetch_chatbot_data():
    ref = db.reference("chatbot")
    data = ref.get() or {}  # Get data as a dictionary
    return [{"id": key, **value} for key, value in data.items()]  # Convert to a list of dictionaries

# Add new Q&A to Firebase (with dynamic ID)
def add_chatbot_entry(question, answer):
    ref = db.reference("chatbot")
    new_entry_ref = ref.push()  # Generates a unique key
    new_entry_ref.set({"questions": question, "answer": answer})  # Store data
    return {"id": new_entry_ref.key, "message": "Question added successfully"}

# Update a question-answer pair (requires ID)
def update_chatbot_entry(entry_id, question, answer):
    ref = db.reference(f"chatbot/{entry_id}")
    ref.update({"questions": question, "answer": answer})
    return {"message": "Question updated successfully"}

# Delete a question-answer pair (requires ID)
def delete_chatbot_entry(entry_id):
    ref = db.reference(f"chatbot/{entry_id}")
    ref.delete()
    return {"message": "Question deleted successfully"}



def add_questions_to_firebase(questions):
    chatbot_ref = db.reference("chatbot")
    print(questions);
    for question in questions:
        new_question_ref = chatbot_ref.push()  # Generate unique ID
        question_id = new_question_ref.key  # Get the generated key
        
        question_with_id = {
            "id": question_id,  # Include the ID inside the object
            **question  # Keep all other fields
        }
        
        new_question_ref.set(question_with_id)  # Store updated data

            






