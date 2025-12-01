"""Objectives Agent for academic research."""

import os
from typing import Dict, Any, List, Optional
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.genai import types

from ...data_models import UserProfile, ProblemDefinition, ResearchObjectives
from ...config import RETRY_CONFIG, DEFAULT_MODEL

from .prompt import SYSTEM_INSTRUCTION, USER_CONTEXT_TEMPLATE

def create_objectives_agent(model: str = DEFAULT_MODEL) -> Agent:
    """
    Factory function to create an Objectives Agent.
    
    Args:
        model: The Gemini model to use.
        
    Returns:
        Configured Agent instance.
    """
    return Agent(
        name="objectives_agent",
        model=Gemini(model=model, retry_options=RETRY_CONFIG),
        output_schema=ResearchObjectives,
        generate_content_config=types.GenerateContentConfig(
            temperature=0.1,
            response_mime_type="application/json",
        ),
        instruction=SYSTEM_INSTRUCTION,
        description=(
            "Defines general and specific research objectives, evaluates feasibility, "
            "and ensures alignment with the problem definition."
        )
    )

def format_prompt_for_objectives(
    user_profile: UserProfile,
    problem_definition: ProblemDefinition
) -> str:
    """
    Formats the prompt with user profile and problem definition context.
    
    Args:
        user_profile: The user's academic profile.
        problem_definition: The defined research problem.
        
    Returns:
        Formatted prompt string.
    """
    # Format timeline
    timeline_str = f"{user_profile.total_timeline.value} {user_profile.total_timeline.unit}"
    
    # Format lists
    existing_skills_str = ", ".join(user_profile.existing_skills) if user_profile.existing_skills else "None specified"
    missing_skills_str = ", ".join(user_profile.missing_skills) if user_profile.missing_skills else "None"
    constraints_str = ", ".join(user_profile.constraints) if user_profile.constraints else "None"
    secondary_questions_str = "; ".join(problem_definition.secondary_questions) if problem_definition.secondary_questions else "None"
    key_variables_str = ", ".join(problem_definition.key_variables) if problem_definition.key_variables else "None"
    
    return USER_CONTEXT_TEMPLATE.format(
        academic_program=user_profile.academic_program,
        field_of_study=user_profile.field_of_study,
        research_area=user_profile.research_area,
        weekly_hours=user_profile.weekly_hours,
        timeline=timeline_str,
        existing_skills=existing_skills_str,
        missing_skills=missing_skills_str,
        constraints=constraints_str,
        problem_statement=problem_definition.problem_statement,
        main_research_question=problem_definition.main_research_question,
        secondary_questions=secondary_questions_str,
        key_variables=key_variables_str
    )


# For backward compatibility and testing
class ObjectivesAgent(Agent):
    """Legacy wrapper - use create_objectives_agent() for new code."""
    
    def __init__(self, model: str = DEFAULT_MODEL, **kwargs):
        super().__init__(
            name="objectives_agent",
            model=Gemini(model=model, retry_options=RETRY_CONFIG),
            output_schema=ResearchObjectives,
            generate_content_config=types.GenerateContentConfig(
                response_mime_type="application/json"
            ),
            instruction=SYSTEM_INSTRUCTION,
            **kwargs
        )
