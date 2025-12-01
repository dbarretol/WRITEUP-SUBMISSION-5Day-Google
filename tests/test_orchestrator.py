"""Unit tests for the Research Proposal Orchestrator."""

import pytest
import json
from unittest.mock import MagicMock, AsyncMock, patch
from academic_research.orchestrator import ResearchProposalOrchestrator
from academic_research.workflow_state import WorkflowState
from academic_research.data_models import (
    UserProfile,
    ProblemDefinition,
    ResearchObjectives,
    MethodologyRecommendation,
    DataCollectionPlan,
    QualityValidation,
    Timeline
)

@pytest.fixture
def orchestrator():
    return ResearchProposalOrchestrator()

@pytest.fixture
def mock_runner():
    runner = MagicMock()
    runner.session_service.create_session = AsyncMock(return_value=MagicMock())
    return runner

@pytest.fixture
def mock_agents():
    return {
        'interviewer': MagicMock(),
        'problem_formulation': MagicMock(),
        'objectives': MagicMock(),
        'methodology': MagicMock(),
        'data_collection': MagicMock(),
        'quality_control': MagicMock()
    }

@pytest.fixture
def sample_data():
    user_profile = UserProfile(
        academic_program="PhD",
        field_of_study="AI",
        research_area="Agents",
        weekly_hours=20,
        total_timeline=Timeline(value=12, unit="months"),
        existing_skills=["Python"],
        missing_skills=[],
        constraints=[]
    )
    
    problem_definition = ProblemDefinition(
        problem_statement="Test problem",
        main_research_question="Test question",
        secondary_questions=[],
        key_variables=[],
        preliminary_literature=[],
        refinement_history=[]
    )
    
    return {
        'user_profile': user_profile,
        'problem_definition': problem_definition
    }

def test_initialization(orchestrator):
    """Test orchestrator initialization."""
    assert orchestrator.context.current_state == WorkflowState.INIT
    assert orchestrator.context.refinement_count == 0

def test_valid_transition(orchestrator):
    """Test valid state transitions."""
    orchestrator._transition_to(WorkflowState.INTERVIEWING)
    assert orchestrator.context.current_state == WorkflowState.INTERVIEWING
    
    orchestrator._transition_to(WorkflowState.PROBLEM_FORMULATION)
    assert orchestrator.context.current_state == WorkflowState.PROBLEM_FORMULATION

def test_invalid_transition(orchestrator):
    """Test invalid state transitions raise error."""
    with pytest.raises(ValueError):
        orchestrator._transition_to(WorkflowState.COMPLETE)

@pytest.mark.asyncio
async def test_run_workflow_success(orchestrator, mock_runner, mock_agents, sample_data):
    """Test successful workflow execution."""
    
    # Mock agent responses
    with patch.object(orchestrator, '_execute_agent', new_callable=AsyncMock) as mock_execute:
        # Problem Formulation
        mock_execute.side_effect = [
            json.dumps(sample_data['problem_definition'].model_dump()),
            json.dumps({
                "general_objective": "Test obj",
                "specific_objectives": ["Obj 1"],
                "feasibility_notes": {},
                "alignment_check": {}
            }),
            json.dumps({
                "recommended_methodology": "Test method",
                "methodology_type": "qualitative",
                "justification": "Test",
                "required_skills": [],
                "timeline_fit": {},
                "alternative_methodologies": []
            }),
            json.dumps({
                "collection_techniques": ["Test tech"],
                "recommended_tools": [],
                "data_sources": [],
                "estimated_sample_size": "10",
                "timeline_breakdown": {},
                "resource_requirements": []
            }),
            json.dumps({
                "validation_passed": True,
                "coherence_score": 0.9,
                "feasibility_score": 0.9,
                "overall_quality_score": 90.0,
                "issues_identified": [],
                "recommendations": [],
                "requires_refinement": False,
                "refinement_targets": []
            })
        ]
        
        result = await orchestrator.run_workflow(
            mock_agents,
            mock_runner,
            initial_profile=sample_data['user_profile']
        )
        
        assert result['success'] is True
        assert result['metadata']['validation_passed'] is True
        assert orchestrator.context.current_state == WorkflowState.COMPLETE

@pytest.mark.asyncio
async def test_refinement_loop(orchestrator, mock_runner, mock_agents, sample_data):
    """Test refinement loop logic."""
    
    # Mock responses: 1st QC fails, 2nd QC passes
    with patch.object(orchestrator, '_execute_agent', new_callable=AsyncMock) as mock_execute:
        mock_execute.side_effect = [
            # Iteration 1
            json.dumps(sample_data['problem_definition'].model_dump()), # Problem
            json.dumps({"general_objective": "Obj", "specific_objectives": [], "feasibility_notes": {}, "alignment_check": {}}), # Obj
            json.dumps({"recommended_methodology": "Meth", "methodology_type": "qual", "justification": "", "required_skills": [], "timeline_fit": {}, "alternative_methodologies": []}), # Method
            json.dumps({"collection_techniques": [], "recommended_tools": [], "data_sources": [], "estimated_sample_size": "", "timeline_breakdown": {}, "resource_requirements": []}), # Data
            json.dumps({ # QC Fail
                "validation_passed": False,
                "coherence_score": 0.5,
                "feasibility_score": 0.5,
                "overall_quality_score": 50.0,
                "issues_identified": [],
                "recommendations": ["Refine problem"],
                "requires_refinement": True,
                "refinement_targets": ["problem_definition"]
            }),
            
            # Iteration 2 (Refinement)
            json.dumps(sample_data['problem_definition'].model_dump()), # Problem (refined)
            json.dumps({"general_objective": "Obj", "specific_objectives": [], "feasibility_notes": {}, "alignment_check": {}}), # Obj
            json.dumps({"recommended_methodology": "Meth", "methodology_type": "qual", "justification": "", "required_skills": [], "timeline_fit": {}, "alternative_methodologies": []}), # Method
            json.dumps({"collection_techniques": [], "recommended_tools": [], "data_sources": [], "estimated_sample_size": "", "timeline_breakdown": {}, "resource_requirements": []}), # Data
            json.dumps({ # QC Pass
                "validation_passed": True,
                "coherence_score": 0.9,
                "feasibility_score": 0.9,
                "overall_quality_score": 90.0,
                "issues_identified": [],
                "recommendations": [],
                "requires_refinement": False,
                "refinement_targets": []
            })
        ]
        
        result = await orchestrator.run_workflow(
            mock_agents,
            mock_runner,
            initial_profile=sample_data['user_profile']
        )
        
        assert result['success'] is True
        assert result['metadata']['refinement_iterations'] == 1
        assert orchestrator.context.current_state == WorkflowState.COMPLETE
