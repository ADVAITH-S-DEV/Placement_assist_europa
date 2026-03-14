from resume_enhancer import ResumeEnhancer
import json
import os

def test_enhancement_quality():
    enhancer = ResumeEnhancer()
    
    # Tiny resume with missing content
    resume = {
        "name": "Amarjeet Kumar",
        "email": "amarjeetakskumar@gmail.com",
        "experience": [
            {
                "role": "Intern",
                "company": "Tech Corp",
                "responsibilities": ["Wrote code", "Fixed bugs"]
            }
        ],
        "projects": [
            {
                "title": "Placement Assist",
                "description": "" # EMPTY
            }
        ],
        "skills": ["Python", "JS"],
        "certifications": []
    }
    
    jd = "We need a Full Stack Developer with experience in React, Python, and AWS."
    
    # Simulate research finding AWS and React in GitHub
    research = {
        "github": {
            "projects": [
                {
                    "name": "Placement-Assist",
                    "description": "A comprehensive ATS-optimized resume builder built with React and Python FastAPI.",
                    "topics": ["react", "fastapi", "python"],
                    "languages": ["Python", "JavaScript"]
                }
            ],
            "top_skills": ["Python", "React", "FastAPI"]
        },
        "linkedin": {}
    }
    
    missing = ["React", "AWS"]
    matched = ["Python"]
    
    print("Generating enhanced resume...")
    prompt = enhancer._build_prompt(resume, jd, missing, matched, research)
    
    try:
        resp = enhancer.client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a professional resume writer. Output JSON only."},
                {"role": "user", "content": prompt},
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
        )
        enhanced = json.loads(resp.choices[0].message.content)
        
        # Validation checks
        issues = []
        if not enhanced.get("projects")[0].get("description"):
            issues.append("Project description is still empty!")
        
        skills = enhanced.get("skills")
        if not isinstance(skills, dict):
            issues.append(f"Skills is not a dict! Got: {type(skills)}")
        else:
            if not any(skills.values()):
                issues.append("Skills categories are empty!")
        
        if not isinstance(enhanced.get("certifications"), list):
            issues.append(f"Certifications is not a list! Got: {type(enhanced.get('certifications'))}")

        if issues:
            print("QUALITY ISSUES FOUND:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("QUALITY CHECKS PASSED!")
            
        print("\nENHANCED JSON PREVIEW:")
        print(json.dumps(enhanced, indent=2))
        
        # Test PDF generation
        pdf_path = "test_enhanced_quality.pdf"
        enhancer.generate_pdf(enhanced, pdf_path)
        print(f"\nPDF generated at: {os.path.abspath(pdf_path)}")

    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_enhancement_quality()
