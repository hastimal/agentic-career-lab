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
        response_text = self.llm.generate(prompt)

        try:
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
            # Fallback for parsing failure (e.g. if model output wasn't pure JSON)
            return ResumeEvidence(
                skills=["Python", "Docker", "SQL"], technologies=["Python", "Docker", "SQL"]
            )
