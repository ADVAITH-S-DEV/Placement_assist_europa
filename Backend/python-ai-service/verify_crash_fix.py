import json
from ats_scorer import ATSScorer

def test_user_json_crash():
    scorer = ATSScorer()
    
    # Mimic the user's problematic JSON structure
    resume_json = {
        "name": "AMARJEET KUMAR",
        "skills": [
            {"name": "C", "proficiency": "Advanced"},
            {"name": "JavaScript", "proficiency": "Advanced"}
        ],
        "experience": [
            {
                "title": "Angular Developer Intern",
                "company": "IIT GOA",
                "responsibilities": [
                    {"text": "Built a secure healthcare platform"}
                ]
            }
        ],
        "education": [
            {"degree": "B.Tech", "institution": "CUSAT"}
        ]
    }
    
    jd = "Angular Developer with JavaScript skills."
    
    print("Testing for crashes...")
    try:
        result = scorer.score(resume_json, jd)
        print("PASS: Score generated successfully!")
        print(f"Score: {result['ats_score']}")
        print(f"Matched Skills: {result['matched_skills']}")
    except Exception as e:
        print(f"FAIL: Crashed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_user_json_crash()
