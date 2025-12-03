"""
Demonstration script for the Problem-Formulation Agent.
Shows how to use the agent with InMemoryRunner for interactive problem definition.
"""

import asyncio
import json
from dotenv import load_dotenv

from google.adk.runners import InMemoryRunner
from google.genai import types

from aida.sub_agents.problem_formulation import (
    create_problem_formulation_agent,
    format_prompt_for_user_profile
)
from aida.data_models import UserProfile, Timeline

# Load environment variables
load_dotenv()


async def demo_problem_formulation():
    """Demonstrates the Problem-Formulation Agent workflow."""
    
    # Create a sample user profile
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
    
    # Create the agent
    agent = create_problem_formulation_agent(model="gemini-2.0-flash-lite")
    
    # Create runner with context manager for proper cleanup
    async with InMemoryRunner(agent=agent, app_name="problem-formulation-demo") as runner:
        # Create session
        session = await runner.session_service.create_session(
            app_name=runner.app_name,
            user_id="demo_user"
        )
        
        # Format the initial prompt with user profile
        initial_prompt = format_prompt_for_user_profile(user_profile)
        
        print("=" * 80)
        print("PROBLEM-FORMULATION AGENT DEMO")
        print("=" * 80)
        print("\nUser Profile:")
        print(f"  Program: {user_profile.academic_program}")
        print(f"  Field: {user_profile.field_of_study}")
        print(f"  Research Area: {user_profile.research_area}")
        print(f"  Time Available: {user_profile.weekly_hours} hrs/week for {user_profile.total_timeline.value} {user_profile.total_timeline.unit}")
        print(f"  Skills: {', '.join(user_profile.existing_skills)}")
        print(f"  To Learn: {', '.join(user_profile.missing_skills)}")
        print(f"  Constraints: {', '.join(user_profile.constraints)}")
        print("\n" + "=" * 80)
        print("GENERATING PROBLEM DEFINITION...")
        print("=" * 80 + "\n")
        
        # Run the agent
        content = types.Content(parts=[types.Part(text=initial_prompt)])
        
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
        problem_def = json.loads(combined_response)
        print("\n✅ Successfully parsed problem definition:")
        print(f"  Problem Statement: {problem_def.get('problem_statement', 'N/A')[:100]}...")
        print(f"  Main Question: {problem_def.get('main_research_question', 'N/A')}")
        print(f"  Secondary Questions: {len(problem_def.get('secondary_questions', []))}")
        print(f"  Key Variables: {len(problem_def.get('key_variables', []))}")
        print(f"  Literature Found: {len(problem_def.get('preliminary_literature', []))}")
    except json.JSONDecodeError as e:
        print(f"\n❌ Unexpected JSON parsing error: {e}")
        print("This shouldn't happen with JSON mode enabled!")
        print(f"Raw response: {combined_response}")


if __name__ == "__main__":
    asyncio.run(demo_problem_formulation())