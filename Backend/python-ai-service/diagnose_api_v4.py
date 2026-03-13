import os
import requests
import base64
import json
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

def diagnose_useresume_v4():
    api_key = os.getenv("USERESUME_API_KEY")
    filename = "test_resume.docx"
    
    if not os.path.exists(filename):
        print(f"Error: {filename} not found")
        return

    url = "https://useresume.ai/api/v3/resume/parse"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    with open(filename, "rb") as f:
        file_bytes = f.read()
    
    encoded_file = base64.b64encode(file_bytes).decode('utf-8')

    print(f"--- Testing with JSON (base64) + 'file' key + parse_to: 'json' ---")
    payload = {
        "file": encoded_file,
        "parse_to": "json"
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=20)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text[:2000]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    diagnose_useresume_v4()
