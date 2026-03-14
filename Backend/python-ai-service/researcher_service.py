import os
import re
import json
import base64
import requests
from typing import List, Dict, Any

# Repos with these names are almost always tutorials/clones, not original work
NOISE_REPO_PATTERNS = [
    r"^hello[-_]?world",
    r"^todo[-_]?list",
    r"^js[-_]hindi",
    r"^fullstackopen[-_]?practice",
    r"^angular$",           # bare framework name = learning repo
    r"^studio$",
    r"^movie[-_]review",
    r"test[-_]?project",
]

# npm packages that are just tooling noise, not resume-worthy skills
DEP_NOISE = {
    "nodemon", "eslint", "prettier", "husky", "lint-staged",
    "concurrently", "cross-env", "dotenv", "morgan", "debug",
    "rimraf", "chalk", "commander", "yargs", "npm-run-all",
}


class ResearcherService:
    """
    Deep, noise-filtered analysis of GitHub repos + LinkedIn paste.
    Only surfaces evidence that is resume-worthy.
    """

    def __init__(self):
        self.github_api = "https://api.github.com"
        self.token = os.getenv("GITHUB_TOKEN")
        self.confidence = {"dependency": 5, "language": 3, "readme": 2, "topic": 4}

    # ─── helpers ──────────────────────────────────────────────

    def _headers(self) -> dict:
        h = {"Accept": "application/vnd.github.v3+json"}
        if self.token:
            h["Authorization"] = f"token {self.token}"
        return h

    @staticmethod
    def _is_noise_repo(repo: dict) -> bool:
        """Filter out forks, trivial repos, and known tutorial patterns."""
        if repo.get("fork"):
            return True
        name = repo["name"].lower()
        if any(re.match(p, name) for p in NOISE_REPO_PATTERNS):
            return True
        # Very small repos with no description are likely throwaway
        if repo.get("size", 0) < 5 and not repo.get("description"):
            return True
        return False

    def _fetch_file(self, owner: str, repo: str, path: str) -> str | None:
        """Return decoded UTF-8 content of a file, or None."""
        url = f"{self.github_api}/repos/{owner}/{repo}/contents/{path}"
        r = requests.get(url, headers=self._headers())
        if r.status_code != 200:
            return None
        try:
            return base64.b64decode(r.json()["content"]).decode("utf-8")
        except Exception:
            return None

    @staticmethod
    def _extract_deps(text: str, file_type: str) -> List[str]:
        """Parse dependency file text into a list of library names."""
        deps = []
        try:
            if file_type == "package.json":
                data = json.loads(text)
                combined = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                deps = [k for k in combined if k.lower() not in DEP_NOISE]
            elif file_type == "requirements.txt":
                for line in text.splitlines():
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    pkg = re.split(r"[><=!~;]", line)[0].strip()
                    if pkg.lower() not in DEP_NOISE and len(pkg) > 1:
                        deps.append(pkg)
        except Exception:
            pass
        return deps

    @staticmethod
    def _extract_readme_skills(readme: str) -> List[str]:
        """Pull tech keywords from README markdown."""
        # Look for common patterns: "Built with X", badges, tech-stack sections
        found = set()
        # Markdown badges  e.g.  ![React](…)
        for m in re.finditer(r"!\[([A-Za-z][A-Za-z0-9. +-]+)\]", readme):
            found.add(m.group(1).strip())
        # Headings like  ## Tech Stack   followed by bullet lists
        tech_section = re.search(
            r"(?:tech|stack|built with|technologies|tools)[^\n]*\n((?:[-*]\s+.+\n?)+)",
            readme, re.I,
        )
        if tech_section:
            for line in tech_section.group(1).splitlines():
                item = re.sub(r"^[-*]\s+", "", line).strip()
                if 1 < len(item) < 40:
                    found.add(item)
        return list(found)

    def _bump(self, scores: dict, skill: str, kind: str):
        skill = skill.lower().strip()
        if not skill or len(skill) < 2:
            return
        scores[skill] = scores.get(skill, 0) + self.confidence.get(kind, 1)

    # ─── main entry ───────────────────────────────────────────

    def discover_github(self, username: str) -> Dict[str, Any]:
        """
        Deep, noise-filtered GitHub analysis.
        Returns only resume-worthy projects + skills with confidence scores.
        """
        if not username:
            return {}

        url = f"{self.github_api}/users/{username}/repos?sort=pushed&per_page=30"
        r = requests.get(url, headers=self._headers())
        if r.status_code != 200:
            return {"error": f"GitHub user '{username}' not found"}

        all_repos = r.json()
        skills: Dict[str, int] = {}
        worthy_projects: List[dict] = []

        for repo in all_repos:
            if self._is_noise_repo(repo):
                continue

            name = repo["name"]
            lang = repo.get("language")
            topics = repo.get("topics", [])
            stars = repo.get("stargazers_count", 0)
            desc = repo.get("description") or ""

            # ── skill scoring ──
            if lang:
                self._bump(skills, lang, "language")
            for t in topics:
                self._bump(skills, t, "topic")

            # ── dependency parsing ──
            for dep_file in ("package.json", "requirements.txt", "pom.xml"):
                content = self._fetch_file(username, name, dep_file)
                if content:
                    for dep in self._extract_deps(content, dep_file):
                        self._bump(skills, dep, "dependency")

            # ── README analysis ──
            readme = self._fetch_file(username, name, "README.md")
            readme_summary = ""
            if readme:
                for s in self._extract_readme_skills(readme):
                    self._bump(skills, s, "readme")
                # Keep first 600 chars as a summary for the LLM
                readme_summary = readme[:600].strip()

            worthy_projects.append({
                "name": name,
                "description": desc,
                "language": lang or "",
                "topics": topics,
                "stars": stars,
                "readme_summary": readme_summary,
            })

        # Sort skills by confidence, keep top 15
        top_skills = sorted(skills.items(), key=lambda x: x[1], reverse=True)[:15]

        # Sort projects by stars then by pushed date (already sorted by API)
        worthy_projects.sort(key=lambda p: p["stars"], reverse=True)

        return {
            "username": username,
            "total_repos_scanned": len(all_repos),
            "noise_filtered": len(all_repos) - len(worthy_projects),
            "top_skills": top_skills,
            "projects": worthy_projects[:6],  # top 6 most relevant
        }

    def parse_linkedin(self, text: str) -> Dict[str, Any]:
        """
        Parse user-pasted LinkedIn profile text into structured sections.
        Uses regex heuristics to find experience, education, and skills.
        """
        if not text or len(text.strip()) < 20:
            return {}

        result: Dict[str, Any] = {}
        text = text[:8000]  # safety cap

        # ── headline ──
        lines = text.strip().splitlines()
        if lines:
            result["headline"] = lines[0].strip()

        # ── experience entries ──
        exp_pattern = re.compile(
            r"(?P<title>[A-Z][^\n]{5,60})\n"
            r"(?P<company>[A-Z][^\n]{2,60})\s*[·•|]\s*"
            r"(?P<duration>[^\n]{5,40})",
            re.M,
        )
        experiences = []
        for m in exp_pattern.finditer(text):
            experiences.append({
                "title": m.group("title").strip(),
                "company": m.group("company").strip(),
                "duration": m.group("duration").strip(),
            })
        if experiences:
            result["experience"] = experiences

        # ── skills ──
        skills_section = re.search(r"(?:Skills|Top Skills)[:\s]*\n((?:.+\n?)+)", text, re.I)
        if skills_section:
            raw = skills_section.group(1)
            skill_list = [s.strip() for s in re.split(r"[•·,\n]", raw) if 1 < len(s.strip()) < 40]
            result["skills"] = skill_list[:20]

        # ── certifications ──
        cert_section = re.search(r"(?:Certifications?|Licenses?)[:\s]*\n((?:.+\n?)+)", text, re.I)
        if cert_section:
            certs = [c.strip() for c in cert_section.group(1).splitlines() if len(c.strip()) > 3]
            result["certifications"] = certs[:10]

        return result

    def get_user_research(self, github_username: str = "", linkedin_text: str = "") -> dict:
        """Single entry point for all discovery."""
        return {
            "github": self.discover_github(github_username) if github_username else {},
            "linkedin": self.parse_linkedin(linkedin_text) if linkedin_text else {},
        }
