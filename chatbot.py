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


def get_best_match(user_input, lang="en", threshold=85):
    chatbot_data = fetch_chatbot_data()

    if not isinstance(chatbot_data, list):
        raise ValueError("Expected chatbot_data to be a list but got", type(chatbot_data))

    question_list = {
        entry["questions"][lang]: entry
        for entry in chatbot_data
        if lang in entry.get("questions", {})
    }

    if not question_list:
        print("No questions found in the selected language.")
        return None, 0, "Sorry, no matching questions found."

    # **Check for an exact match first**
    if user_input in question_list:
        matched_entry = question_list[user_input]
        answer = matched_entry["answer"].get(lang, "Sorry, I don't have an answer in this language.")
        print(f"Exact Match Found: {user_input}")
        return user_input, 100, answer  # Returning 100% match score for exact match

    # **If no exact match, proceed with fuzzy matching**
    best_match, score = process.extractOne(user_input, question_list.keys(), scorer=fuzz.WRatio)

    print(f"User Input: {user_input}")
    print(f"Best Match: {best_match}, Score: {score}")

    if score >= threshold:
        matched_entry = question_list[best_match]
        answer = matched_entry["answer"].get(lang, "Sorry, I don't have an answer in this language.")
        return best_match, score, answer
    else:
        print("Score below threshold. Returning default response.")
        return None, score, "Sorry, I couldn't understand your question. Please try again."
