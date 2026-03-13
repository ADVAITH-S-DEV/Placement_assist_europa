import json
import os
from resume_analyzer import ResumeAnalyzer

def test_groq_analysis():
    analyzer = ResumeAnalyzer()
    
    # Check if API key is loaded
    if not analyzer.api_key:
        print("Error: GROQ_API_KEY not found in .env")
        return

    # Use a sample file if it exists, or create a mock one
    test_file = "test_resume.docx"
    if not os.path.exists(test_file):
        print(f"Error: {test_file} not found for testing.")
        return

    print(f"Starting analysis for {test_file} using Groq AI...")
    with open(test_file, "rb") as f:
        file_bytes = f.read()
    
    result = analyzer.analyze(file_bytes, test_file)
    
    print("\n--- Analysis Result ---")
    print(json.dumps(result, indent=2))
    
    if "error" in result:
        print(f"\nAnalysis failed with error: {result['error']}")
    else:
        print("\nAnalysis successful! AI suggestions generated.")

if __name__ == "__main__":
    test_groq_analysis()
