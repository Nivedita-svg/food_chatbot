import re

def extract_session_id(session_str: str) -> str:
    match = re.search(r"/sessions/(.*?)/contexts/", session_str)
    if match:
        extracted_string = match.group(1)
        return extracted_string
    return ""

def get_str_from_food_dict(food_dict: dict) -> str:
    result = ", ".join([f"{int(value)} {key}" for key, value in food_dict.items()])
    return result

if __name__ == "__main__":
    print(get_str_from_food_dict({"samosa": 2, "chole": 5}))
    # Uncomment the line below to test the extract_session_id function
    # print(extract_session_id("projects/chatbot-for-food-delivery-rdan/agent/sessions/0989a65a-c193-13e8-8c70-022390191cba/contexts/ongoing-tracking"))
