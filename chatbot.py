import random
from fuzzywuzzy import process, fuzz
from firebase import fetch_chatbot_data

# def get_best_match(user_input, lang="en"):
#     chatbot_data = fetch_chatbot_data()
#     # Extract all questions in the selected language
#     question_list = {entry["questions"][lang]: entry for entry in chatbot_data.values() if lang in entry["questions"]}

#     # Use fuzzy matching to find the best match
#     best_match, score = process.extractOne(user_input, question_list.keys())

#     # Retrieve the corresponding answer
#     matched_entry = question_list[best_match]
#     answer = matched_entry["answer"].get(lang, "Sorry, I don't have an answer in this language.")

#     return best_match, score, answer





# Predefined sorry messages
SORRY_MESSAGES = [
    "Sorry, I couldn't understand your question. Please try again.",
    "I'm not sure about that. Can you rephrase?",
    "I don't have an answer for that. Try asking differently.",
    "I couldn't find a match. Please ask another way.",
]

def get_best_match(user_input, lang="en", threshold=85):
    chatbot_data = fetch_chatbot_data()

    if not isinstance(chatbot_data, list):
        raise ValueError("Expected chatbot_data to be a list but got", type(chatbot_data))

    print(f"User Input: {user_input}")

    # ✅ Normalize question list across all languages
    question_list = {}
    for entry in chatbot_data:
        for q_lang, question in entry.get("questions", {}).items():
            question_list[question.lower()] = entry  # Store question in any language

    if not question_list:
        print("❌ No questions found in the database!")
        return None, 0, "Sorry, no questions are available in the database."

    # ✅ Normalize input
    normalized_input = user_input.lower().strip()

    # ✅ 1. Check for an exact match
    if normalized_input in question_list:
        matched_entry = question_list[normalized_input]
        answer = matched_entry["answer"].get(lang, random.choice(SORRY_MESSAGES))
        print(f"✅ Exact match found: {normalized_input}")
        return normalized_input, 100, answer  

    # ✅ 2. Improve fuzzy matching for short inputs
    input_words = normalized_input.split()
    if len(input_words) <= 2:  # If input is very short (like "college name")
        threshold = 50  # Lower threshold for better matches

    # ✅ 3. Use `token_set_ratio` for better matching
    print("🔎 No exact match found. Using fuzzy matching...")
    best_match, score = process.extractOne(normalized_input, question_list.keys(), scorer=fuzz.token_set_ratio)

    print(f"Best Match: {best_match}, Score: {score}")

    # ✅ 4. Return only if above threshold
    if score >= threshold:
        matched_entry = question_list[best_match]
        answer = matched_entry["answer"].get(lang, random.choice(SORRY_MESSAGES))
        return best_match, score, answer
    else:
        print("❌ Score below threshold. Returning default response.")
        return None, 0, random.choice(SORRY_MESSAGES)
