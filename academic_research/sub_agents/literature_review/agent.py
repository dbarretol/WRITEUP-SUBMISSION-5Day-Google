"""Literature Review Agent for preliminary academic research."""

import os
from typing import Dict, Any, List, Optional
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools import google_search
from google.genai import types

from ...data_models import LiteratureReviewResult
from ...config import RETRY_CONFIG, DEFAULT_MODEL

from .prompt import SYSTEM_INSTRUCTION, format_prompt_for_literature_review

def create_literature_review_agent(model: str = DEFAULT_MODEL) -> Agent:
    """
    Factory function to create a Literature Review Agent.
    
    This agent is a specialist that uses google_search to find academic literature.
    It performs 2-3 searches with varied queries and returns structured results.
    
    Args:
        model: The Gemini model to use.
        
    Returns:
        Configured Agent instance.
    """
    print(f"[DEBUG] Creating LiteratureReviewAgent with model: {model}")
    return Agent(
        name="literature_review_agent",
        model=Gemini(model=model, retry_options=RETRY_CONFIG),
        # output_schema removed to allow tool use (JSON mode conflicts with tools)
        generate_content_config=types.GenerateContentConfig(
            temperature=0.2,  # Slightly higher for search query variation
            # response_mime_type removed
        ),
        instruction=SYSTEM_INSTRUCTION,
        tools=[google_search],  # Tool will be called by the agent
        description=(
            "Specialist agent for conducting preliminary literature review. "
            "Performs multiple academic searches and returns structured literature findings."
        )
    )


# For backward compatibility and testing
class LiteratureReviewAgent(Agent):
    """Legacy wrapper - use create_literature_review_agent() for new code."""
    
    def __init__(self, model: str = DEFAULT_MODEL, **kwargs):
        super().__init__(
            name="literature_review_agent",
            model=Gemini(model=model, retry_options=RETRY_CONFIG),
            # output_schema removed
            generate_content_config=types.GenerateContentConfig(
                temperature=0.2,
                # response_mime_type removed
            ),
            instruction=SYSTEM_INSTRUCTION,
            tools=[google_search],
            **kwargs
        )
