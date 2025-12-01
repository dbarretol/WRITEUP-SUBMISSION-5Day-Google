"""Questionnaire definition for the interviewer agent."""

from typing import List, Optional, Callable, Any
from pydantic import BaseModel

class InterviewQuestion(BaseModel):
    """Represents a single question in the interview."""
    id: str
    text: str
    field_name: str
    validation_func: Optional[Callable[[Any], bool]] = None
    clarification_prompt: Optional[str] = None

def validate_positive_int(value: Any) -> bool:
    try:
        val = int(value)
        return val > 0
    except (ValueError, TypeError):
        return False

def validate_timeline(value: Any) -> bool:
    # This is a placeholder. Complex validation might be needed for the dict structure.
    # For now, we assume the LLM extracts it correctly or we validate the extracted dict later.
    return True

QUESTIONS: List[InterviewQuestion] = [
    InterviewQuestion(
        id="academic_program",
        text="What is your current academic program (e.g., Bachelor's, Master's, PhD)?",
        field_name="academic_program"
    ),
    InterviewQuestion(
        id="field_of_study",
        text="What is your general field of study?",
        field_name="field_of_study"
    ),
    InterviewQuestion(
        id="research_area",
        text="What is your specific research area of interest?",
        field_name="research_area"
    ),
    InterviewQuestion(
        id="weekly_hours",
        text="How many hours per week can you dedicate to this research?",
        field_name="weekly_hours",
        validation_func=validate_positive_int,
        clarification_prompt="Please provide a valid number of hours (e.g., 10, 20)."
    ),
    InterviewQuestion(
        id="total_timeline",
        text="What is your total timeline for this project (e.g., 6 months, 1 year)?",
        field_name="total_timeline",
        validation_func=validate_timeline
    ),
    InterviewQuestion(
        id="existing_skills",
        text="What relevant skills do you currently possess (e.g., Python, Statistics, Qualitative Analysis)?",
        field_name="existing_skills"
    ),
    InterviewQuestion(
        id="missing_skills",
        text="Are there any specific skills you are looking to develop or currently lack?",
        field_name="missing_skills"
    ),
    InterviewQuestion(
        id="constraints",
        text="Do you have any specific constraints (e.g., no fieldwork, limited software access, remote only)?",
        field_name="constraints"
    ),
    InterviewQuestion(
        id="additional_context",
        text="Is there any other context or information you'd like to share?",
        field_name="additional_context"
    )
]
