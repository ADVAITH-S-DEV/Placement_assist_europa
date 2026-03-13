import os
import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

def diagnose_useresume():
    api_key = os.getenv("USERESUME_API_KEY")
    filename = "test_resume.docx"
    
    if not os.path.exists(filename):
        print(f"Error: {filename} not found")
        return

    url = "https://useresume.ai/api/v3/resume/parse"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    with open(filename, "rb") as f:
        file_bytes = f.read()

    print(f"--- Testing with key 'file' ---")
    try:
        files = {"file": (filename, file_bytes)}
        r = requests.post(url, headers=headers, files=files, timeout=20)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text[:500]}")
    except Exception as e:
        print(f"Error: {e}")

    print(f"\n--- Testing with key 'resume' ---")
    try:
        files = {"resume": (filename, file_bytes)}
        r = requests.post(url, headers=headers, files=files, timeout=20)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text[:500]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    diagnose_useresume()
