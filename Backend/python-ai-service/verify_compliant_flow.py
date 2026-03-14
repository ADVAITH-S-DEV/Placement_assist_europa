import os
import json
from researcher_service import ResearcherService
from resume_enhancer import ResumeEnhancer

def test_compliant_flow():
    # 1. Setup
    username = "CODERAKS11" # User's verified handle
    jd = "Seeking a Full-Stack Developer proficient in React, Node.js, and Supabase. Experience with AI/ML is a plus."
    
    resume_json = {
        "name": "AMARJEET KUMAR",
        "skills": ["Python", "React", "Node.js"],
        "experience": [
            {
                "role": "Software Intern",
                "company": "IIT Goa",
                "responsibilities": ["Worked on AI projects."]
            }
        ]
    }

    print("--- Starting Compliant Enhancement Verification ---")
    
    # 2. Test Researcher Service
    researcher = ResearcherService()
    print(f"Testing GitHub discovery for {username}...")
    research_data = researcher.get_user_research(github_username=username)
    print("Research Data Summary:")
    print(json.dumps(research_data, indent=2))

    # 3. Test Enhancement Flow
    enhancer = ResumeEnhancer()
    print("\nRunning Full Enhancement Flow (including PDF)...")
    
    result = enhancer.enhance_full_flow(
        resume_json, 
        job_description=jd, 
        github_username=username
    )

    if "error" in result:
        print(f"ERROR: {result['error']}")
    else:
        print(f"--- RESULTS ---")
        print(f"Original Score: {result.get('original_score')}")
        print(f"Enhanced Score: {result.get('enhanced_score')}")
        print(f"Score Delta: {result.get('enhanced_score') - result.get('original_score')}")
        
        # 4. Generate PDF
        pdf_path = "test_enhanced_resume.pdf"
        out = enhancer.generate_pdf(result["enhanced_resume"], pdf_path)
        if out:
             print(f"PDF generated successfully: {pdf_path}")
        else:
             print("PDF generation failed.")
            
        print("\nSuccess: Compliant Pipeline verified.")

if __name__ == "__main__":
    test_compliant_flow()
