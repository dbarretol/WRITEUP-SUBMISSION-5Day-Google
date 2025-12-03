"""Workflow state machine for research proposal orchestrator."""

from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from .config import MAX_REFINEMENTS


class WorkflowState(str, Enum):
    """States in the research proposal workflow."""
    INIT = "init"
    INTERVIEWING = "interviewing"
    PROBLEM_FORMULATION = "problem_formulation"
    OBJECTIVES = "objectives"
    METHODOLOGY = "methodology"
    DATA_COLLECTION = "data_collection"
    QUALITY_CONTROL = "quality_control"
    REFINEMENT = "refinement"
    COMPLETE = "complete"
    ERROR = "error"


class StateTransition(BaseModel):
    """Represents a state transition in the workflow."""
    from_state: WorkflowState
    to_state: WorkflowState
    timestamp: str
    metadata: Dict = Field(default_factory=dict)


class WorkflowContext(BaseModel):
    """Context tracking for the workflow."""
    current_state: WorkflowState = WorkflowState.INIT
    state_history: List[StateTransition] = Field(default_factory=list)
    refinement_count: int = 0
    max_refinements: int = MAX_REFINEMENTS  # Now configurable via config.py
    error_message: Optional[str] = None
    
    def transition_to(self, new_state: WorkflowState, metadata: Dict = None) -> None:
        """
        Transition to a new state and record the transition.
        
        Args:
            new_state: The state to transition to.
            metadata: Optional metadata about the transition.
        """
        from datetime import datetime
        
        transition = StateTransition(
            from_state=self.current_state,
            to_state=new_state,
            timestamp=datetime.now().isoformat(),
            metadata=metadata or {}
        )
        
        self.state_history.append(transition)
        self.current_state = new_state
        
        # Track refinement count
        if new_state == WorkflowState.REFINEMENT:
            self.refinement_count += 1
    
    def can_refine(self) -> bool:
        """Check if refinement is still allowed."""
        return self.refinement_count < self.max_refinements
    
    def get_progress_percentage(self) -> float:
        """Calculate workflow progress as a percentage."""
        state_weights = {
            WorkflowState.INIT: 0,
            WorkflowState.INTERVIEWING: 10,
            WorkflowState.PROBLEM_FORMULATION: 25,
            WorkflowState.OBJECTIVES: 40,
            WorkflowState.METHODOLOGY: 55,
            WorkflowState.DATA_COLLECTION: 70,
            WorkflowState.QUALITY_CONTROL: 85,
            WorkflowState.REFINEMENT: 90,
            WorkflowState.COMPLETE: 100,
            WorkflowState.ERROR: 0
        }
        return state_weights.get(self.current_state, 0)
    
    def get_current_step_name(self) -> str:
        """Get a human-readable name for the current step."""
        step_names = {
            WorkflowState.INIT: "Initializing",
            WorkflowState.INTERVIEWING: "Conducting Interview",
            WorkflowState.PROBLEM_FORMULATION: "Formulating Research Problem",
            WorkflowState.OBJECTIVES: "Defining Research Objectives",
            WorkflowState.METHODOLOGY: "Selecting Methodology",
            WorkflowState.DATA_COLLECTION: "Planning Data Collection",
            WorkflowState.QUALITY_CONTROL: "Validating Proposal Quality",
            WorkflowState.REFINEMENT: "Refining Proposal",
            WorkflowState.COMPLETE: "Proposal Complete",
            WorkflowState.ERROR: "Error Occurred"
        }
        return step_names.get(self.current_state, "Unknown")


# Define valid state transitions
VALID_TRANSITIONS = {
    WorkflowState.INIT: [WorkflowState.INTERVIEWING, WorkflowState.ERROR],
    WorkflowState.INTERVIEWING: [WorkflowState.PROBLEM_FORMULATION, WorkflowState.ERROR],
    WorkflowState.PROBLEM_FORMULATION: [WorkflowState.OBJECTIVES, WorkflowState.ERROR],
    WorkflowState.OBJECTIVES: [WorkflowState.METHODOLOGY, WorkflowState.ERROR],
    WorkflowState.METHODOLOGY: [WorkflowState.DATA_COLLECTION, WorkflowState.ERROR],
    WorkflowState.DATA_COLLECTION: [WorkflowState.QUALITY_CONTROL, WorkflowState.ERROR],
    WorkflowState.QUALITY_CONTROL: [
        WorkflowState.COMPLETE,
        WorkflowState.REFINEMENT,
        WorkflowState.ERROR
    ],
    WorkflowState.REFINEMENT: [WorkflowState.PROBLEM_FORMULATION, WorkflowState.ERROR],
    WorkflowState.COMPLETE: [],
    WorkflowState.ERROR: []
}


def is_valid_transition(from_state: WorkflowState, to_state: WorkflowState) -> bool:
    """
    Check if a state transition is valid.
    
    Args:
        from_state: The current state.
        to_state: The desired next state.
        
    Returns:
        True if the transition is valid, False otherwise.
    """
    return to_state in VALID_TRANSITIONS.get(from_state, [])
