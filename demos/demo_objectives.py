"""
Demonstration script for the Objectives Agent.
Shows how to generate SMART research objectives with feasibility and alignment checks.
"""

import asyncio
import json
from dotenv import load_dotenv

from google.adk.runners import InMemoryRunner
from google.genai import types

from aida.sub_agents.objectives import (
    create_objectives_agent,
    format_prompt_for_objectives
)
from aida.data_models import UserProfile, ProblemDefinition, Timeline

# Load environment variables
load_dotenv()


async def demo_objectives_generation():
    """Demonstrates the Objectives Agent workflow."""
    
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
        additional_context="Interested in coordination mechanisms for autonomous agents"
    )
    
    # Create sample problem definition
    problem_definition = ProblemDefinition(
        problem_statement="Current multi-agent systems lack effective coordination mechanisms for resource allocation in distributed environments, leading to inefficiencies and conflicts.",
        main_research_question="How can we design coordination mechanisms that improve resource allocation efficiency in multi-agent systems?",
        secondary_questions=[
            "What are the key factors affecting coordination efficiency in multi-agent systems?",
            "How do different communication protocols impact resource allocation performance?",
            "What metrics best evaluate the effectiveness of coordination mechanisms?"
        ],
        key_variables=[
            "Coordination efficiency",
            "Resource allocation time",
            "Communication overhead",
            "System scalability",
            "Conflict resolution rate"
        ],
        preliminary_literature=[],
        refinement_history=[]
    )
    
    # Create the agent
    agent = create_objectives_agent(model="gemini-2.0-flash-lite")
    
    # Create runner with context manager
    async with InMemoryRunner(agent=agent, app_name="objectives-demo") as runner:
        # Create session
        session = await runner.session_service.create_session(
            app_name=runner.app_name,
            user_id="demo_user"
        )
        
        # Format the prompt
        prompt = format_prompt_for_objectives(user_profile, problem_definition)
        
        print("=" * 80)
        print("OBJECTIVES AGENT DEMO")
        print("=" * 80)
        print("\nUser Profile:")
        print(f"  Program: {user_profile.academic_program}")
        print(f"  Field: {user_profile.field_of_study}")
        print(f"  Research Area: {user_profile.research_area}")
        print(f"  Time: {user_profile.weekly_hours} hrs/week for {user_profile.total_timeline.value} {user_profile.total_timeline.unit}")
        print(f"  Skills: {', '.join(user_profile.existing_skills)}")
        print(f"  To Learn: {', '.join(user_profile.missing_skills)}")
        print(f"  Constraints: {', '.join(user_profile.constraints)}")
        
        print("\nProblem Definition:")
        print(f"  Problem: {problem_definition.problem_statement}")
        print(f"  Main Question: {problem_definition.main_research_question}")
        print(f"  Secondary Questions: {len(problem_definition.secondary_questions)}")
        
        print("\n" + "=" * 80)
        print("GENERATING RESEARCH OBJECTIVES...")
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
        objectives = json.loads(combined_response)
        print("\n✅ Successfully parsed objectives:")
        print(f"\n  General Objective:")
        print(f"    {objectives.get('general_objective', 'N/A')}")
        
        print(f"\n  Specific Objectives ({len(objectives.get('specific_objectives', []))}):")
        for i, obj in enumerate(objectives.get('specific_objectives', []), 1):
            print(f"    {i}. {obj}")
        
        print(f"\n  Feasibility Assessment:")
        feasibility = objectives.get('feasibility_notes', {})
        print(f"    Timeline: {feasibility.get('timeline_assessment', 'N/A')}")
        print(f"    Skills Required: {', '.join(feasibility.get('skills_required', []))}")
        print(f"    Constraint Compliance: {feasibility.get('constraint_compliance', 'N/A')}")
        
        print(f"\n  Alignment Check:")
        alignment = objectives.get('alignment_check', {})
        print(f"    Coherence Score: {alignment.get('coherence_score', 'N/A')}")
        print(f"    Coverage: {alignment.get('coverage_analysis', 'N/A')}")
        
    except json.JSONDecodeError as e:
        print(f"\n❌ Unexpected JSON parsing error: {e}")
        print("This shouldn't happen with JSON mode enabled!")
        print(f"Raw response: {combined_response}")


if __name__ == "__main__":
    asyncio.run(demo_objectives_generation())
