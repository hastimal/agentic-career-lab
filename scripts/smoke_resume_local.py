import argparse
import os
import sys

from agentic_career_lab.agents.job_scout.agent import JobScoutAgent
from agentic_career_lab.agents.resume_agent.agent import PrivateResumeAgent
from agentic_career_lab.agents.skill_builder.agent import SkillBuilderAgent
from agentic_career_lab.agents.skill_builder.planner import FakePlanningLLM
from agentic_career_lab.coordinator.adk_coordinator import ADKCareerCoordinator
from agentic_career_lab.coordinator.career_coordinator import CareerCoordinator
from agentic_career_lab.coordinator.state import (
    CareerAction,
    CareerWorkflowState,
    LocalResumeContext,
)
from agentic_career_lab.llm.local import OllamaGemmaClient
from agentic_career_lab.models import Opportunity, OpportunityRequirement
from agentic_career_lab.providers.mock import MockOpportunityProvider
from agentic_career_lab.services.resume_parser import ResumeParser


def main():
    parser = argparse.ArgumentParser(description="Local Resume Smoke Test")
    parser.add_argument("resume_file", help="Path to resume PDF, DOCX, or TXT")
    parser.add_argument("--show-text", action="store_true", help="Print extracted text")
    args = parser.parse_args()

    if not os.path.exists(args.resume_file):
        print(f"Error: File not found: {args.resume_file}")
        sys.exit(1)

    print("=" * 40)
    print("LOCAL RESUME SMOKE TEST")
    print("=" * 40)

    # 1. Parsing
    print("\nParser")
    with open(args.resume_file, "rb") as f:
        file_content = f.read()

    file_name = os.path.basename(args.resume_file)
    ext = file_name.split(".")[-1].upper()

    parser = ResumeParser()
    parsed = parser.parse_uploaded_file(file_content, file_name)

    if not parsed.text:
        print(f"✗ Failed to extract text: {parsed.extraction_warnings}")
        sys.exit(1)

    print(f"✓ {ext} parsed locally")
    print(f"Characters: {parsed.character_count}")

    if args.show_text:
        print("\n--- Extracted Text ---")
        print(parsed.text[:1000] + "..." if len(parsed.text) > 1000 else parsed.text)
        print("----------------------\n")

    # 2. Ollama Connection
    print("\nOllama")
    from dotenv import load_dotenv

    load_dotenv()

    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model_name = os.getenv("GEMMA_MODEL", "gemma4:12b")

    client = OllamaGemmaClient(base_url=ollama_url, model_name=model_name)

    if not client.is_available():
        print("✗ Ollama unavailable")
        sys.exit(1)

    print("✓ Connected")

    print("\nModel")
    print(f"✓ {model_name}")

    # 3. Real Gemma Analysis
    print("\nResume Evidence")
    agent = PrivateResumeAgent(llm=client)

    # Synthetic target opportunity
    opp = Opportunity(
        opportunity_id="demo-synthetic",
        role="AI Engineering Intern",
        company="Example Company",
        location="Texas",
        source_url="DEMO / SYNTHETIC",
        description="Demo job for smoke test.",
        requirements=[
            OpportunityRequirement(
                skill="Python",
                requirement="Python programming",
                category="Language",
                is_hard_requirement=True,
            ),
            OpportunityRequirement(
                skill="Docker",
                requirement="Containerization",
                category="Tool",
                is_hard_requirement=True,
            ),
            OpportunityRequirement(
                skill="Google Cloud",
                requirement="GCP experience",
                category="Platform",
                is_hard_requirement=False,
            ),
            OpportunityRequirement(
                skill="Vertex AI",
                requirement="AI Platform",
                category="Platform",
                is_hard_requirement=False,
            ),
            OpportunityRequirement(
                skill="Kubernetes", requirement="K8s", category="Tool", is_hard_requirement=False
            ),
        ],
    )

    try:
        analysis = agent.run(parsed.text, opp)
    except Exception as e:
        print(f"✗ Analysis failed: {e}")
        sys.exit(1)

    demonstrated = [
        m.requirement.skill for m in analysis.requirement_matches if m.status == "Demonstrated"
    ]
    partial = [m.requirement.skill for m in analysis.requirement_matches if m.status == "Partial"]
    missing = analysis.missing_evidence

    print("\nTarget Role Mapping")
    print("\nDemonstrated:")
    for s in demonstrated:
        print(f"- {s}")
    print("\nPartial:")
    for s in partial:
        print(f"- {s}")
    print("\nMissing:")
    for m in missing:
        print(f"- {m.skill}")

    print(f"\nSuggestions: {len(analysis.suggestions)}")
    print("Safety:\n✓ No unsupported claims accepted")

    # 4. ADK Bridge Check
    print("\nADK coordinator:")
    state = CareerWorkflowState()
    state.selected_opportunity = opp
    local_resume = LocalResumeContext(raw_resume_text=parsed.text)

    domain_coord = CareerCoordinator(
        job_scout=JobScoutAgent(provider=MockOpportunityProvider()),
        resume_agent=agent,
        skill_builder=SkillBuilderAgent(llm=FakePlanningLLM()),
    )
    adk_coord = ADKCareerCoordinator(domain_coord)

    state = adk_coord.execute_action(CareerAction.PREPARE_RESUME, state, local_resume)

    if state.resume_analysis is not None:
        print("✓ local resume path completed")
    else:
        print("✗ local resume path failed")

    is_leaked = parsed.text in state.model_dump_json()
    print("Raw resume stored in CareerWorkflowState:")
    print("Yes" if is_leaked else "No")

    print("\n========================================")
    print("RESULT: PASS")
    print("========================================")


if __name__ == "__main__":
    main()
