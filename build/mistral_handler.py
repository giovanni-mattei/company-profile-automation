import os
import requests
from dotenv import load_dotenv

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_API_URL = os.getenv("MISTRAL_API_URL", "https://api.mistral.ai/v1/chat/completions")

def call_mistral(messages, model="mistral-tiny", temperature=0.1, max_tokens=100):
    if not messages or not isinstance(messages, list):
        return "Error: 'messages' must be a non-empty list."
    if not MISTRAL_API_KEY:
        return "Error: Mistral API key not configured."

    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens}

    try:
        response = requests.post(MISTRAL_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        response_json = response.json()
        if "choices" not in response_json or not response_json["choices"]:
            return "Error: Invalid API response format."
        return response_json["choices"][0]["message"]["content"].strip()
    except requests.exceptions.RequestException as e:
        return f"Network error: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"