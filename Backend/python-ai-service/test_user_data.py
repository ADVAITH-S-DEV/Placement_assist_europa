import json
from ats_scorer import ATSScorer

resume_json = {
    "name": "AMARJEET KUMAR",
    "email": "amarjeetakskumar@gmail.com",
    "phone": "+91-9153899611",
    "linkedin": "",
    "github": "",
    "location": "",
    "education": [
        {
            "institution": "Cochin University of Science and Technology Kochi",
            "location": "Kerala, India",
            "cgpa": "9.28",
            "degree": "Bachelor of Technology Information Technology"
        }
    ],
    "experience": [
        {
            "role": "Angular Developer Intern",
            "company": "IIT GOA, GOA",
            "location": "",
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
            "title": "Rehab Care – Healthcare Management System",
            "organization": "IIT Goa Internship Project",
            "technologies": [
                "Angular",
                "Node.js"
            ],
            "description": [
                "Built a secure healthcare platform for patient-therapist interaction using Angular and Node.js.",
                "Implemented JWT authentication, protected routes, and role-based access control.",
                "Designed REST APIs and optimized MongoDB queries for efficient medical record handling."
            ]
        },
        {
            "title": "Food Order App – Real-Time MERN Application",
            "organization": "Webstack Academy Internship Project",
            "technologies": [
                "MERN",
                "WebSockets"
            ],
            "description": [
                "Developed a scalable food ordering system with real-time tracking using WebSockets and MongoDB change streams.",
                "Implemented secure authentication and Stripe payment gateway integration.",
                "Built responsive UI with optimized performance across devices."
            ]
        },
        {
            "title": "Psychometric Insights – AI based Personality Tests",
            "organization": "Code reCET 2.0",
            "technologies": [
                "HuggingFace",
                "XGBoost",
                "Flask"
            ],
            "description": [
                "Built an AI-driven platform for SSB aspirants, simulating WAT, SRT, and PPDT tests with instant NLP-based feedback.",
                "Implemented HuggingFace Transformers, XGBoost, and Flask REST APIs for response analysis and real-time evaluation."
            ]
        }
    ],
    "skills": {
        "languages": [
            "C",
            "C++",
            "JavaScript",
            "TypeScript",
            "Python"
        ],
        "frontend": [
            "React.js",
            "Angular",
            "Next.js",
            "Tailwind CSS"
        ],
        "backend": [
            "Node.js",
            "Express.js",
            "Flask"
        ],
        "databases": [
            "MongoDB",
            "MySQL",
            "Mongoose"
        ],
        "ai_ml": [
            "HuggingFace Transformers",
            "XGBoost",
            "NLP"
        ]
    }
}

job_description = """
Position: Web Developer Intern
Department: Technology / Engineering
Key Responsibilities:
Assist in developing and maintaining web applications and websites.
Write clean, efficient, and well-documented code.
Support the team in front-end development using HTML, CSS, and JavaScript.
Work with frameworks/libraries such as React, Angular, or similar (if applicable).
Help in debugging, testing, and optimizing web applications.
Collaborate with designers and senior developers to implement UI/UX improvements.
Participate in code reviews and team meetings.
Required Skills & Qualifications:
Basic knowledge of HTML, CSS, and JavaScript.
Familiarity with any modern front-end framework (e.g., React, Angular, Vue) is a plus.
Understanding of responsive design principles.
Basic knowledge of version control tools such as Git.
Good problem-solving and communication skills.
Currently pursuing or recently completed a degree in Computer Science, IT, or a related field.
Preferred Skills (Optional):
Basic understanding of REST APIs.
Exposure to backend technologies (Node.js, Python, or similar).
Familiarity with databases such as MySQL or MongoDB.
"""

scorer = ATSScorer()
result = scorer.score(resume_json, job_description)

print(json.dumps(result, indent=2))
