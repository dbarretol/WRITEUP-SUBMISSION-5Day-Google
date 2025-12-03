"""Unit tests for the Quality-Control Agent."""

import pytest
from aida.sub_agents.quality_control import (
    QualityControlAgent,
    create_quality_control_agent,
    format_prompt_for_quality_control
)
from aida.config import RETRY_CONFIG
from aida.data_models import (
    UserProfile,
    ProblemDefinition,
    ResearchObjectives,
    MethodologyRecommendation,
    DataCollectionPlan,
    QualityValidation,
    Timeline
)

@pytest.fixture
def agent():
    return QualityControlAgent()

@pytest.fixture
def user_profile():
    return UserProfile(
        academic_program="Master's",
        field_of_study="Computer Science",
        research_area="Multi-Agent Systems",
        weekly_hours=15,
        total_timeline=Timeline(value=6, unit="months"),
        existing_skills=["Python", "Data Analysis"],
        missing_skills=["Statistical Modeling"],
        constraints=["Remote only"],
        additional_context="Focus on coordination"
    )

@pytest.fixture
def problem_definition():
    return ProblemDefinition(
        problem_statement="Multi-agent systems lack effective coordination mechanisms.",
        main_research_question="How can we improve coordination?",
        secondary_questions=["What factors affect coordination?"],
        key_variables=["Coordination efficiency"],
        preliminary_literature=[],
        refinement_history=[]
    )

@pytest.fixture
def research_objectives():
    return ResearchObjectives(
        general_objective="Develop coordination mechanisms",
        specific_objectives=["Design protocol", "Implement algorithm", "Evaluate performance"],
        feasibility_notes={},
        alignment_check={}
    )

@pytest.fixture
def methodology():
    return MethodologyRecommendation(
        recommended_methodology="Experimental Study",
        methodology_type="quantitative",
        justification="Allows controlled testing",
        required_skills=["Python", "Statistical Analysis"],
        timeline_fit={"is_feasible": True},
        alternative_methodologies=[]
    )

@pytest.fixture
def data_collection():
    return DataCollectionPlan(
        collection_techniques=["Simulation", "Performance Measurement"],
        recommended_tools=[
            {"name": "Python", "accessibility": "free", "type": "software"}
        ],
        data_sources=["Simulated environments"],
        estimated_sample_size="1000 simulation runs",
        timeline_breakdown={"total_duration": "8 weeks"},
        resource_requirements=["Computing resources"]
    )

def test_initialization(agent):
    """Test that the agent initializes correctly."""
    assert agent.name == "quality_control_agent"
    assert agent.model is not None

def test_factory_function():
    """Test the factory function creates a properly configured agent."""
    agent = create_quality_control_agent()
    assert agent.name == "quality_control_agent"
    assert agent.description is not None

def test_retry_config():
    """Test that retry configuration is properly set."""
    assert RETRY_CONFIG.attempts == 5
    assert RETRY_CONFIG.exp_base == 7
    assert 429 in RETRY_CONFIG.http_status_codes

def test_format_prompt(user_profile, problem_definition, research_objectives, methodology, data_collection):
    """Test prompt formatting with all inputs."""
    prompt = format_prompt_for_quality_control(
        user_profile,
        problem_definition,
        research_objectives,
        methodology,
        data_collection
    )
    
    # Check user profile elements
    assert "Master's" in prompt
    assert "Computer Science" in prompt
    assert "15 hours/week" in prompt
    assert "6 months" in prompt
    
    # Check problem definition
    assert "Multi-agent systems lack effective coordination" in prompt
    assert "How can we improve coordination" in prompt
    
    # Check objectives
    assert "Develop coordination mechanisms" in prompt
    
    # Check methodology
    assert "Experimental Study" in prompt
    assert "quantitative" in prompt
    
    # Check data collection
    assert "Simulation" in prompt
    assert "1000 simulation runs" in prompt

def test_quality_validation_model():
    """Test the QualityValidation data model."""
    validation = QualityValidation(
        validation_passed=True,
        coherence_score=0.85,
        feasibility_score=0.80,
        overall_quality_score=82.5,
        issues_identified=[
            {
                "severity": "minor",
                "component": "methodology",
                "description": "Timeline might be tight",
                "impact": "May need to adjust scope"
            }
        ],
        recommendations=["Consider adding buffer time"],
        requires_refinement=False,
        refinement_targets=[]
    )
    
    assert validation.validation_passed is True
    assert validation.coherence_score == 0.85
    assert validation.feasibility_score == 0.80
    assert len(validation.issues_identified) == 1
    assert validation.issues_identified[0]["severity"] == "minor"
    assert len(validation.recommendations) == 1
    assert validation.requires_refinement is False

def test_quality_validation_scores():
    """Test that validation scores are within valid range."""
    validation = QualityValidation(
        validation_passed=False,
        coherence_score=0.65,
        feasibility_score=0.60,
        overall_quality_score=62.5,
        issues_identified=[],
        recommendations=[],
        requires_refinement=True,
        refinement_targets=["problem_definition"]
    )
    
    assert 0.0 <= validation.coherence_score <= 1.0
    assert 0.0 <= validation.feasibility_score <= 1.0
    assert validation.requires_refinement is True
    assert "problem_definition" in validation.refinement_targets
