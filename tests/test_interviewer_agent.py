"""Unit tests for the Interviewer Agent."""

import pytest
from unittest.mock import MagicMock, patch
import json
from academic_research.sub_agents.interviewer import InterviewerAgent
from academic_research.data_models import InterviewState

@pytest.fixture
def agent():
    return InterviewerAgent()

@pytest.fixture
def initial_state():
    return InterviewState()

def test_initial_question(agent, initial_state):
    # Test that the first question is correct
    assert agent.questions[0].id == "academic_program"
    assert initial_state.current_question_index == 0

def test_process_turn_valid_answer(agent, initial_state):
    # Mock LLM response
    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "extracted_value": "Master's",
        "next_message": "What is your general field of study?",
        "is_valid": True
    })
    
    with patch.object(agent.client.models, 'generate_content', return_value=mock_response):
        result = agent.process_turn("I am in a Master's program", initial_state)
        
        assert result["state"].profile_data["academic_program"] == "Master's"
        assert result["state"].current_question_index == 1
        assert result["is_complete"] is False
        assert result["response"] == "What is your general field of study?"

def test_process_turn_invalid_answer(agent, initial_state):
    # Mock LLM response for invalid input
    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "extracted_value": None,
        "next_message": "Please specify if it's Bachelor's, Master's, or PhD.",
        "is_valid": False
    })
    
    with patch.object(agent.client.models, 'generate_content', return_value=mock_response):
        result = agent.process_turn("I don't know", initial_state)
        
        assert "academic_program" not in result["state"].profile_data
        assert result["state"].current_question_index == 0
        assert result["is_complete"] is False
        assert result["response"] == "Please specify if it's Bachelor's, Master's, or PhD."

def test_completion(agent, initial_state):
    # Fast forward to the last question
    initial_state.current_question_index = len(agent.questions) - 1
    
    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "extracted_value": "No other context",
        "next_message": "Thank you!",
        "is_valid": True
    })
    
    with patch.object(agent.client.models, 'generate_content', return_value=mock_response):
        result = agent.process_turn("No", initial_state)
        
        assert result["is_complete"] is True
        assert result["state"].is_complete is True
        assert "final_profile" in result
