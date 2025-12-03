"""Unit tests for the Objectives Agent."""

import pytest
from aida.sub_agents.objectives import (
    ObjectivesAgent,
    create_objectives_agent,
    format_prompt_for_objectives
)
from aida.config import RETRY_CONFIG
from aida.data_models import (
    UserProfile,
    ProblemDefinition,
    ResearchObjectives,
    Timeline
)

@pytest.fixture
def agent():
    return ObjectivesAgent()

@pytest.fixture
def user_profile():
    return UserProfile(
        academic_program="Master's",
        field_of_study="Computer Science",
        research_area="Multi-Agent Systems",
        weekly_hours=15,
        total_timeline=Timeline(value=6, unit="months"),
        existing_skills=["Python", "Machine Learning"],
        missing_skills=["Distributed Systems", "Game Theory"],
        constraints=["Remote only", "No GPU access"],
        additional_context="Focus on coordination mechanisms"
    )

@pytest.fixture
def problem_definition():
    return ProblemDefinition(
        problem_statement="Current multi-agent systems lack effective coordination mechanisms for resource allocation in distributed environments.",
        main_research_question="How can we design coordination mechanisms that improve resource allocation efficiency in multi-agent systems?",
        secondary_questions=[
            "What are the key factors affecting coordination efficiency?",
            "How do different communication protocols impact performance?",
            "What metrics best evaluate coordination effectiveness?"
        ],
        key_variables=[
            "Coordination efficiency",
            "Resource allocation time",
            "Communication overhead",
            "System scalability"
        ],
        preliminary_literature=[],
        refinement_history=[]
    )

def test_initialization(agent):
    """Test that the agent initializes correctly."""
    assert agent.name == "objectives_agent"
    assert agent.model is not None

def test_factory_function():
    """Test the factory function creates a properly configured agent."""
    agent = create_objectives_agent()
    assert agent.name == "objectives_agent"
    assert agent.description is not None

def test_retry_config():
    """Test that retry configuration is properly set."""
    assert RETRY_CONFIG.attempts == 5
    assert RETRY_CONFIG.exp_base == 7
    assert 429 in RETRY_CONFIG.http_status_codes

def test_format_prompt(user_profile, problem_definition):
    """Test prompt formatting with user profile and problem definition."""
    prompt = format_prompt_for_objectives(user_profile, problem_definition)
    
    # Check user profile elements
    assert "Master's" in prompt
    assert "Computer Science" in prompt
    assert "Multi-Agent Systems" in prompt
    assert "15 hours/week" in prompt
    assert "6 months" in prompt
    assert "Python, Machine Learning" in prompt
    assert "Distributed Systems, Game Theory" in prompt
    assert "Remote only, No GPU access" in prompt
    
    # Check problem definition elements
    assert "Current multi-agent systems lack effective coordination" in prompt
    assert "How can we design coordination mechanisms" in prompt
    assert "key factors affecting coordination efficiency" in prompt
    assert "Coordination efficiency" in prompt

def test_research_objectives_model():
    """Test the ResearchObjectives data model."""
    objectives = ResearchObjectives(
        general_objective="Develop coordination mechanisms for multi-agent systems",
        specific_objectives=[
            "Design a protocol for agent communication",
            "Implement resource allocation algorithm",
            "Evaluate system performance"
        ],
        feasibility_notes={
            "timeline_assessment": "Achievable within 6 months",
            "skills_required": ["Distributed Systems"],
            "constraint_compliance": "All objectives can be done remotely"
        },
        alignment_check={
            "general_to_problem": "Directly addresses the coordination problem",
            "coverage_analysis": "All research questions covered"
        }
    )
    
    assert objectives.general_objective == "Develop coordination mechanisms for multi-agent systems"
    assert len(objectives.specific_objectives) == 3
    assert "timeline_assessment" in objectives.feasibility_notes
    assert "general_to_problem" in objectives.alignment_check
