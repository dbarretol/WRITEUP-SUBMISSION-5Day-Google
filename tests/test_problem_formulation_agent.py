"""Unit tests for the Problem-Formulation Agent."""

import pytest
from google.adk.tools import AgentTool
from academic_research.sub_agents.problem_formulation import (
    ProblemFormulationAgent,
    create_problem_formulation_agent,
    format_prompt_for_user_profile
)
from academic_research.config import RETRY_CONFIG
from academic_research.data_models import UserProfile, ProblemDefinition, Timeline

@pytest.fixture
def agent():
    return ProblemFormulationAgent()

@pytest.fixture
def user_profile():
    return UserProfile(
        academic_program="Master's",
        field_of_study="Computer Science",
        research_area="AI Agents",
        weekly_hours=20,
        total_timeline=Timeline(value=6, unit="months"),
        existing_skills=["Python", "LLMs"],
        missing_skills=["Reinforcement Learning"],
        constraints=["No GPU access"],
        additional_context="Interested in multi-agent systems."
    )

def test_initialization(agent):
    """Test that the agent initializes correctly with proper configuration."""
    assert agent.name == "problem_formulation_agent"
    
    # --- FIXED ASSERTION ---
    # Verify that the tools list contains an AgentTool (the sub-agent wrapper)
    assert any(isinstance(tool, AgentTool) for tool in agent.tools)
    
    # Optionally, verify it delegates to the correct agent
    sub_agent_tool = next(t for t in agent.tools if isinstance(t, AgentTool))
    assert sub_agent_tool.agent.name == "literature_review_agent"

def test_factory_function():
    """Test the factory function creates a properly configured agent."""
    agent = create_problem_formulation_agent()
    assert agent.name == "problem_formulation_agent"
    assert agent.description is not None
    
    # --- FIXED ASSERTION ---
    assert any(isinstance(tool, AgentTool) for tool in agent.tools)
    sub_agent_tool = next(t for t in agent.tools if isinstance(t, AgentTool))
    assert sub_agent_tool.agent.name == "literature_review_agent"

def test_retry_config():
    """Test that retry configuration is properly set."""
    assert RETRY_CONFIG.attempts == 5
    assert RETRY_CONFIG.exp_base == 7
    assert 429 in RETRY_CONFIG.http_status_codes

def test_format_prompt_initial(user_profile):
    """Test prompt formatting for initial problem definition."""
    prompt = format_prompt_for_user_profile(user_profile)
    
    assert "Computer Science" in prompt
    assert "AI Agents" in prompt
    assert "Master's" in prompt
    assert "20 hours/week" in prompt
    assert "6 months" in prompt
    assert "Python, LLMs" in prompt
    assert "Reinforcement Learning" in prompt
    assert "No GPU access" in prompt

def test_format_prompt_refinement(user_profile):
    """Test prompt formatting for refinement with feedback."""
    current_def = ProblemDefinition(
        problem_statement="Old statement",
        main_research_question="Old question",
        secondary_questions=["Q1", "Q2"],
        key_variables=["V1", "V2"],
        preliminary_literature=[],
        refinement_history=[]
    )
    
    prompt = format_prompt_for_user_profile(
        user_profile,
        feedback="Make it more specific",
        current_definition=current_def
    )
    
    assert "REFINEMENT REQUEST" in prompt
    assert "Make it more specific" in prompt
    assert "Old statement" in prompt
    assert "Old question" in prompt