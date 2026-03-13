"""
ats_scorer.py — Advanced ATS scoring engine with Explainable AI (XAI).
Scores a parsed resume JSON against a job description with semantic intelligence and hyper-specific feedback.
"""

import re
from typing import Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Common action verbs for ATS
ACTION_VERBS = {
    "built", "developed", "optimized", "led", "managed", "implemented", "designed",
    "created", "researched", "solved", "collaborated", "facilitated", "mentored",
    "coordinated", "executed", "accelerated", "accomplished", "achieved", "adapted",
    "administered", "advanced", "advised", "allocated", "analyzed", "appraised",
    "arranged", "assembled", "assessed", "assigned", "assisted", "attained",
    "audited", "authored", "automated", "awarded", "balanced", "bargained",
    "benchmarked", "budgeted", "calculated", "cataloged", "centralized", "certified",
    "chaired", "changed", "charted", "checked", "classified", "cleared", "closed",
    "coached", "combined", "communicated", "compared", "compiled", "completed",
    "composed", "computed", "conceived", "conducted", "configured", "consolidated",
    "constructed", "consulted", "contained", "contracted", "contributed", "controlled",
    "converted", "convinced", "corrected", "counseled", "critiqued", "customized",
    "debugged", "decided", "defined", "delegated", "delivered", "demonstrated",
    "depicted", "deployed", "derived", "detailed", "detected", "determined",
    "documented", "drafted", "drove", "edited", "educated", "effected", "elicited",
    "eliminated", "emulated", "enabled", "enacted", "encouraged", "engineered",
    "enhanced", "enlarged", "enlisted", "ensured", "enumerated", "envisioned",
    "established", "estimated", "evaluated", "examined", "exceeded", "exhibited",
    "expanded", "expedited", "experimented", "explained", "explored", "expressed",
    "extended", "extracted", "fabricated", "fashioned", "forecasted", "formed",
    "formulated", "fostered", "founded", "framed", "fulfilled", "furthered",
    "gathered", "generated", "governed", "guided", "halted", "handled", "hired",
    "identified", "illustrated", "improved", "incorporated", "increased", "indexed",
    "induced", "influenced", "informed", "initiated", "innovated", "inspected",
    "inspired", "installed", "instituted", "instructed", "insured", "integrated",
    "intended", "intensified", "interpreted", "intervened", "interviewed", "introduced",
    "invented", "investigated", "involved", "isolated", "issued", "joined", "judged",
    "launched", "learned", "lectured", "lessened", "liquated", "listened", "located",
    "logged", "lower", "maintained", "mapped", "marginalized", "marketed", "mastered",
    "maximized", "measured", "mediated", "merged", "minimized", "modeled", "modified",
    "monitored", "motivated", "navigated", "negotiated", "noticed", "nurtured",
    "observed", "obtained", "offered", "offset", "opened", "operated", "ordered",
    "organized", "oriented", "originated", "outlined", "overcame", "overhauled",
    "oversaw", "participated", "perceived", "perfected", "performed", "persuaded",
    "pioneered", "placed", "planned", "positioned", "predicted", "prepared",
    "prescribed", "presented", "presided", "prevented", "printed", "prioritized",
    "processed", "produced", "programmed", "projected", "promoted", "proofread",
    "proposed", "protected", "proved", "provided", "publicized", "published",
    "purchased", "qualified", "quantified", "questioned", "raised", "ranked",
    "rated", "reached", "realized", "reasoned", "received", "recognized",
    "recommended", "reconciled", "recorded", "recruited", "rectified", "redesign",
    "reduced", "referred", "refined", "regained", "regulated", "rehabilitated",
    "reinforced", "reinstated", "rejected", "related", "released", "relieved",
    "remanufactured", "rendered", "renewed", "renovated", "reorganized", "repaired",
    "replaced", "replenished", "reported", "represented", "requested", "required",
    "researched", "reserved", "resolved", "responded", "restored", "restructured",
    "resulted", "retained", "retrieved", "revamped", "revealed", "reversed",
    "reviewed", "revised", "revitalized", "rewarded", "routed", "safeguarded",
    "salvaged", "satisfied", "saved", "scanned", "scheduled", "schooled",
    "screened", "searched", "secured", "selected", "separated", "served",
    "serviced", "settled", "shaped", "shared", "showed", "simplified", "simulated",
    "sketched", "skilled", "smoothed", "solidified", "sorted", "spearheaded",
    "specialized", "specified", "stimulated", "strategized", "streamlined",
    "strengthened", "stressed", "stretched", "structured", "studied", "submitted",
    "substantiated", "substituted", "suggested", "summarized", "supervised",
    "supplied", "supported", "surpassed", "surveyed", "sustained", "synthesized",
    "systematized", "tabulated", "tailored", "targeted", "taught", "teamed",
    "technical", "tested", "testified", "tightened", "tolerated", "totaled",
    "traced", "tracked", "traded", "trained", "transcribed", "transformed",
    "translated", "transmitted", "transported", "traversed", "treated", "tripled",
    "troubleshot", "tutored", "uncovered", "undertook", "unified", "unite",
    "updated", "upgraded", "urged", "used", "utilized", "validated", "valued",
    "verified", "viewed", "visited", "vitalized", "volunteered", "warned",
    "warranted", "watched", "weakened", "weighed", "widened", "witnessed",
    "worked", "wrote", "yielded"
}

