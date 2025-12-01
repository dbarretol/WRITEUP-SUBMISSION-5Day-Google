"""Quality-Control Agent for academic research proposal validation."""

import os
from typing import Dict, Any, List, Optional
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.genai import types

from ...data_models import (
    UserProfile,
    ProblemDefinition,
    ResearchObjectives,
    MethodologyRecommendation,
    DataCollectionPlan,
    QualityValidation
)
from ...config import RETRY_CONFIG, DEFAULT_MODEL

from .prompt import SYSTEM_INSTRUCTION, USER_CONTEXT_TEMPLATE

def create_quality_control_agent(model: str = DEFAULT_MODEL) -> Agent:
    """
    Factory function to create a Quality-Control Agent.
    
    Args:
        model: The Gemini model to use.
        
    Returns:
        Configured Agent instance.
    """
    return Agent(
        name="quality_control_agent",
        model=Gemini(model=model, retry_options=RETRY_CONFIG),
        output_schema=QualityValidation,
        generate_content_config=types.GenerateContentConfig(
            temperature=0.1,
            response_mime_type="application/json",
        ),
        instruction=SYSTEM_INSTRUCTION,
        description=(
            "Validates research proposals across multiple criteria, "
            "identifies issues, and manages refinement loops to ensure "
            "proposal quality and coherence."
        )
    )

def format_prompt_for_quality_control(
    user_profile: UserProfile,
    problem_definition: ProblemDefinition,
    research_objectives: ResearchObjectives,
    methodology: MethodologyRecommendation,
    data_collection: DataCollectionPlan
) -> str:
    """
    Formats the prompt with all proposal components for validation.
    
    Args:
        user_profile: The user's academic profile.
        problem_definition: The defined research problem.
        research_objectives: The research objectives.
        methodology: The recommended methodology.
        data_collection: The data collection plan.
        
    Returns:
        Formatted prompt string.
    """
    # Format timeline
    timeline_str = f"{user_profile.total_timeline.value} {user_profile.total_timeline.unit}"
    
    # Format lists
    existing_skills_str = ", ".join(user_profile.existing_skills) if user_profile.existing_skills else "None"
    missing_skills_str = ", ".join(user_profile.missing_skills) if user_profile.missing_skills else "None"
    constraints_str = ", ".join(user_profile.constraints) if user_profile.constraints else "None"
    
    secondary_questions_str = "; ".join(problem_definition.secondary_questions) if problem_definition.secondary_questions else "None"
    key_variables_str = ", ".join(problem_definition.key_variables) if problem_definition.key_variables else "None"
    
    specific_objectives_str = "; ".join(research_objectives.specific_objectives) if research_objectives.specific_objectives else "None"
    
    methodology_skills_str = ", ".join(methodology.required_skills) if methodology.required_skills else "None"
    
    collection_techniques_str = ", ".join(data_collection.collection_techniques) if data_collection.collection_techniques else "None"
    
    # Summarize tools
    tools_summary = []
    for tool in data_collection.recommended_tools[:3]:  # First 3 tools
        tools_summary.append(f"{tool.get('name', 'Unknown')} ({tool.get('accessibility', 'unknown')})")
    recommended_tools_summary_str = ", ".join(tools_summary) if tools_summary else "None"
    
    # Get data collection timeline
    dc_timeline = data_collection.timeline_breakdown.get('total_duration', 'Not specified')
    
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
        key_variables=key_variables_str,
        general_objective=research_objectives.general_objective,
        specific_objectives=specific_objectives_str,
        recommended_methodology=methodology.recommended_methodology,
        methodology_type=methodology.methodology_type,
        methodology_skills=methodology_skills_str,
        collection_techniques=collection_techniques_str,
        recommended_tools_summary=recommended_tools_summary_str,
        estimated_sample_size=data_collection.estimated_sample_size,
        data_collection_timeline=dc_timeline
    )


# For backward compatibility and testing
class QualityControlAgent(Agent):
    """Legacy wrapper - use create_quality_control_agent() for new code."""
    
    def __init__(self, model: str = DEFAULT_MODEL, **kwargs):
        super().__init__(
            name="quality_control_agent",
            model=Gemini(model=model, retry_options=RETRY_CONFIG),
            output_schema=QualityValidation,
            generate_content_config=types.GenerateContentConfig(
                response_mime_type="application/json"
            ),
            instruction=SYSTEM_INSTRUCTION,
            **kwargs
        )
