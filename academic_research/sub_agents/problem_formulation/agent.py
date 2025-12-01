"""Problem-Formulation Agent for academic research."""

import os
from typing import Dict, Any, List, Optional
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools import AgentTool
from google.genai import types

from ...data_models import UserProfile, ProblemDefinition
from ...config import RETRY_CONFIG, DEFAULT_MODEL
from ..literature_review import create_literature_review_agent

from .prompt import SYSTEM_INSTRUCTION, USER_CONTEXT_TEMPLATE

def create_problem_formulation_agent(model: str = DEFAULT_MODEL) -> Agent:
    """
    Factory function to create a Problem-Formulation Agent.
    
    This agent delegates literature review to a specialist agent and focuses
    on formulating the research problem based on the literature findings.
    
    Args:
        model: The Gemini model to use.
        
    Returns:
        Configured Agent instance.
    """
    # Create the literature review specialist agent
    lit_review_agent = create_literature_review_agent(model=model)
    
    return Agent(
        name="problem_formulation_agent",
        model=Gemini(model=model, retry_options=RETRY_CONFIG),
        # output_schema removed to allow tool use (JSON mode conflicts with tools)
        generate_content_config=types.GenerateContentConfig(
            temperature=0.1,
            # response_mime_type removed
        ),
        instruction=SYSTEM_INSTRUCTION,
        tools=[
            AgentTool(agent=lit_review_agent),  # Delegate literature review to specialist
        ],
        description=(
            "Formulates research problems by delegating literature search to a specialist agent "
            "and generating structured problem definitions for academic research proposals."
        )
    )

def format_prompt_for_user_profile(
    user_profile: UserProfile,
    feedback: Optional[str] = None,
    current_definition: Optional[ProblemDefinition] = None
) -> str:
    """
    Formats the prompt with user profile context and optional refinement information.
    
    Args:
        user_profile: The user's academic profile.
        feedback: Optional user feedback for refinement.
        current_definition: Optional current problem definition for refinement.
        
    Returns:
        Formatted prompt string.
    """
    # Format timeline
    timeline_str = f"{user_profile.total_timeline.value} {user_profile.total_timeline.unit}"
    
    # Format lists
    existing_skills_str = ", ".join(user_profile.existing_skills) if user_profile.existing_skills else "None specified"
    missing_skills_str = ", ".join(user_profile.missing_skills) if user_profile.missing_skills else "None"
    constraints_str = ", ".join(user_profile.constraints) if user_profile.constraints else "None"
    
    # Build refinement context
    refinement_context = ""
    if current_definition and feedback:
        refinement_context = f"""
REFINEMENT REQUEST:
User Feedback: {feedback}

Current Problem Definition:
- Problem Statement: {current_definition.problem_statement}
- Main Question: {current_definition.main_research_question}
- Secondary Questions: {', '.join(current_definition.secondary_questions)}
- Key Variables: {', '.join(current_definition.key_variables)}

Please refine the problem definition based on the user's feedback while maintaining coherence and feasibility.
"""
    
    return USER_CONTEXT_TEMPLATE.format(
        field_of_study=user_profile.field_of_study,
        research_area=user_profile.research_area,
        academic_program=user_profile.academic_program,
        weekly_hours=user_profile.weekly_hours,
        timeline=timeline_str,
        existing_skills=existing_skills_str,
        missing_skills=missing_skills_str,
        constraints=constraints_str,
        additional_context=user_profile.additional_context or "None",
        refinement_context=refinement_context
    )


# For backward compatibility and testing
class ProblemFormulationAgent(Agent):
    """Legacy wrapper - use create_problem_formulation_agent() for new code."""
    
    def __init__(self, model: str = DEFAULT_MODEL, **kwargs):
        lit_review_agent = create_literature_review_agent(model=model)
        super().__init__(
            name="problem_formulation_agent",
            model=Gemini(model=model, retry_options=RETRY_CONFIG),
            # output_schema removed
            generate_content_config=types.GenerateContentConfig(
                # response_mime_type removed
            ),
            instruction=SYSTEM_INSTRUCTION,
            tools=[AgentTool(agent=lit_review_agent)],
            **kwargs
        )

