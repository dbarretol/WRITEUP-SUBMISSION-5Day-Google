# Test script to verify literature_review_agent functionality

import asyncio
from google.genai import types
from google.adk.runners import InMemoryRunner
from aida.sub_agents.literature_review import (
    create_literature_review_agent,
    format_prompt_for_literature_review
)

import pytest

@pytest.mark.asyncio
async def test_literature_review_agent():
    """Test the literature review agent in isolation."""
    
    # Create the agent
    agent = create_literature_review_agent()
    
    # Create a test prompt
    prompt = format_prompt_for_literature_review(
        field_of_study="Computer Science",
        research_area="Multi-Agent Systems",
        additional_context="Focus on coordination and communication in multi-agent reinforcement learning"
    )
    
    content = types.Content(parts=[types.Part(text=prompt)])
    
    print("🔍 Testing Literature Review Agent...")
    print("="*80)
    print(f"Prompt: {prompt[:200]}...")
    print("="*80)
    
    # Track tool calls
    tool_calls = []
    
    # Use context manager for runner
    async with InMemoryRunner(agent=agent, app_name="lit-review-test") as runner:
        # Create session
        session = await runner.session_service.create_session(
            app_name="lit-review-test",
            user_id="test_user"
        )
        
        # Run agent
        async for event in runner.run_async(
            user_id=session.user_id,
            session_id=session.id,
            new_message=content
        ):
            # Track intermediate tool uses if available
            if hasattr(event, 'intermediate_data') and event.intermediate_data:
                if hasattr(event.intermediate_data, 'tool_uses'):
                    for tool_use in event.intermediate_data.tool_uses:
                        tool_name = tool_use.function_call.name if hasattr(tool_use, 'function_call') else 'unknown'
                        tool_calls.append(tool_name)
                        print(f"\n🔧 Tool Called: {tool_name}")
            
            # Print final response
            if event.is_final_response() and event.content:
                for part in event.content.parts:
                    if part.text:
                        print(f"\n✅ Response:\n{part.text[:500]}...")
    
    print("\n" + "="*80)
    print(f"📊 SUMMARY:")
    print(f"   Tool calls made: {len(tool_calls)}")
    if 'google_search' in tool_calls:
        print(f"   ✅ google_search WAS CALLED ({tool_calls.count('google_search')} times)")
    else:
        print(f"   ❌ google_search WAS NOT CALLED")
        print(f"   Tools called: {tool_calls}")
    
    return tool_calls

if __name__ == "__main__":
    result = asyncio.run(test_literature_review_agent())
