import json
from ats_scorer import ATSScorer

def test():
    scorer = ATSScorer()
    
    # Load the parsed resume data
    with open("out_final.json", "r", encoding="utf-8") as f:
        # out_final.json has "Status Code: 200" on first line
        lines = f.readlines()
        json_str = "".join(lines[1:])
        resume_data = json.loads(json_str)["data"]

    jd = """
    We are looking for a MERN Stack Developer with experience in React, Node.js, Express, and MongoDB. 
    Knowledge of Angular and TypeScript is a plus. 
    Should have built scalable applications and be able to optimize database queries. 
    We value candidates who have led projects and increased performance by at least 20%.
    Experience with HuggingFace or XGBoost is a bonus.
    """
    
    result = scorer.score(resume_data, jd)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    test()
