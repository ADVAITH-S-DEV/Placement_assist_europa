import os
import json
from resume_parser import ResumeParser
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

def test_useresume_integration():
    parser = ResumeParser()
    api_key = os.getenv("USERESUME_API_KEY")
    
    if not api_key:
        print("Error: USERESUME_API_KEY not found in .env")
        return

    test_file = "test_resume.docx"
    if not os.path.exists(test_file):
        print(f"Error: {test_file} not found for testing.")
        return

    print(f"Testing UseResume AI Integration for {test_file}...")
    with open(test_file, "rb") as f:
        file_bytes = f.read()
    
    # This should trigger parse_external since USERESUME_API_KEY is present
    result = parser.parse(file_bytes, test_file)
    
    print("\n--- Parsed Result Summary ---")
    print(f"Name: {result.get('name')}")
    print(f"Email: {result.get('email')}")
    print(f"Phone: {result.get('phone')}")
    print(f"Source: {result.get('meta', {}).get('parser')}")
    
    # Check sections
    for section in ["education", "experience", "skills"]:
        count = len(result.get(section, []))
        print(f"{section.capitalize()} count: {count}")

    if "error" in result:
        print(f"\nIntegration failed with error: {result['error']}")
    else:
        print("\nIntegration successful! UseResume AI is now the primary parser.")

if __name__ == "__main__":
    test_useresume_integration()
