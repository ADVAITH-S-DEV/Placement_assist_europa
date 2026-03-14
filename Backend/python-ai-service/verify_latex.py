from resume_enhancer import ResumeEnhancer
import json
import os

def test_latex_look():
    enhancer = ResumeEnhancer()
    
    # Using the exact data from the user's LaTeX request
    resume = {
        "name": "AMARJEET KUMAR",
        "email": "amarjeetakskumar@gmail.com",
        "phone": "+91-9153899611",
        "linkedin": "https://www.linkedin.com/in/amarjeet-kumar-aks1021",
        "github": "https://github.com/CODERAKS11",
        "education": [
            {
                "institution": "Cochin University of Science and Technology",
                "location": "Kochi, Kerala, India",
                "degree": "Bachelor of Technology Information Technology",
                "cgpa": "9.28/10"
            }
        ],
        "experience": [
            {
                "role": "Angular Developer Intern",
                "company": "IIT GOA",
                "location": "GOA",
                "start_date": "05/2025",
                "end_date": "06/2025",
                "responsibilities": []
            },
            {
                "role": "MERN Stack Developer Intern",
                "company": "Webstack Academy",
                "location": "Bangalore",
                "start_date": "05/2024",
                "end_date": "06/2024",
                "responsibilities": []
            }
        ],
        "projects": [
            {
                "title": "Rehab Care -- Healthcare Management System",
                "technologies": ["Angular", "Node.js"],
                "description": "Built a secure healthcare platform for patient-therapist interaction using Angular and Node.js. Implemented JWT authentication, protected routes, and role-based access control."
            }
        ],
        "skills": {
            "languages": ["C", "C++", "JavaScript", "TypeScript", "Python"],
            "frontend_tools": ["React.js", "Angular", "Next.js", "Tailwind CSS"],
            "backend_tools": ["Node.js", "Express.js", "Flask"],
            "databases": ["MongoDB", "MySQL", "Mongoose"]
        },
        "achievements": [
            "Finalist at Morhead -- Cain Global Fellowship, UNC, NC, USA.",
            "Best use of Technology Award in HACK_EUROPA."
        ],
        "certifications": [
            "Infosys Springboard AI/ML Specialist",
            "CISCO Networking Basics"
        ]
    }
    
    pdf_path = "latex_formatted_resume.pdf"
    print(f"Generating LaTeX-style PDF: {pdf_path}")
    
    try:
        result_path = enhancer.generate_pdf(resume, pdf_path)
        if result_path:
            print(f"✅ Success! PDF saved at: {os.path.abspath(result_path)}")
        else:
            print("❌ PDF generation failed.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_latex_look()
