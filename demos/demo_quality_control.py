"""
Demonstration script for the Quality-Control Agent.
Shows how to validate a complete research proposal.
"""

import asyncio
import json
from dotenv import load_dotenv

from google.adk.runners import InMemoryRunner
from google.genai import types

from aida.sub_agents.quality_control import (
    create_quality_control_agent,
    format_prompt_for_quality_control
)
from aida.data_models import (
    UserProfile,
    ProblemDefinition,
    ResearchObjectives,
    MethodologyRecommendation,
    DataCollectionPlan,
    Timeline
)

# Load environment variables
load_dotenv()


async def demo_quality_validation():
    """Demonstrates the Quality-Control Agent workflow."""
    
    # Create sample user profile
    user_profile = UserProfile(
        academic_program="Master's",
        field_of_study="Computer Science",
        research_area="Multi-Agent Systems",
        weekly_hours=15,
        total_timeline=Timeline(value=6, unit="months"),
        existing_skills=["Python", "Machine Learning", "Data Analysis"],
        missing_skills=["Distributed Systems"],
        constraints=["Remote only", "Limited computational resources"],
        additional_context="Interested in coordination mechanisms"
    )
    
    # Create sample problem definition
    problem_definition = ProblemDefinition(
        problem_statement="Current multi-agent systems lack effective coordination mechanisms for resource allocation in distributed environments.",
        main_research_question="How can we design coordination mechanisms that improve resource allocation efficiency in multi-agent systems?",
        secondary_questions=[
            "What factors affect coordination efficiency?",
            "How do communication protocols impact performance?"
        ],
        key_variables=["Coordination efficiency", "Resource allocation time"],
        preliminary_literature=[],
        refinement_history=[]
    )
    
    # Create sample research objectives
    research_objectives = ResearchObjectives(
        general_objective="Develop and evaluate coordination mechanisms for multi-agent systems",
        specific_objectives=[
            "Design a communication protocol for agent coordination",
            "Implement a resource allocation algorithm",
            "Evaluate performance through simulation",
            "Compare with existing approaches"
        ],
        feasibility_notes={},
        alignment_check={}
    )
    
    # Create sample methodology
    methodology = MethodologyRecommendation(
        recommended_methodology="Experimental Study with Simulation",
        methodology_type="quantitative",
        justification="Allows controlled testing of coordination mechanisms.",
        required_skills=["Python", "Statistical Analysis", "Simulation Design"],
        timeline_fit={"is_feasible": True, "estimated_duration": "5 months"},
        alternative_methodologies=[]
    )
    
    # Create sample data collection plan
    data_collection = DataCollectionPlan(
        collection_techniques=["Agent-based Simulation", "Performance Benchmarking"],
        recommended_tools=[
            {"name": "Python", "purpose": "Simulation", "type": "software", "accessibility": "free"},
            {"name": "NumPy", "purpose": "Data processing", "type": "software", "accessibility": "free"}
        ],
        data_sources=["Simulated multi-agent environments", "Benchmark datasets"],
        estimated_sample_size="1000 simulation runs across 10 scenarios",
        timeline_breakdown={
            "preparation": {"duration": "2 weeks"},
            "collection": {"duration": "8 weeks"},
            "quality_check": {"duration": "2 weeks"},
            "total_duration": "12 weeks"
        },
        resource_requirements=["Computing resources (CPU time)", "Time: 15 hrs/week"]
    )
    
    # Create the agent
    agent = create_quality_control_agent(model="gemini-2.0-flash-lite")
    
    # Create runner with context manager
    async with InMemoryRunner(agent=agent, app_name="quality-control-demo") as runner:
        # Create session
        session = await runner.session_service.create_session(
            app_name=runner.app_name,
            user_id="demo_user"
        )
        
        # Format the prompt
        prompt = format_prompt_for_quality_control(
            user_profile,
            problem_definition,
            research_objectives,
            methodology,
            data_collection
        )
        
        print("=" * 80)
        print("QUALITY-CONTROL AGENT DEMO")
        print("=" * 80)
        print("\nValidating Complete Research Proposal...")
        print(f"  Field: {user_profile.field_of_study}")
        print(f"  Timeline: {user_profile.total_timeline.value} {user_profile.total_timeline.unit}")
        print(f"  Methodology: {methodology.recommended_methodology}")
        
        print("\n" + "=" * 80)
        print("PERFORMING MULTI-CRITERIA VALIDATION...")
        print("=" * 80 + "\n")
        
        # Run the agent
        content = types.Content(parts=[types.Part(text=prompt)])
        
        all_responses = []
        async for event in runner.run_async(
            user_id=session.user_id,
            session_id=session.id,
            new_message=content,
        ):
            if event.content.parts and event.content.parts[0].text:
                part_text = event.content.parts[0].text
                all_responses.append(part_text)
                print(part_text)
    
    print("\n" + "=" * 80)
    print("DEMO COMPLETE")
    print("=" * 80)
    
    # Parse the response - Gemini JSON mode guarantees valid JSON
    combined_response = "\n".join(all_responses)
    
    try:
        validation = json.loads(combined_response)
        print("\n✅ Successfully parsed quality validation:")
        print(f"\n  Validation Passed: {validation.get('validation_passed', 'N/A')}")
        print(f"  Coherence Score: {validation.get('coherence_score', 'N/A')}")
        print(f"  Feasibility Score: {validation.get('feasibility_score', 'N/A')}")
        
        issues = validation.get('issues_identified', [])
        print(f"\n  Issues Identified ({len(issues)}):")
        for issue in issues:
            print(f"    - [{issue.get('severity', 'N/A').upper()}] {issue.get('component', 'N/A')}")
            print(f"      {issue.get('description', 'N/A')}")
        
        recommendations = validation.get('recommendations', [])
        print(f"\n  Recommendations ({len(recommendations)}):")
        for rec in recommendations:
            print(f"    - {rec}")
        
        print(f"\n  Requires Refinement: {validation.get('requires_refinement', 'N/A')}")
        
        if validation.get('requires_refinement'):
            targets = validation.get('refinement_targets', [])
            print(f"  Refinement Targets: {', '.join(targets)}")
        
    except json.JSONDecodeError as e:
        print(f"\n❌ Unexpected JSON parsing error: {e}")
        print("This shouldn't happen with JSON mode enabled!")
        print(f"Raw response: {combined_response}")


if __name__ == "__main__":
    asyncio.run(demo_quality_validation())