# Tech synonyms dictionary for semantic matching & whitelist
TECH_SYNONYMS = {
    "nodejs": ["node.js", "node js", "node"],
    "reactjs": ["react.js", "react js", "react"],
    "angularjs": ["angular.js", "angular js", "angular"],
    "vuejs": ["vue.js", "vue js", "vue"],
    "mongodb": ["mongo db", "mongo"],
    "postgresql": ["postgre", "postgres", "psql"],
    "typescript": ["ts"],
    "javascript": ["js"],
    "aws": ["amazon web services", "amazon"],
    "gcp": ["google cloud platform", "google cloud"],
    "azure": ["microsoft azure"],
    "machine learning": ["ml"],
    "artificial intelligence": ["ai"],
    "natural language processing": ["nlp"],
    "html": ["html5"],
    "css": ["css3", "tailwind", "sass", "less"],
    "sql": ["mysql", "nosql", "sql server", "sqlite"],
    "git": ["github", "gitlab", "version control"],
    "docker": ["kubernetes", "k8s", "containerization"],
    "rest": ["restful", "apis", "api"],
    "cicd": ["jenkins", "ci/cd", "deployment"],
    "agile": ["scrum", "kanban"],
    "python": ["py"],
    "java": ["spring"],
    "php": ["laravel"],
    "mern": ["mongodb", "express", "react", "node"],
    "huggingface": ["hugging face", "transformers"],
}

# Words to ignore when extracting "potential" skills from JD
SKILL_NOISE = {
    "required", "preferred", "knowledge", "experience", "excellent", "good", "strong",
    "understanding", "basics", "advanced", "position", "engineering", "department",
    "description", "skills", "responsibilities", "qualifications", "developer", "engineer",
    "support", "participate", "intern", "it", "ui", "currently", "optional", "help",
    "assist", "collaborate", "familiarity", "key", "work", "write", "computer", "web",
    "technology", "science", "exposure", "plus", "bonus", "interested", "apply", "send",
    "email", "within", "team", "growth", "high", "impact", "successful", "candidate",
    "ability", "years", "highly", "etc", "using", "through", "using", "into", "highly",
    "both", "well", "such", "including", "across", "other", "various", "multiple",
    "should", "we", "stack", "value", "at least", "be able", "built", "looking", "for"
}

DEGREE_LEVELS = {
    "phd": 5,
    "doctorate": 5,
    "masters": 4,
    "master": 4,
    "mtech": 4,
    "mba": 4,
    "mcs": 4,
    "bachelors": 3,
    "bachelor": 3,
    "btech": 3,
    "be": 3,
    "bs": 3,
    "diploma": 2,
    "high school": 1
}

