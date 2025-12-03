# Test to verify google_search tool is being invoked

import asyncio
from google.genai import types
from google.adk.runners import InMemoryRunner
from aida.sub_agents.problem_formulation import (
    create_problem_formulation_agent,
    format_prompt_for_user_profile
)
from aida.data_models import UserProfile, Timeline

import pytest

@pytest.mark.asyncio
async def test_google_search_invocation():
    """Test if google_search tool is actually invoked."""
    
    # Create a simple profile
    profile = UserProfile(
        academic_program="Master's",
        field_of_study="Computer Science",
        research_area="Multi-Agent Systems",
        weekly_hours=15,
        total_timeline=Timeline(value=6, unit="months"),
        existing_skills=["Python"],
        missing_skills=["Game Theory"],
        constraints=["Remote only"],
        additional_context="Test case for search verification"
    )
    
    # Create agent
    agent = create_problem_formulation_agent()
    
    # Use context manager for runner
    async with InMemoryRunner(agent=agent, app_name="search-test") as runner:
        session = await runner.session_service.create_session(
            app_name="search-test",
            user_id="test_user"
        )
        
        # Run with event tracking
        prompt = format_prompt_for_user_profile(profile)
        content = types.Content(parts=[types.Part(text=prompt)])
        
        print("🔍 Tracking agent execution...")
        print("="*80)
        
        tool_calls = []
        
        async for event in runner.run_async(
            user_id=session.user_id,
            session_id=session.id,
            new_message=content
        ):
            # Track tool usage
            if hasattr(event, 'intermediate_data') and event.intermediate_data:
                if hasattr(event.intermediate_data, 'tool_uses'):
                    for tool_use in event.intermediate_data.tool_uses:
                        tool_info = {
                            'name': tool_use.function_call.name if hasattr(tool_use, 'function_call') else 'unknown',
                            'args': str(tool_use.function_call.args) if hasattr(tool_use, 'function_call') else None
                        }
                        tool_calls.append(tool_info)
                        print(f"\n🔧 Tool Called: {tool_info['name']}")
                        if tool_info['args']:
                            print(f"   Args: {tool_info['args'][:200]}...")
            
            # Final response
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        print(f"\n✅ Response received ({len(part.text)} chars)")
    
    print("\n" + "="*80)
    print(f"📊 SUMMARY: {len(tool_calls)} tool call(s) made")
    
    if tool_calls:
        print("\nTools invoked:")
        for i, tool in enumerate(tool_calls, 1):
            print(f"  {i}. {tool['name']}")
    else:
        print("\n⚠️  WARNING: No tools were called!")
        print("   This means google_search was NOT invoked.")
    
    return tool_calls

if __name__ == "__main__":
    result = asyncio.run(test_google_search_invocation())
