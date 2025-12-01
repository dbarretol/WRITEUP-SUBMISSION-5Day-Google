"""Unit tests for state management and proposal building."""

import pytest
import os
import shutil
import json
from datetime import datetime
from academic_research.state_manager import StateManager
from academic_research.proposal_builder import ProposalBuilder
from academic_research.workflow_state import WorkflowContext, WorkflowState
from academic_research.data_models import ProblemDefinition

@pytest.fixture
def clean_state_dir():
    base_dir = ".gemini/test_state"
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    yield base_dir
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)

def test_state_persistence(clean_state_dir):
    """Test saving and loading workflow state."""
    manager = StateManager(base_dir=clean_state_dir)
    context = WorkflowContext(current_state=WorkflowState.PROBLEM_FORMULATION)
    run_id = "test_run_123"
    
    # Save
    path = manager.save_workflow_state(context, run_id)
    assert os.path.exists(path)
    
    # Load
    loaded_context = manager.load_workflow_state(run_id)
    assert loaded_context is not None
    assert loaded_context.current_state == WorkflowState.PROBLEM_FORMULATION

def test_proposal_snapshots(clean_state_dir):
    """Test saving and listing proposal snapshots."""
    manager = StateManager(base_dir=clean_state_dir)
    run_id = "test_run_456"
    data = {"key": "value"}
    
    # Save snapshot
    path = manager.save_proposal_snapshot(data, run_id, iteration=1)
    assert os.path.exists(path)
    
    # List snapshots
    snapshots = manager.list_snapshots(run_id)
    assert len(snapshots) == 1
    assert snapshots[0]["iteration"] == 1
    assert snapshots[0]["tag"] == "snapshot"

def test_proposal_builder_markdown():
    """Test Markdown generation."""
    proposal = {
        "problem_definition": {
            "problem_statement": "Test Problem",
            "main_research_question": "Test Question?"
        },
        "research_objectives": {
            "general_objective": "Test Objective",
            "specific_objectives": ["Obj 1", "Obj 2"]
        }
    }
    
    md = ProposalBuilder.to_markdown(proposal)
    
    assert "# Research Proposal Draft" in md
    assert "## 1. Introduction" in md
    assert "**Problem Statement:**\nTest Problem" in md
    assert "## 2. Research Objectives" in md
    assert "- Obj 1" in md
