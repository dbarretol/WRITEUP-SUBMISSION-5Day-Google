"""Unit tests for the Data-Collection Agent."""

import pytest
from aida.sub_agents.data_collection import (
    DataCollectionAgent,
    create_data_collection_agent,
    format_prompt_for_data_collection
)
from aida.config import RETRY_CONFIG
from aida.data_models import (
    UserProfile,
    ResearchObjectives,
    MethodologyRecommendation,
    DataCollectionPlan,
    Timeline
)

@pytest.fixture
def agent():
    return DataCollectionAgent()

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
        constraints=["Remote only", "Limited budget"],
        additional_context="Focus on coordination"
    )

@pytest.fixture
def research_objectives():
    return ResearchObjectives(
        general_objective="Develop coordination mechanisms",
        specific_objectives=[
            "Design protocol",
            "Implement algorithm",
            "Evaluate performance"
        ],
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

def test_initialization(agent):
    """Test that the agent initializes correctly."""
    assert agent.name == "data_collection_agent"
    assert agent.model is not None

def test_factory_function():
    """Test the factory function creates a properly configured agent."""
    agent = create_data_collection_agent()
    assert agent.name == "data_collection_agent"
    assert agent.description is not None

def test_retry_config():
    """Test that retry configuration is properly set."""
    assert RETRY_CONFIG.attempts == 5
    assert RETRY_CONFIG.exp_base == 7
    assert 429 in RETRY_CONFIG.http_status_codes

def test_format_prompt(user_profile, research_objectives, methodology):
    """Test prompt formatting with all inputs."""
    prompt = format_prompt_for_data_collection(
        user_profile,
        research_objectives,
        methodology
    )
    
    # Check user profile elements
    assert "Master's" in prompt
    assert "Computer Science" in prompt
    assert "Multi-Agent Systems" in prompt
    assert "15 hours/week" in prompt
    assert "6 months" in prompt
    assert "Python, Data Analysis" in prompt
    assert "Statistical Modeling" in prompt
    assert "Remote only, Limited budget" in prompt
    
    # Check research objectives elements
    assert "Develop coordination mechanisms" in prompt
    assert "Design protocol" in prompt
    
    # Check methodology elements
    assert "Experimental Study" in prompt
    assert "quantitative" in prompt
    assert "Python, Statistical Analysis" in prompt

def test_data_collection_plan_model():
    """Test the DataCollectionPlan data model."""
    plan = DataCollectionPlan(
        collection_techniques=["Simulation", "Performance Measurement"],
        recommended_tools=[
            {
                "name": "Python",
                "purpose": "Simulation implementation",
                "type": "software",
                "accessibility": "free",
                "learning_curve": "moderate"
            }
        ],
        data_sources=["Simulated environments", "Benchmark datasets"],
        estimated_sample_size="1000 simulation runs",
        timeline_breakdown={
            "preparation": {"duration": "2 weeks"},
            "collection": {"duration": "8 weeks"},
            "quality_check": {"duration": "2 weeks"}
        },
        resource_requirements=["Computing resources", "Time: 15 hrs/week"]
    )
    
    assert len(plan.collection_techniques) == 2
    assert len(plan.recommended_tools) == 1
    assert plan.recommended_tools[0]["name"] == "Python"
    assert "1000 simulation runs" in plan.estimated_sample_size
    assert "preparation" in plan.timeline_breakdown
    assert len(plan.resource_requirements) == 2
