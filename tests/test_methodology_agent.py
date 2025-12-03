"""Unit tests for the Methodology Agent."""

import pytest
from aida.sub_agents.methodology import (
    MethodologyAgent,
    create_methodology_agent,
    format_prompt_for_methodology
)
from aida.config import RETRY_CONFIG
from aida.data_models import (
    UserProfile,
    ProblemDefinition,
    ResearchObjectives,
    MethodologyRecommendation,
    Timeline
)

@pytest.fixture
def agent():
    return MethodologyAgent()

@pytest.fixture
def user_profile():
    return UserProfile(
        academic_program="Master's",
        field_of_study="Computer Science",
        research_area="Multi-Agent Systems",
        weekly_hours=15,
        total_timeline=Timeline(value=6, unit="months"),
        existing_skills=["Python", "Machine Learning"],
        missing_skills=["Distributed Systems"],
        constraints=["Remote only", "No GPU access"],
        additional_context="Focus on coordination"
    )

@pytest.fixture
def problem_definition():
    return ProblemDefinition(
        problem_statement="Multi-agent systems lack effective coordination mechanisms.",
        main_research_question="How can we improve coordination in multi-agent systems?",
        secondary_questions=["What factors affect coordination?"],
        key_variables=["Coordination efficiency"],
        preliminary_literature=[],
        refinement_history=[]
    )

@pytest.fixture
def research_objectives():
    return ResearchObjectives(
        general_objective="Develop coordination mechanisms for multi-agent systems",
        specific_objectives=[
            "Design a communication protocol",
            "Implement resource allocation algorithm",
            "Evaluate system performance"
        ],
        feasibility_notes={},
        alignment_check={}
    )

def test_initialization(agent):
    """Test that the agent initializes correctly."""
    assert agent.name == "methodology_agent"
    assert agent.model is not None

def test_factory_function():
    """Test the factory function creates a properly configured agent."""
    agent = create_methodology_agent()
    assert agent.name == "methodology_agent"
    assert agent.description is not None

def test_retry_config():
    """Test that retry configuration is properly set."""
    assert RETRY_CONFIG.attempts == 5
    assert RETRY_CONFIG.exp_base == 7
    assert 429 in RETRY_CONFIG.http_status_codes

def test_format_prompt(user_profile, problem_definition, research_objectives):
    """Test prompt formatting with all inputs."""
    prompt = format_prompt_for_methodology(
        user_profile,
        problem_definition,
        research_objectives
    )
    
    # Check user profile elements
    assert "Master's" in prompt
    assert "Computer Science" in prompt
    assert "Multi-Agent Systems" in prompt
    assert "15 hours/week" in prompt
    assert "6 months" in prompt
    assert "Python, Machine Learning" in prompt
    assert "Distributed Systems" in prompt
    assert "Remote only, No GPU access" in prompt
    
    # Check problem definition elements
    assert "Multi-agent systems lack effective coordination" in prompt
    assert "How can we improve coordination" in prompt
    
    # Check research objectives elements
    assert "Develop coordination mechanisms" in prompt
    assert "Design a communication protocol" in prompt

def test_methodology_recommendation_model():
    """Test the MethodologyRecommendation data model."""
    recommendation = MethodologyRecommendation(
        recommended_methodology="Experimental Study",
        methodology_type="quantitative",
        justification="This methodology allows for controlled testing of coordination mechanisms.",
        required_skills=["Python", "Statistical Analysis", "Distributed Systems"],
        timeline_fit={
            "is_feasible": True,
            "estimated_duration": "5 months",
            "key_phases": [
                {"phase": "Design", "duration": "1 month"},
                {"phase": "Implementation", "duration": "2 months"},
                {"phase": "Evaluation", "duration": "2 months"}
            ]
        },
        alternative_methodologies=[
            {
                "name": "Case Study",
                "type": "qualitative",
                "pros": ["In-depth analysis"],
                "cons": ["Limited generalizability"]
            }
        ]
    )
    
    assert recommendation.recommended_methodology == "Experimental Study"
    assert recommendation.methodology_type == "quantitative"
    assert len(recommendation.required_skills) == 3
    assert recommendation.timeline_fit["is_feasible"] is True
    assert len(recommendation.alternative_methodologies) == 1

def test_methodology_type_validation():
    """Test that methodology type accepts valid values."""
    valid_types = ["qualitative", "quantitative", "mixed"]
    
    for mtype in valid_types:
        recommendation = MethodologyRecommendation(
            recommended_methodology="Test",
            methodology_type=mtype,
            justification="Test justification",
            required_skills=[],
            timeline_fit={},
            alternative_methodologies=[]
        )
        assert recommendation.methodology_type == mtype
