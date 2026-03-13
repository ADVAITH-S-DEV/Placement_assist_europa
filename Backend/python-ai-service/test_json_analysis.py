import json
import requests

def test_json_analysis():
    url = "http://localhost:8000/analyze-from-json"
    
    # User's sample data structure
    resume_json = {
        "success": True,
        "data": {
            "name": "AMARJEET KUMAR",
            "summary": "Experienced Full-Stack Developer with expertise in MERN Stack...",
            "skills": [
                {"name": "React.js", "proficiency": "Advanced"},
                {"name": "Node.js", "proficiency": "Advanced"}
            ],
            "experience": [
                {
                    "title": "Angular Developer Intern",
                    "company": "IIT GOA",
                    "responsibilities": [
                        {"text": "Built a secure healthcare platform"}
                    ]
                }
            ]
        }
    }
    
    payload = {
        "resume_json": resume_json,
        "job_description": "We are looking for a Senior Full Stack Developer proficient in React, Node.js, and Cloud Infrastructure."
    }
    
    print("Sending JSON for analysis...")
    try:
        r = requests.post(url, json=payload, timeout=30)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            result = r.json()
            print("\n--- AI Suggestion 1 ---")
            if result.get("success") and result["data"].get("suggestions"):
                print(result["data"]["suggestions"][0])
            print("\n--- Action-Result Rewrite Sample ---")
            if result["data"].get("action_result_rewrites"):
                print(f"Original: {result['data']['action_result_rewrites'][0]['original']}")
                print(f"Improved: {result['data']['action_result_rewrites'][0]['improved']}")
        else:
            print(f"Error: {r.text}")
    except Exception as e:
        print(f"Failed to connect: {e}")

if __name__ == "__main__":
    test_json_analysis()
