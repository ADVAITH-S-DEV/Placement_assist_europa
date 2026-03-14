from resume_enhancer import ResumeEnhancer
import json
import os

def test_rich_latex():
    enhancer = ResumeEnhancer()
    
    # Rich data to test multi-column density
    resume = {
        "name": "AMARJEET KUMAR",
        "email": "amarjeetakskumar@gmail.com",
        "phone": "+91-9153899611",
        "linkedin": "https://www.linkedin.com/in/amarjeet-kumar-aks1021",
        "github": "https://github.com/CODERAKS11",
        "summary": "Highly motivated Full Stack Developer Intern with a strong foundation in MERN stack, Angular, and AI/ML technologies. Proven track record of building scalable web applications and AI-driven platforms during internships at IIT Goa and Webstack Academy. Passionate about solving complex problems and delivering high-quality, user-centric solutions.",
        "education": [
            {
                "institution": "Cochin University of Science and Technology",
                "location": "Kochi, Kerala, India",
                "degree": "Bachelor of Technology Information Technology",
                "cgpa": "9.28/10",
                "start_date": "2021",
                "end_date": "2025"
            }
        ],
        "experience": [
            {
                "role": "Angular Developer Intern",
                "company": "IIT GOA",
                "location": "GOA",
                "start_date": "05/2025",
                "end_date": "06/2025",
                "responsibilities": [
                    "Built a secure healthcare platform for patient-therapist interaction using Angular and Node.js.",
                    "Implemented JWT authentication, protected routes, and role-based access control.",
                    "Designed REST APIs and optimized MongoDB queries for efficient medical record handling."
                ]
            }
        ],
        "projects": [
            {
                "title": "Psychometric Insights -- AI based Personality Tests",
                "technologies": ["HuggingFace", "XGBoost", "Flask"],
                "description": "Built an AI-driven platform for SSB aspirants, simulating WAT, SRT, and PPDT tests with instant NLP-based feedback. Implemented HuggingFace Transformers, XGBoost, and Flask REST APIs for response analysis and real-time evaluation."
            }
        ],
        "skills": {
            "languages": ["C", "C++", "JavaScript", "TypeScript", "Python"],
            "frontend": ["React.js", "Angular", "Next.js", "Tailwind CSS"],
            "backend": ["Node.js", "Express.js", "Flask"],
            "databases": ["MongoDB", "MySQL", "Mongoose"],
            "ai_ml": ["HuggingFace Transformers", "XGBoost", "NLP"],
            "tools": ["Git", "Docker", "Postman"]
        },
        "achievements": [
            "Finalist at Morhead -- Cain Global Fellowship, UNC, NC, USA.",
            "Best use of Technology Award in HACK_EUROPA.",
            "UPSC NDA 2 2022 SSB Recommended."
        ],
        "certifications": [
            "Infosys Springboard AI/ML Specialist",
            "CISCO Networking Basics",
            "University of Helsinki 5ECTS (MERN)"
        ]
    }
    
    pdf_path = "rich_professional_resume.pdf"
    print(f"Generating Rich LaTeX-style PDF: {pdf_path}")
    
    try:
        result_path = enhancer.generate_pdf(resume, pdf_path)
        if result_path:
            print(f"✅ Success! PDF saved at: {os.path.abspath(result_path)}")
        else:
            print("❌ PDF generation failed.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_rich_latex()
