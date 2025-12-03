"""Methodology Agent for academic research."""

import os
from typing import Dict, Any, List, Optional
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.genai import types

from ...data_models import UserProfile, ProblemDefinition, ResearchObjectives, MethodologyRecommendation
from ...config import RETRY_CONFIG, DEFAULT_MODEL

from .prompt import SYSTEM_INSTRUCTION, USER_CONTEXT_TEMPLATE

def create_methodology_agent(model: str = DEFAULT_MODEL) -> Agent:
    """
    Factory function to create a Methodology Agent.
    
    Args:
        model: The Gemini model to use.
        
    Returns:
        Configured Agent instance.
    """
    return Agent(
        name="methodology_agent",
        model=Gemini(model=model, retry_options=RETRY_CONFIG),
        output_schema=MethodologyRecommendation,
        generate_content_config=types.GenerateContentConfig(
            temperature=0.1,
            response_mime_type="application/json",
        ),
        instruction=SYSTEM_INSTRUCTION,
        description=(
            "Recommends research methodologies, provides justification, "
            "assesses timeline fit, and suggests alternatives based on "
            "research objectives and user constraints."
        )
    )

def format_prompt_for_methodology(
    user_profile: UserProfile,
    problem_definition: ProblemDefinition,
    research_objectives: ResearchObjectives
) -> str:
    """
    Formats the prompt with user profile, problem definition, and objectives context.
    
    Args:
        user_profile: The user's academic profile.
        problem_definition: The defined research problem.
        research_objectives: The research objectives.
        
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
    
    # Infer research type hint from problem definition
    research_type_hint = "To be determined based on objectives"
    if any(word in problem_definition.main_research_question.lower() for word in ["how many", "measure", "quantify", "correlation", "effect"]):
        research_type_hint = "Likely quantitative"
    elif any(word in problem_definition.main_research_question.lower() for word in ["how", "why", "experience", "perception", "understand"]):
        research_type_hint = "Likely qualitative"
    
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
        research_type_hint=research_type_hint,
        general_objective=research_objectives.general_objective,
        specific_objectives=specific_objectives_str
    )


# For backward compatibility and testing
class MethodologyAgent(Agent):
    """Legacy wrapper - use create_methodology_agent() for new code."""
    
    def __init__(self, model: str = DEFAULT_MODEL, **kwargs):
        super().__init__(
            name="methodology_agent",
            model=Gemini(model=model, retry_options=RETRY_CONFIG),
            output_schema=MethodologyRecommendation,
            generate_content_config=types.GenerateContentConfig(
                response_mime_type="application/json"
            ),
            instruction=SYSTEM_INSTRUCTION,
            **kwargs
        )
