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
import random


# Predefined sorry messages for different languages
SORRY_MESSAGES = {
    "en": [
        "Sorry, I couldn't understand your question. Please try again.",
        "I'm not sure about that. Can you rephrase?",
        "I don't have an answer for that. Try asking differently.",
        "I couldn't find a match. Please ask another way.",
    ],
    "ta": [
        "மன்னிக்கவும், உங்கள் கேள்வியை புரிந்துகொள்ள முடியவில்லை. தயவுசெய்து மீண்டும் முயற்சிக்கவும்.",
        "எனக்குத் தெளிவாக இல்லை. மீண்டும் சொல்ல முடியுமா?",
        "இந்தக் கேள்விக்கு எனக்கு பதில் இல்லை. வேறொரு முறையில் கேட்கவும்.",
        "பொருத்தமான பதில் கிடைக்கவில்லை. மற்றொரு முறையில் முயற்சிக்கவும்.",
    ],
    "te": [
        "క్షమించండి, మీ ప్రశ్నను అర్థం చేసుకోలేకపోయాను. దయచేసి మళ్లీ ప్రయత్నించండి.",
        "నాకు స్పష్టంగా లేదు. మీరు మళ్లీ చెప్పగలరా?",
        "దయచేసి వేరే విధంగా అడగండి.",
        "నేను సమాధానం ఇవ్వలేకపోయాను. మరోసారి ప్రయత్నించండి.",
    ],
    "ml": [
        "ക്ഷമിക്കണം, നിങ്ങളുടെ ചോദ്യത്തിൽ വ്യക്തതയില്ല. ദയവായി വീണ്ടും ശ്രമിക്കുക.",
        "എനിക്ക് അതിന്റെ ഉത്തരം അറിയില്ല. ദയവായി വീണ്ടും ചോദിക്കുക.",
        "ഞാൻ ഇതിന് ഉത്തരം നൽകാനാകില്ല. ദയവായി മറ്റൊരു വിധത്തിൽ ചോദിക്കുക.",
        "ഒരു പൊരുത്തവും കണ്ടെത്തിയില്ല. ദയവായി മറ്റൊരു രീതിയിൽ ചോദിക്കുക.",
    ],
    "hi": [
        "माफ़ कीजिए, मैं आपके सवाल को समझ नहीं पाया। कृपया फिर से कोशिश करें।",
        "मुझे यकीन नहीं है। क्या आप इसे दोबारा समझा सकते हैं?",
        "मुझे इसका जवाब नहीं पता। कृपया दूसरे तरीके से पूछें।",
        "मुझे कोई उपयुक्त उत्तर नहीं मिला। कृपया दूसरा तरीका अपनाएं।",
    ],
}

def get_best_match(user_input, lang="en", threshold=85):  
    chatbot_data = fetch_chatbot_data()

    if not isinstance(chatbot_data, list):
        raise ValueError("Expected chatbot_data to be a list but got", type(chatbot_data))

    # ✅ Normalize question list (supporting all languages, not just selected one)
    question_list = {}
    entry_map = {}

    for entry in chatbot_data:
        for q_lang, question in entry.get("questions", {}).items():
            normalized_question = question.lower()
            question_list[normalized_question] = entry
            entry_map[normalized_question] = q_lang  # Store language of each question

    print(f"User Input: {user_input}")

    if not question_list:
        print("❌ No questions found in the database!")
        return None, 0, "Sorry, no questions are available in the database."

    # ✅ Normalize input
    normalized_input = user_input.lower().strip()

    # ✅ 1. Check for an exact match (in any language)
    if normalized_input in question_list:
        matched_entry = question_list[normalized_input]
        print(f"✅ Exact match found: {normalized_input}")

        # Retrieve the answer in the selected language
        answer = matched_entry["answer"].get(lang, None)

        hasValue = matched_entry["suggestions"].get("hasValue",False)
        reference = {}
        if suggestions["hasValue"] == True:
            reference = matched_entry["suggestions"]
        if answer:
            return normalized_input, 100, answer, reference,hasValue
        else:
            return normalized_input, 100, random.choice(SORRY_MESSAGES.get(lang, SORRY_MESSAGES["en"])), reference,hasValue

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

        # Retrieve the answer in the selected language
        answer = matched_entry["answer"].get(lang, None)

        answer = matched_entry["answer"].get(lang, None)

        hasValue = matched_entry["suggestions"].get("hasValue",False)
        reference = {}
        if suggestions["hasValue"] == True:
            reference = matched_entry["suggestions"]
            
        if answer:
            return best_match, score, answer , reference,hasValue
        else:
            return best_match, score, random.choice(SORRY_MESSAGES.get(lang, SORRY_MESSAGES["en"])), reference,hasValue
    
    else:
        print("❌ Score below threshold. Returning default response.")
        return None, 0, random.choice(SORRY_MESSAGES.get(lang, SORRY_MESSAGES["en"])), reference,hasValue
