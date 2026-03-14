import requests
import json

def test_parse_jd():
    url = "http://127.0.0.1:8000/parse-jd"
    raw_text = """Description

Overview:

Guidepoints Engineering team thrives on problem-solving and creating happier users. As Guidepoint works to achieve its mission of making individuals, businesses, and the world smarter through personalized knowledge-sharing solutions, the engineering team is taking on challenges to improve our internal CRM system and externally facing Portals to optimize the seamless delivery of our services.

As a Frontend Engineer Intern, youll work with a team of engineers through challenging development projects. Come join a highly collaborative team of skilled engineers with a passion for quality.

What You ll Do:

Work in an agile environment completing User Stories authored by professional Product Managers. Along with high-fidelity comps and annotations by a team of in-house Designers
Collaborate on implementations with .NET team members (in addition to other Frontend Engineers) through projects in React applications
Work with QA and Application Support teams to triage bugs
Work with DevOps to automate the build, deployment and distribution of SPAs and static assets
Consume Restful APIs, JSON payloads, and various payload contexts
Build new Portals/Applications with React, while making incremental enhancements to monolithic legacy applications (server-side rendered)
Write Unit tests and documentation.
What You Have:

0-1 years professional experience as an individual contributor.
Prior experience working with organized development teams
Either SME on React & ES6 or pixel-perfect HTML/CSS/JS w/UX, or both!
Experience with JavaScript ES6+, Typescript, SCSS
Understand branching, merging, pull requests and conflict resolution in Git (Bitbucket or GitHub)
Experience in Unit testing (jest)
About Guidepoint:

Guidepoint is a leading research enablement platform designed to advance understanding and empower our clients decision-making process. Powered by innovative technology, real-time data, and hard-to-source expertise, we help our clients to turn answers into action.

Backed by a network of nearly 1.75 million experts and Guidepoint s 1,600 employees worldwide, we inform leading organizations research by delivering on-demand intelligence and research on request. With Guidepoint, companies and investors can better navigate the abundance of information available today, making it both more useful and more powerful.

At Guidepoint, our success relies on the diversity of our employees, advisors, and client base, which allows us to create connections that offer a wealth of perspectives. We are committed to upholding policies that contribute to an equitable and welcoming environment for our community, regardless of background, identity, or experience.

#LI-AD2

#LI-HYBRID


Role: Front End Developer
Industry Type: Accounting / Auditing
Department: Engineering - Software & QA
Employment Type: Full Time, Permanent
Role Category: Software Development
Education
UG: Any Graduate
PG: Any Postgraduate
Key Skills
Application supportgithubGITFront endConflict resolutionAgileHTMLJSONUnit testingCRM"""

    payload = raw_text
    try:
        response = requests.post(url, data=payload, headers={"Content-Type": "text/plain"})
        with open("parse_jd_result.json", "w") as f:
            json.dump(response.json(), f, indent=2)
        print("Result saved to parse_jd_result.json")
    except Exception as e:
        print("Error connecting to server:", e)

if __name__ == "__main__":
    test_parse_jd()
