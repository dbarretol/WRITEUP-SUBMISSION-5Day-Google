"""
Demonstration script for the Methodology Agent.
Shows how to recommend research methodologies with justification and alternatives.
"""

import asyncio
import json
from dotenv import load_dotenv

from google.adk.runners import InMemoryRunner
from google.genai import types

from aida.sub_agents.methodology import (
    create_methodology_agent,
    format_prompt_for_methodology
)
from aida.data_models import (
    UserProfile,
    ProblemDefinition,
    ResearchObjectives,
    Timeline
)

# Load environment variables
load_dotenv()


async def demo_methodology_recommendation():
    """Demonstrates the Methodology Agent workflow."""
    
    # Create sample user profile
    user_profile = UserProfile(
        academic_program="Master's",
        field_of_study="Computer Science",
        research_area="Multi-Agent Systems",
        weekly_hours=15,
        total_timeline=Timeline(value=6, unit="months"),
        existing_skills=["Python", "Machine Learning", "Data Analysis"],
        missing_skills=["Distributed Systems", "Game Theory"],
        constraints=["Remote only", "Limited computational resources"],
        additional_context="Interested in coordination mechanisms"
    )
    
    # Create sample problem definition
    problem_definition = ProblemDefinition(
        problem_statement="Current multi-agent systems lack effective coordination mechanisms for resource allocation in distributed environments.",
        main_research_question="How can we design coordination mechanisms that improve resource allocation efficiency in multi-agent systems?",
        secondary_questions=[
            "What are the key factors affecting coordination efficiency?",
            "How do different communication protocols impact performance?"
        ],
        key_variables=["Coordination efficiency", "Resource allocation time"],
        preliminary_literature=[],
        refinement_history=[]
    )
    
    # Create sample research objectives
    research_objectives = ResearchObjectives(
        general_objective="Develop and evaluate coordination mechanisms that improve resource allocation efficiency in multi-agent systems",
        specific_objectives=[
            "Design a novel communication protocol for agent coordination",
            "Implement a resource allocation algorithm based on the protocol",
            "Evaluate the performance of the coordination mechanism through simulation",
            "Compare the proposed mechanism with existing approaches"
        ],
        feasibility_notes={},
        alignment_check={}
    )
    
    # Create the agent
    agent = create_methodology_agent(model="gemini-2.0-flash-lite")
    
    # Create runner with context manager
    async with InMemoryRunner(agent=agent, app_name="methodology-demo") as runner:
        # Create session
        session = await runner.session_service.create_session(
            app_name=runner.app_name,
            user_id="demo_user"
        )
        
        # Format the prompt
        prompt = format_prompt_for_methodology(
            user_profile,
            problem_definition,
            research_objectives
        )
        
        print("=" * 80)
        print("METHODOLOGY AGENT DEMO")
        print("=" * 80)
        print("\nResearch Context:")
        print(f"  Field: {user_profile.field_of_study}")
        print(f"  Area: {user_profile.research_area}")
        print(f"  Timeline: {user_profile.total_timeline.value} {user_profile.total_timeline.unit}")
        print(f"  Problem: {problem_definition.problem_statement[:80]}...")
        print(f"  Objective: {research_objectives.general_objective[:80]}...")
        
        print("\n" + "=" * 80)
        print("GENERATING METHODOLOGY RECOMMENDATION...")
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
        methodology = json.loads(combined_response)
        print("\n✅ Successfully parsed methodology recommendation:")
        print(f"\n  Recommended Methodology: {methodology.get('recommended_methodology', 'N/A')}")
        print(f"  Type: {methodology.get('methodology_type', 'N/A')}")
        
        print(f"\n  Justification:")
        print(f"    {methodology.get('justification', 'N/A')}")
        
        print(f"\n  Required Skills ({len(methodology.get('required_skills', []))}):")
        for skill in methodology.get('required_skills', []):
            print(f"    - {skill}")
        
        timeline_fit = methodology.get('timeline_fit', {})
        print(f"\n  Timeline Fit:")
        print(f"    Feasible: {timeline_fit.get('is_feasible', 'N/A')}")
        print(f"    Duration: {timeline_fit.get('estimated_duration', 'N/A')}")
        
        alternatives = methodology.get('alternative_methodologies', [])
        print(f"\n  Alternative Methodologies ({len(alternatives)}):")
        for i, alt in enumerate(alternatives, 1):
            print(f"    {i}. {alt.get('name', 'N/A')} ({alt.get('type', 'N/A')})")
            print(f"       Pros: {', '.join(alt.get('pros', []))}")
            print(f"       Cons: {', '.join(alt.get('cons', []))}")
        
    except json.JSONDecodeError as e:
        print(f"\n❌ Unexpected JSON parsing error: {e}")
        print("This shouldn't happen with JSON mode enabled!")
        print(f"Raw response: {combined_response}")


if __name__ == "__main__":
    asyncio.run(demo_methodology_recommendation())
