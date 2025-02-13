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


from fuzzywuzzy import process, fuzz

def get_best_match(user_input, lang="en", threshold=85):
    chatbot_data = fetch_chatbot_data()

    if not isinstance(chatbot_data, list):
        raise ValueError("Expected chatbot_data to be a list but got", type(chatbot_data))

    # ✅ Normalize question list (lowercase for matching)
    question_list = {
        entry["questions"][lang].lower(): entry
        for entry in chatbot_data
        if lang in entry.get("questions", {})
    }

    print(f"User Input: {user_input}")

    # ✅ 1. If no questions exist in database, return immediately
    if not question_list:
        print("❌ No questions found in the database!")
        return None, 0, "Sorry, no questions are available in the database."

    # ✅ 2. Check for an exact match (ignoring case)
    normalized_input = user_input.lower()
    if normalized_input in question_list:
        matched_entry = question_list[normalized_input]
        answer = matched_entry["answer"].get(lang, "Sorry, I don't have an answer in this language.")
        print(f"✅ Exact match found: {normalized_input}")
        return normalized_input, 100, answer  # 100 because it's an exact match

    # ✅ 3. If no exact match, use fuzzy matching
    print("🔎 No exact match found. Using fuzzy matching...")
    best_match, score = process.extractOne(normalized_input, question_list.keys(), scorer=fuzz.WRatio)

    print(f"Best Match: {best_match}, Score: {score}")

    # ✅ 4. Only return fuzzy match if it's above the threshold
    if score >= threshold:
        matched_entry = question_list[best_match]
        answer = matched_entry["answer"].get(lang, "Sorry, I don't have an answer in this language.")
        return best_match, score, answer
    else:
        print("❌ Score below threshold. Returning default response.")
        return None, 0, "Sorry, I couldn't understand your question. Please try again."
