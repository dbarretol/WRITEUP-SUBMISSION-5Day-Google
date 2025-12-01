"""Data-Collection Agent for academic research."""

import os
from typing import Dict, Any, List, Optional
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.genai import types

from ...data_models import (
    UserProfile,
    ResearchObjectives,
    MethodologyRecommendation,
    DataCollectionPlan
)
from ...config import RETRY_CONFIG, DEFAULT_MODEL

from .prompt import SYSTEM_INSTRUCTION, USER_CONTEXT_TEMPLATE

def create_data_collection_agent(model: str = DEFAULT_MODEL) -> Agent:
    """
    Factory function to create a Data-Collection Agent.
    
    Args:
        model: The Gemini model to use.
        
    Returns:
        Configured Agent instance.
    """
    return Agent(
        name="data_collection_agent",
        model=Gemini(model=model, retry_options=RETRY_CONFIG),
        output_schema=DataCollectionPlan,
        generate_content_config=types.GenerateContentConfig(
            temperature=0.1,
            response_mime_type="application/json",
        ),
        instruction=SYSTEM_INSTRUCTION,
        description=(
            "Recommends data collection techniques and tools, estimates "
            "resource requirements, and creates timeline breakdowns based on "
            "methodology and research objectives."
        )
    )

def format_prompt_for_data_collection(
    user_profile: UserProfile,
    research_objectives: ResearchObjectives,
    methodology: MethodologyRecommendation
) -> str:
    """
    Formats the prompt with user profile, objectives, and methodology context.
    
    Args:
        user_profile: The user's academic profile.
        research_objectives: The research objectives.
        methodology: The recommended methodology.
        
    Returns:
        Formatted prompt string.
    """
    # Format timeline
    timeline_str = f"{user_profile.total_timeline.value} {user_profile.total_timeline.unit}"
    
    # Format lists
    existing_skills_str = ", ".join(user_profile.existing_skills) if user_profile.existing_skills else "None specified"
    missing_skills_str = ", ".join(user_profile.missing_skills) if user_profile.missing_skills else "None"
    constraints_str = ", ".join(user_profile.constraints) if user_profile.constraints else "None"
    specific_objectives_str = "; ".join(research_objectives.specific_objectives) if research_objectives.specific_objectives else "None"
    methodology_skills_str = ", ".join(methodology.required_skills) if methodology.required_skills else "None"
    
    return USER_CONTEXT_TEMPLATE.format(
        academic_program=user_profile.academic_program,
        field_of_study=user_profile.field_of_study,
        research_area=user_profile.research_area,
        weekly_hours=user_profile.weekly_hours,
        timeline=timeline_str,
        existing_skills=existing_skills_str,
        missing_skills=missing_skills_str,
        constraints=constraints_str,
        general_objective=research_objectives.general_objective,
        specific_objectives=specific_objectives_str,
        recommended_methodology=methodology.recommended_methodology,
        methodology_type=methodology.methodology_type,
        methodology_skills=methodology_skills_str
    )


# For backward compatibility and testing
class DataCollectionAgent(Agent):
    """Legacy wrapper - use create_data_collection_agent() for new code."""
    
    def __init__(self, model: str = DEFAULT_MODEL, **kwargs):
        super().__init__(
            name="data_collection_agent",
            model=Gemini(model=model, retry_options=RETRY_CONFIG),
            output_schema=DataCollectionPlan,
            generate_content_config=types.GenerateContentConfig(
                response_mime_type="application/json"
            ),
            instruction=SYSTEM_INSTRUCTION,
            **kwargs
        )
