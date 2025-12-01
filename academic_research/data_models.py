"""Data models for the academic research interviewer agent."""

from typing import List, Optional, Dict, Union, Any
from pydantic import BaseModel, Field

class Timeline(BaseModel):
    """Represents the total timeline for the research."""
    value: int
    unit: str = Field(description="Time unit, e.g., 'months', 'years', 'weeks'")

class UserProfile(BaseModel):
    """Structured user profile generated from the interview."""
    academic_program: str = Field(description="The student's academic program (e.g., Bachelor's, Master's)")
    field_of_study: str = Field(description="The general field of study")
    research_area: str = Field(description="Specific research area of interest")
    weekly_hours: int = Field(description="Number of hours available per week")
    total_timeline: Timeline = Field(description="Total duration available for the research")
    existing_skills: List[str] = Field(default_factory=list, description="List of skills the user currently possesses")
    missing_skills: List[str] = Field(default_factory=list, description="List of skills the user needs to acquire")
    constraints: List[str] = Field(default_factory=list, description="Constraints such as fieldwork, software access, etc.")
    additional_context: Optional[str] = Field(None, description="Any other relevant context provided by the user")

class InterviewState(BaseModel):
    """Tracks the state of the interview process."""
    current_question_index: int = 0
    profile_data: Dict[str, Union[str, int, Dict, List[str]]] = Field(default_factory=dict)
    is_complete: bool = False
    conversation_history: List[Dict[str, str]] = Field(default_factory=list)

class LiteratureEntry(BaseModel):
    """Single literature entry from preliminary research."""
    title: str = Field(description="Title of the paper or article")
    url: str = Field(description="URL link to the resource")
    relevance_note: str = Field(description="Brief note on why this is relevant to the research area")
    source: Optional[str] = Field(default=None, description="Source domain (e.g., arxiv.org, ieee.org)")

class LiteratureReviewResult(BaseModel):
    """Results from preliminary literature review conducted by literature_review_agent."""
    queries_performed: List[str] = Field(
        description="List of search queries that were executed"
    )
    literature_found: List[LiteratureEntry] = Field(
        description="List of discovered literature entries"
    )
    search_summary: str = Field(
        description="Summary of search findings and key themes discovered"
    )
    gaps_identified: Optional[List[str]] = Field(
        default=None,
        description="Potential research gaps identified from the literature"
    )

class ProblemDefinition(BaseModel):
    """Structured definition of the research problem."""
    problem_statement: str = Field(description="The core problem statement")
    main_research_question: str = Field(description="The primary research question")
    secondary_questions: List[str] = Field(default_factory=list, description="Secondary research questions")
    key_variables: List[str] = Field(default_factory=list, description="Key variables identified")
    preliminary_literature: List[LiteratureEntry] = Field(
        default_factory=list, 
        description="List of preliminary literature found (from literature_review_agent)"
    )
    refinement_history: List[Dict[str, Any]] = Field(default_factory=list, description="History of refinements made to the problem definition")

class ResearchObjectives(BaseModel):
    """Structured research objectives with feasibility and alignment validation."""
    general_objective: str = Field(description="The overarching general objective of the research")
    specific_objectives: List[str] = Field(description="3-5 specific SMART objectives")
    feasibility_notes: Dict[str, Any] = Field(
        default_factory=dict,
        description="Feasibility assessment including timeline, skills, and resource checks"
    )
    alignment_check: Dict[str, Any] = Field(
        default_factory=dict,
        description="Alignment verification with problem statement and research questions"
    )

class MethodologyRecommendation(BaseModel):
    """Research methodology recommendation with justification and alternatives."""
    recommended_methodology: str = Field(description="The primary recommended research methodology")
    methodology_type: str = Field(description="Type: qualitative, quantitative, or mixed")
    justification: str = Field(description="Detailed justification for the recommended methodology")
    required_skills: List[str] = Field(
        default_factory=list,
        description="Skills required to execute this methodology"
    )
    timeline_fit: Dict[str, Any] = Field(
        default_factory=dict,
        description="Assessment of how the methodology fits within the available timeline"
    )
    alternative_methodologies: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Alternative methodology options with pros and cons"
    )

class DataCollectionPlan(BaseModel):
    """Data collection plan with techniques, tools, and resource requirements."""
    collection_techniques: List[str] = Field(
        description="List of recommended data collection techniques"
    )
    recommended_tools: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Tools and instruments recommended for data collection"
    )
    data_sources: List[str] = Field(
        default_factory=list,
        description="Identified sources for data collection"
    )
    estimated_sample_size: str = Field(
        description="Estimated sample size or data volume needed"
    )
    timeline_breakdown: Dict[str, Any] = Field(
        default_factory=dict,
        description="Timeline breakdown for data collection phases"
    )
    resource_requirements: List[str] = Field(
        default_factory=list,
        description="List of required resources (human, financial, technical)"
    )

class QualityValidation(BaseModel):
    """Quality validation results with multi-criteria assessment."""
    validation_passed: bool = Field(
        description="Whether the proposal passed all validation criteria"
    )
    coherence_score: float = Field(
        description="Score (0-1) indicating internal coherence across components"
    )
    feasibility_score: float = Field(
        description="Score (0-1) indicating overall feasibility"
    )
    overall_quality_score: float = Field(
        description="Overall quality score (0-100) combining coherence and feasibility"
    )
    issues_identified: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of issues found during validation"
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Actionable recommendations for improvement"
    )
    requires_refinement: bool = Field(
        description="Whether refinement is needed"
    )
    refinement_targets: List[str] = Field(
        default_factory=list,
        description="Specific components that need refinement"
    )

