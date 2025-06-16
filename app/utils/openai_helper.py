import requests
import os

def get_new_response(prompt):
    import time
    time.sleep(1.5)  # Delay to prevent 429

    api_key = os.getenv("OPENAI_API_KEY")  # Make sure this is set in your .env
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4.1",
        "input": prompt
    }
    

    response = requests.post("https://api.openai.com/v1/responses", headers=headers, json=data)

    if response.status_code == 200:
        json_data = response.json()
        return json_data['output'][0]['content'][0]['text']
    else:
        return f"⚠️ Chatbot error: {response.status_code}"
