"""Quick smoke-test for the improved enhancement pipeline."""
import json
from researcher_service import ResearcherService
from resume_enhancer import ResumeEnhancer

USERNAME = "CODERAKS11"
JD = "Full-Stack Developer with React, Node.js, MongoDB. Experience with REST APIs, Git, and CI/CD. ML/AI experience is a plus."

RESUME = {
    "name": "AMARJEET KUMAR",
    "email": "amarjeetakskumar@gmail.com",
    "phone": "+91-9153899611",
    "linkedin": "linkedin.com/in/amarjeet-kumar-aks1021",
    "github": "github.com/CODERAKS11",
    "summary": "Full-Stack Developer with MERN experience.",
    "education": [{"degree": "B.Tech IT", "institution": "CUSAT", "location": "Kochi"}],
    "experience": [
        {
            "role": "Software Intern",
            "company": "IIT Goa",
            "start_date": "May 2025",
            "end_date": "Jul 2025",
            "location": "Remote",
            "responsibilities": ["Worked on AI and ML projects.", "Built web dashboards."]
        }
    ],
    "projects": [
        {"title": "AI Learning App", "technologies": ["React Native", "Supabase"], "description": "AI-driven quiz platform."},
        {"title": "E-Commerce App", "technologies": ["Angular", "Bootstrap"], "description": "Online storefront."},
    ],
    "skills": ["Python", "React", "Node.js", "MongoDB"],
    "achievements": ["Won national-level coding competition."]
}


def main():
    print("=" * 60)
    print("STEP 1: Deep GitHub Research")
    print("=" * 60)
    rs = ResearcherService()
    gh = rs.discover_github(USERNAME)
    print(f"  Repos scanned:   {gh.get('total_repos_scanned', 0)}")
    print(f"  Noise filtered:  {gh.get('noise_filtered', 0)}")
    print(f"  Worthy projects: {len(gh.get('projects', []))}")
    print(f"  Top skills:")
    for skill, score in gh.get("top_skills", [])[:8]:
        print(f"    {skill:20s}  confidence={score}")

    print("\n" + "=" * 60)
    print("STEP 2: Full Enhancement Flow")
    print("=" * 60)
    enhancer = ResumeEnhancer()
    result = enhancer.enhance_full_flow(RESUME, JD, USERNAME)

    if "error" in result:
        print(f"  ERROR: {result['error']}")
        print(f"  Baseline score: {result.get('original_score')}")
        return

    print(f"  Original ATS:  {result['original_score']}")
    print(f"  Enhanced ATS:  {result['enhanced_score']}")
    print(f"  Delta:         +{result['enhanced_score'] - result['original_score']:.1f}")
    print(f"  Skills added:  {result.get('skills_added', [])}")

    # Check quality: enhanced resume should NOT have more than 4 projects
    projects = result["enhanced_resume"].get("projects", [])
    print(f"\n  Projects in output: {len(projects)}")
    for p in projects:
        title = p.get("title") or p.get("name")
        print(f"    • {title}")

    # Generate PDF
    pdf_path = "test_quality_resume.pdf"
    out = enhancer.generate_pdf(result["enhanced_resume"], pdf_path)
    print(f"\n  PDF generated: {out}")

    print("\n✅ DONE")


if __name__ == "__main__":
    main()