class ATSScorer:
    """Advanced ATS scoring engine with Hyper-Specific Detailed Review."""

    def score(self, resume_json: dict[str, Any], job_description: str) -> dict[str, Any]:
        """
        Calculate enhanced ATS score and provide hyper-specific, explainable feedback.
        """
        if not job_description:
            return {
                "ats_score": 0,
                "detailed_review": ["Job description is missing. Please provide one for a full analysis."],
                "breakdown": {
                    "skills_match": 0,
                    "keyword_density": 0,
                    "quantified_achievements": 0,
                    "section_completeness": 0,
                    "action_verbs": 0,
                    "role_relevance": 0,
                    "education_alignment": 0
                }
            }

        # 1. Semantic Skills Match (0-25)
        skills_score, matched_skills, missing_skills = self._calculate_semantic_skills_match(resume_json, job_description)

        # 2. Keyword Density & Recency (0-15)
        density_score = self._calculate_keyword_density(resume_json, job_description)

        # 3. Quantified Achievements (0-15)
        quant_info = self._calculate_quantified_achievements(resume_json)
        quant_score = quant_info["score"]

        # 4. Section Completeness (0-10)
        completeness_info = self._calculate_section_completeness(resume_json)
        completeness_score = completeness_info["score"]

        # 5. Action Verbs & Sentence Quality (0-15)
        verbs_score, verbs_found, sentence_quality = self._calculate_action_verbs_and_quality(resume_json)

        # 6. Role Relevance (0-10)
        relevance_score, role_feedback = self._calculate_role_relevance(resume_json, job_description)

        # 7. Education Alignment (0-10)
        edu_score, edu_feedback = self._calculate_education_alignment(resume_json, job_description)

        total_score = skills_score + density_score + quant_score + completeness_score + verbs_score + relevance_score + edu_score
        
        # Generate Hyper-Specific Review
        detailed_review = self._generate_hyper_specific_review(
            resume_json=resume_json,
            jd=job_description,
            skills_info={"matched": matched_skills, "missing": missing_skills, "score": skills_score},
            quant_info=quant_info,
            verbs_info={"found": verbs_found, "score": verbs_score, "quality": sentence_quality},
            relevance_info={"score": relevance_score, "feedback": role_feedback},
            edu_info={"score": edu_score, "feedback": edu_feedback},
            completeness_info={"missing": completeness_info["missing"]}
        )

        return {
            "ats_score": round(total_score, 1),
            "breakdown": {
                "skills_match": round(skills_score, 1),
                "keyword_density": round(density_score, 1),
                "quantified_achievements": round(quant_score, 1),
                "section_completeness": round(completeness_score, 1),
                "action_verbs": round(verbs_score, 1),
                "role_relevance": round(relevance_score, 1),
                "education_alignment": round(edu_score, 1)
            },
            "detailed_review": detailed_review,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "methodology": {
                "skills_matching": "Analyzes the Job Description for technical keywords and searches your profile using a semantic synonym dictionary (e.g., 'Node.js' matches 'Node').",
                "impact_analysis": "Scans your work history for numbers, percentages ($10k, 15%), and scales (1k+ users) to determine if your achievements are measurable.",
                "recency_weighting": "Assigns 3x more importance to skills and keywords found in your most recent experience entry.",
                "relevance_audit": "Compares your past job titles against the target role title in the JD (e.g., matching 'Angular Developer' to 'Web Developer')."
            }
        }

    def _generate_hyper_specific_review(self, resume_json, jd, skills_info, quant_info, verbs_info, relevance_info, edu_info, completeness_info) -> list[str]:
        """Generate human-like, hyper-specific feedback with specific examples."""
        review = []
        
        # 1. Technical Gap Audit
        if skills_info["missing"]:
            for skill in skills_info["missing"][:3]:
                # Find context in JD
                pattern = re.compile(rf'[^.]*?{re.escape(skill)}[^.]*?\.', re.I)
                match = pattern.search(jd)
                context = match.group(0).strip() if match else f"The JD requires {skill}."
                review.append(f"MISSING SKILL: Found '{skill}' in JD context: \"{context}\". Your resume does not explicitly mention this.")
        else:
            review.append("SKILL MATCH: You have all the core technologies listed in the job description. Great job!")

        # 2. Measurable Impact Audit
        missing_metrics_roles = quant_info["missing_in_roles"]
        if missing_metrics_roles:
            for role in missing_metrics_roles[:1]:
                review.append(f"IMPACT GAP: Your role at '{role.get('company')}' as '{role.get('role')}' is purely descriptive. Add quantifiable results like 'Improved performance by 20%' or 'Managed 500+ records'.")
        elif quant_info["score"] > 10:
            review.append("IMPACT AUDIT: Your resume shows high data-driven maturity with multiple quantified achievements.")

        # 3. Tone & Sentence Quality Audit
        quality = verbs_info["quality"]
        if quality["too_short_count"] > 2:
            review.append(f"CONTENT QUALITY: {quality['too_short_count']} of your bullet points are too brief. Aim for 12-20 words per point to provide enough context for recruiters.")
        if verbs_info["score"] < 7:
            review.append("TONE AUDIT: Use more high-impact action verbs. Instead of 'Help in...', use 'Spearheaded' or 'Orchestrated' to take full ownership.")

        # 4. Alignment Audit
        if relevance_info["score"] < 6:
            review.append(f"ALIGNMENT: {relevance_info['feedback']}")

        # 5. Section Completeness
        if completeness_info["missing"]:
            review.append(f"STRUCTURE: You are missing the following standard sections: {', '.join(completeness_info['missing'])}.")

        return review

    def _normalize_tech(self, text: str) -> str:
        """Normalize tech terms based on synonyms."""
        text = text.lower().strip()
        text = re.sub(r'\s*\d+(\.\d+)*\+?$', '', text)
        for canonical, aliases in TECH_SYNONYMS.items():
            if text == canonical or text in aliases: return canonical
        return text

    def _calculate_semantic_skills_match(self, resume_json: dict, jd: str) -> tuple[float, list[str], list[str]]:
        """Compare resume skills with JD using semantic normalization."""
        resume_skills_raw = []
        if isinstance(resume_json.get("skills"), dict):
            for cat in resume_json["skills"].values(): resume_skills_raw.extend(cat)
        else: resume_skills_raw = resume_json.get("skills", [])
            
        resume_skills_norm = {self._normalize_tech(s) for s in resume_skills_raw if s}
        jd_keywords = set()
        jd_lower = jd.lower()
        
        for canonical, aliases in TECH_SYNONYMS.items():
            if canonical in jd_lower or any(f" {a} " in f" {jd_lower} " for a in aliases):
                jd_keywords.add(canonical)
        
        potential_jd_skills = set(re.findall(r'\b[A-Z][a-zA-Z+#\.]*\b', jd))
        for ps in potential_jd_skills:
            ps_norm = ps.lower().strip()
            if ps_norm in SKILL_NOISE or len(ps_norm) < 2: continue
            final_skill = self._normalize_tech(ps_norm)
            if final_skill not in SKILL_NOISE: jd_keywords.add(final_skill)

        matched = [s for s in jd_keywords if s in resume_skills_norm]
        missing = [s for s in jd_keywords if s not in resume_skills_norm]
        
        if not jd_keywords: return (15 if resume_skills_norm else 0), [], []
        match_ratio = len(matched) / len(jd_keywords)
        return min(match_ratio * 35, 25), matched, missing

    def _calculate_keyword_density(self, resume_json: dict, jd: str) -> float:
        """TF-IDF Similarity score with recency weighting."""
        parts = [resume_json.get("summary", "") * 2]
        exps = resume_json.get("experience", [])
        for i, exp in enumerate(exps):
            weight = 3 if i == 0 else 1
            content = f"{exp.get('role')} {exp.get('company')} " + " ".join(exp.get("responsibilities", []))
            parts.append(content * weight)
        for proj in resume_json.get("projects", []):
            parts.append(proj.get("title", "") + " " + " ".join(proj.get("technologies", [])))
        if isinstance(resume_json.get("skills"), dict):
            for cat in resume_json["skills"].values(): parts.extend(cat)
        else: parts.extend(resume_json.get("skills", []))
        
        try:
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf = vectorizer.fit_transform([jd, " ".join([str(p) for p in parts if p])])
            sim = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
            return min(sim * 55, 15)
        except: return 0

    def _calculate_quantified_achievements(self, resume_json: dict) -> dict[str, Any]:
        """Detect metrics and identify which roles lack them."""
        text = self._flatten_resume(resume_json)
        text_no_phones = re.sub(r'\+?\d{7,}', '', text)
        patterns = [
            r'\b\d+%\b', r'\$\d+(?:[kKmMbB])?\b', r'\b\d+[xX]\b',
            r'\b(?:increased|decreased|growth|saved|reduced|managed|led|impacted|optimized|improved)\s+(?:by\s+)?(?:\d+)(?:%|\s+users|\s+revenue)?\b',
            r'\b(?:reach|user|revenue|cost|time|performance|latency)\s+(?:of|by)?\s*(?:\d+)\b'
        ]
        total_count = 0
        missing_in_roles = []
        for p in patterns: total_count += len(re.findall(p, text_no_phones, re.I))
        for exp in resume_json.get("experience", []):
            exp_text = f"{exp.get('role')} " + " ".join(exp.get("responsibilities", []))
            if not any(re.search(p, exp_text, re.I) for p in patterns): missing_in_roles.append(exp)
        return {"score": min(total_count * 3, 15), "total_count": total_count, "missing_in_roles": missing_in_roles}

    def _calculate_section_completeness(self, resume_json: dict) -> dict[str, Any]:
        """Check for core sections."""
        required = {"education": 2.5, "experience": 3.5, "projects": 2, "skills": 2}
        missing = []
        score = 0
        for sec, pts in required.items():
            if resume_json.get(sec): score += pts
            else: missing.append(sec)
        return {"score": score, "missing": missing}

    def _calculate_action_verbs_and_quality(self, resume_json: dict) -> tuple[float, list[str], dict[str, Any]]:
        """Detect strong verbs and analyze sentence complexity."""
        text = self._flatten_resume(resume_json)
        words = re.findall(r'\b\w+\b', text.lower())
        unique_verbs = {w for w in words if w in ACTION_VERBS}
        
        sentences = re.split(r'[.!?•ò]', text)
        too_short = 0
        valid = 0
        for s in sentences:
            s_words = s.strip().split()
            if 0 < len(s_words) < 8: too_short += 1
            if len(s_words) > 0: valid += 1
            
        quality_score = min(((valid - too_short) / max(valid, 1)) * 5, 5)
        return min(len(unique_verbs) * 0.5, 10) + quality_score, list(unique_verbs), {"too_short_count": too_short}

    def _calculate_role_relevance(self, resume_json: dict, jd: str) -> tuple[float, str]:
        """Compare target role in JD with experience role titles."""
        jd_title_words = set(re.findall(r'\b[A-Z][a-z]+\b', jd[:300]))
        common_roles = {"developer", "engineer", "manager", "architect", "lead", "designer", "consultant", "analyst", "intern", "staff", "senior", "junior"}
        target_role_terms = {w.lower() for w in jd_title_words if w.lower() in common_roles}
        if not target_role_terms: return 5, "Role title not clearly identified in JD."
        exp_roles = [e.get("role", "").lower() for e in resume_json.get("experience", [])]
        match = any(any(tr in er for tr in target_role_terms) for er in exp_roles)
        if match: return 10, "Your professional titles align well with the target role."
        else: return 2, f"Target role is '{'/'.join(target_role_terms)}', but your titles focus elsewhere."

    def _calculate_education_alignment(self, resume_json: dict, jd: str) -> tuple[float, str]:
        """Check if education level aligns with JD requirements."""
        jd_lower = jd.lower()
        req_v = 0
        req_s = "High School"
        for l, v in DEGREE_LEVELS.items():
            if l in jd_lower and v > req_v: req_v, req_s = v, l.capitalize()
        if req_v == 0: return 7, "No specific degree requirement found."
        cand_v = 0
        cand_s = "No Degree"
        for edu in resume_json.get("education", []):
            deg = edu.get("degree", "").lower()
            for l, v in DEGREE_LEVELS.items():
                if l in deg and v > cand_v: cand_v, cand_s = v, l.capitalize()
        if cand_v >= req_v: return 10, f"Degree {cand_s} meets requirement {req_s}."
        elif cand_v > 0: return 5, f"JD requires {req_s}, you have {cand_s}."
        return 0, "No matching degree level found."

    def _flatten_resume(self, resume_json: dict) -> str:
        """Convert JSON to flat text."""
        parts = [resume_json.get("name", ""), resume_json.get("summary", "")]
        for edu in resume_json.get("education", []): parts.append(f"{edu.get('degree')} {edu.get('institution')}")
        for exp in resume_json.get("experience", []):
            parts.append(f"{exp.get('role')} {exp.get('company')}")
            parts.extend(exp.get("responsibilities", []))
        for proj in resume_json.get("projects", []):
            parts.append(proj.get("title", ""))
            parts.extend(proj.get("technologies", []))
            parts.extend(proj.get("description", []))
        if isinstance(resume_json.get("skills"), dict):
            for cat in resume_json["skills"].values(): parts.extend(cat)
        else: parts.extend(resume_json.get("skills", []))
        return " ".join([str(p) for p in parts if p])
