import os
from dotenv import load_dotenv

# Path to the .env file in the Backend directory
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(env_path)

key = os.getenv("USERESUME_API_KEY")
if key:
    print(f"PASS: USERESUME_API_KEY is found (starting with {key[:10]}...)")
else:
    print("FAIL: USERESUME_API_KEY is NOT found")
