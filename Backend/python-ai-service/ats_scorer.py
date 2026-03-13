"""
ATSScorer — stub implementation.
Replace with actual ATS-scoring logic later.
"""


class ATSScorer:
    """Scores a resume against a job description for ATS compatibility."""

    def score(self, file_bytes: bytes, filename: str, job_description: str) -> dict:
        """
        Score a resume for ATS compatibility.

        Args:
            file_bytes:      Raw bytes of the uploaded resume file.
            filename:        Original filename.
            job_description: The target job description to score against.

        Returns:
            dict with ATS score results.
        """
        # TODO: Implement keyword extraction, matching, and scoring.
        return {
            "filename": filename,
            "ats_score": None,
            "matched_keywords": [],
            "missing_keywords": [],
            "recommendations": [
                "This is a placeholder. Integrate an ATS-scoring algorithm."
            ],
        }
