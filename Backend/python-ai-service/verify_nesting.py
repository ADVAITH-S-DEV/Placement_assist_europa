import json
from ats_scorer import ATSScorer

# Simulating the nested structure the user sent
wrapped_resume_json = {
    "success": True,
    "data": {
        "name": "AMARJEET KUMAR",
        "email": "amarjeetakskumar@gmail.com",
        "education": [
            {
                "institution": "Cochin University of Science and Technology Kochi",
                "degree": "Bachelor of Technology Information Technology"
            }
        ],
        "experience": [
            {
                "role": "Angular Developer Intern",
                "company": "IIT GOA, GOA"
            }
        ],
        "skills": {
            "languages": ["JavaScript", "Python"],
            "frontend": ["React.js", "Angular"]
        }
    }
}

# The endpoint now unwraps this
if wrapped_resume_json.get("success") and "data" in wrapped_resume_json:
    actual_resume = wrapped_resume_json["data"]
else:
    actual_resume = wrapped_resume_json

jd = "Looking for an Angular and Python developer."

scorer = ATSScorer()
result = scorer.score(actual_resume, jd)
print(f"ATS Score after fix: {result['ats_score']}")
print(f"Sections processed: {result['breakdown']['section_completeness']}")
