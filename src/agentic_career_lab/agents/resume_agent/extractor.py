import json

from agentic_career_lab.llm.local import LocalLLM
from agentic_career_lab.models import ResumeEvidence


class ResumeExtractor:
    def __init__(self, llm: LocalLLM):
        self.llm = llm

    def extract(self, resume_text: str) -> ResumeEvidence:
        prompt = f"""
        Extract the following from the resume. Return ONLY valid JSON:
        {{
            "skills": ["list of explicit skills"],
            "experience": [{{"title": "Role", "company": "Company"}}],
            "projects": [{{"title": "Project Name"}}],
            "education": ["Degrees"],
            "technologies": ["list of technologies mentioned"]
        }}

        Resume text:
        {resume_text}
        """
        try:
            response_text = self.llm.generate(prompt)
            data = json.loads(response_text)
            return ResumeEvidence(
                skills=data.get("skills", []),
                experience=data.get("experience", []),
                projects=data.get("projects", []),
                education=data.get("education", []),
                technologies=data.get("technologies", []),
                unsupported_claims_detected=[],
            )
        except Exception:
            # Deterministic local fallback if local Ollama times out or returns non-JSON:
            # Inspect resume_text directly for known verifiable keywords instead of blindly attributing unmentioned skills.
            known_skills = [
                "Python",
                "Docker",
                "SQL",
                "Google Cloud",
                "REST APIs",
                "Kubernetes",
                "FastAPI",
                "PostgreSQL",
                "Git",
            ]
            resume_lower = resume_text.lower()
            detected_skills = [s for s in known_skills if s.lower() in resume_lower]

            return ResumeEvidence(
                skills=detected_skills,
                technologies=detected_skills,
                experience=[],
                projects=[],
                education=[],
                unsupported_claims_detected=[
                    "Local LLM extraction unavailable; matched from verified text keywords only."
                ],
            )
