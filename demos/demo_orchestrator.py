"""
Demonstration script for the Research Proposal Orchestrator.
Simulates the full workflow using mocked agents to show state transitions and coordination.
"""

import asyncio
import json
import logging
from unittest.mock import MagicMock, AsyncMock

from academic_research.orchestrator import ResearchProposalOrchestrator
from academic_research.data_models import UserProfile, Timeline

# Configure logging to show orchestrator progress
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def demo_orchestrator():
    """Run the orchestrator demo."""
    
    print("=" * 80)
    print("RESEARCH PROPOSAL ORCHESTRATOR DEMO")
    print("=" * 80)
    
    # 1. Setup Mock Agents
    # We mock the agents to return static JSON responses for the demo
    # This avoids making 50+ API calls and ensures a predictable path
    
    mock_agents = {
        'interviewer': MagicMock(),
        'problem_formulation': MagicMock(),
        'objectives': MagicMock(),
        'methodology': MagicMock(),
        'data_collection': MagicMock(),
        'quality_control': MagicMock()
    }
    
    # Define mock responses
    responses = {
        'problem_formulation': {
            "problem_statement": "AI agents lack coordination.",
            "main_research_question": "How to improve coordination?",
            "secondary_questions": ["What protocols work best?"],
            "key_variables": ["Efficiency", "Latency"],
            "preliminary_literature": [],
            "refinement_history": []
        },
        'objectives': {
            "general_objective": "Develop coordination protocol",
            "specific_objectives": ["Design protocol", "Test protocol"],
            "feasibility_notes": {},
            "alignment_check": {}
        },
        'methodology': {
            "recommended_methodology": "Simulation Study",
            "methodology_type": "quantitative",
            "justification": "Allows controlled testing",
            "required_skills": ["Python"],
            "timeline_fit": {},
            "alternative_methodologies": []
        },
        'data_collection': {
            "collection_techniques": ["Simulation logging"],
            "recommended_tools": [],
            "data_sources": [],
            "estimated_sample_size": "100 runs",
            "timeline_breakdown": {},
            "resource_requirements": []
        },
        'quality_control': {
            "validation_passed": True,
            "coherence_score": 0.95,
            "feasibility_score": 0.9,
            "overall_quality_score": 92.5,
            "issues_identified": [],
            "recommendations": [],
            "requires_refinement": False,
            "refinement_targets": []
        }
    }
    
    # 2. Setup Orchestrator
    def progress_callback(step, pct):
        print(f"\n>>> PROGRESS: {step} ({pct}%)")
        
    orchestrator = ResearchProposalOrchestrator(progress_callback=progress_callback)
    
    # 3. Mock the _execute_agent method to return our static JSON
    # This simulates the agent actually running and returning text
    async def mock_execute(agent, prompt, runner):
        # Determine which agent is running based on the mock object
        for name, mock_agent in mock_agents.items():
            if agent == mock_agent:
                print(f"    [Mock] Executing {name} agent...")
                return json.dumps(responses[name])
        return "{}"

    orchestrator._execute_agent = mock_execute
    
    # 4. Create Initial User Profile (Simulating Interview Completion)
    initial_profile = UserProfile(
        academic_program="Master's",
        field_of_study="Computer Science",
        research_area="Multi-Agent Systems",
        weekly_hours=20,
        total_timeline=Timeline(value=6, unit="months"),
        existing_skills=["Python", "AI"],
        missing_skills=[],
        constraints=[]
    )
    
    # 5. Run Workflow
    print("\nStarting Workflow...")
    result = await orchestrator.run_workflow(
        mock_agents,
        runner=MagicMock(), # Mock runner
        initial_profile=initial_profile
    )
    
    # 6. Display Results
    print("\n" + "=" * 80)
    print("WORKFLOW COMPLETE")
    print("=" * 80)
    
    if result['success']:
        print("\nFinal Proposal Generated:")
        proposal = result['proposal']
        print(f"  Problem: {proposal['problem_definition']['problem_statement']}")
        print(f"  Objective: {proposal['research_objectives']['general_objective']}")
        print(f"  Methodology: {proposal['methodology']['recommended_methodology']}")
        print(f"  QC Score: {proposal['quality_validation']['coherence_score']}")
        
        print("\nWorkflow Metadata:")
        print(f"  Refinement Iterations: {result['metadata']['refinement_iterations']}")
        print("  History:")
        for transition in result['metadata']['workflow_history']:
            print(f"    {transition['from']} -> {transition['to']}")
    else:
        print(f"\nWorkflow Failed: {result['error']}")

if __name__ == "__main__":
    asyncio.run(demo_orchestrator())
