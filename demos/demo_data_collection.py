"""
Demonstration script for the Data-Collection Agent.
Shows how to recommend data collection techniques, tools, and estimate resources.
"""

import asyncio
import json
from dotenv import load_dotenv

from google.adk.runners import InMemoryRunner
from google.genai import types

from academic_research.sub_agents.data_collection import (
    create_data_collection_agent,
    format_prompt_for_data_collection
)
from academic_research.data_models import (
    UserProfile,
    ResearchObjectives,
    MethodologyRecommendation,
    Timeline
)

# Load environment variables
load_dotenv()


async def demo_data_collection_planning():
    """Demonstrates the Data-Collection Agent workflow."""
    
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
        justification="Allows controlled testing of coordination mechanisms in various scenarios.",
        required_skills=["Python", "Statistical Analysis", "Simulation Design"],
        timeline_fit={
            "is_feasible": True,
            "estimated_duration": "5 months"
        },
        alternative_methodologies=[]
    )
    
    # Create the agent
    agent = create_data_collection_agent(model="gemini-2.0-flash-lite")
    
    # Create runner
    runner = InMemoryRunner(agent=agent, app_name="data-collection-demo")
    
    # Create session
    session = await runner.session_service.create_session(
        app_name=runner.app_name,
        user_id="demo_user"
    )
    
    # Format the prompt
    prompt = format_prompt_for_data_collection(
        user_profile,
        research_objectives,
        methodology
    )
    
    print("=" * 80)
    print("DATA-COLLECTION AGENT DEMO")
    print("=" * 80)
    print("\nResearch Context:")
    print(f"  Field: {user_profile.field_of_study}")
    print(f"  Area: {user_profile.research_area}")
    print(f"  Timeline: {user_profile.total_timeline.value} {user_profile.total_timeline.unit}")
    print(f"  Methodology: {methodology.recommended_methodology}")
    print(f"  Type: {methodology.methodology_type}")
    
    print("\n" + "=" * 80)
    print("GENERATING DATA COLLECTION PLAN...")
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
        plan = json.loads(combined_response)
        print("\n✅ Successfully parsed data collection plan:")
        
        print(f"\n  Collection Techniques ({len(plan.get('collection_techniques', []))}):")
        for tech in plan.get('collection_techniques', []):
            print(f"    - {tech}")
            
        print(f"\n  Recommended Tools ({len(plan.get('recommended_tools', []))}):")
        for tool in plan.get('recommended_tools', []):
            print(f"    - {tool.get('name', 'N/A')}: {tool.get('purpose', 'N/A')}")
            print(f"      Type: {tool.get('type', 'N/A')}, Accessibility: {tool.get('accessibility', 'N/A')}")
        
        print(f"\n  Data Sources ({len(plan.get('data_sources', []))}):")
        for source in plan.get('data_sources', []):
            print(f"    - {source}")
        
        print(f"\n  Estimated Sample Size:")
        print(f"    {plan.get('estimated_sample_size', 'N/A')}")
        
        timeline = plan.get('timeline_breakdown', {})
        print(f"\n  Timeline Breakdown:")
        print(f"    Total: {timeline.get('total_duration', 'N/A')}")
        for phase in ['preparation', 'collection', 'quality_check']:
            if phase in timeline:
                print(f"    {phase.title()}: {timeline[phase].get('duration', 'N/A')}")
        
        print(f"\n  Resource Requirements ({len(plan.get('resource_requirements', []))}):")
        for req in plan.get('resource_requirements', []):
            print(f"    - {req}")
        
    except json.JSONDecodeError as e:
        print(f"\n❌ Unexpected JSON parsing error: {e}")
        print("This shouldn't happen with JSON mode enabled!")
        print(f"Raw response: {combined_response}")


if __name__ == "__main__":
    asyncio.run(demo_data_collection_planning())
