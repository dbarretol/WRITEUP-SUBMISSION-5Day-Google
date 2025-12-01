"""State management for workflow persistence and proposal versioning."""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from .workflow_state import WorkflowContext

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StateManager:
    """Manages persistence of workflow state and proposal snapshots."""
    
    def __init__(self, base_dir: str = ".gemini"):
        self.base_dir = base_dir
        self.state_dir = os.path.join(base_dir, "state")
        self.snapshot_dir = os.path.join(base_dir, "snapshots")
        
        os.makedirs(self.state_dir, exist_ok=True)
        os.makedirs(self.snapshot_dir, exist_ok=True)
    
    def save_workflow_state(self, context: WorkflowContext, run_id: str) -> str:
        """
        Save the current workflow state.
        
        Args:
            context: The workflow context to save.
            run_id: Unique identifier for the workflow run.
            
        Returns:
            Path to the saved state file.
        """
        file_path = os.path.join(self.state_dir, f"{run_id}_state.json")
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(context.model_dump_json(indent=2))
            logger.info(f"Saved workflow state to {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Failed to save workflow state: {e}")
            raise
    
    def load_workflow_state(self, run_id: str) -> Optional[WorkflowContext]:
        """
        Load workflow state.
        
        Args:
            run_id: Unique identifier for the workflow run.
            
        Returns:
            The loaded WorkflowContext or None if not found.
        """
        file_path = os.path.join(self.state_dir, f"{run_id}_state.json")
        if not os.path.exists(file_path):
            return None
            
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return WorkflowContext(**data)
        except Exception as e:
            logger.error(f"Failed to load workflow state: {e}")
            raise
    
    def save_proposal_snapshot(
        self, 
        proposal_data: Dict[str, Any], 
        run_id: str, 
        iteration: int,
        tag: str = "snapshot"
    ) -> str:
        """
        Save a snapshot of the proposal.
        
        Args:
            proposal_data: Dictionary containing proposal components.
            run_id: Unique identifier for the workflow run.
            iteration: Current refinement iteration.
            tag: Optional tag for the snapshot (e.g., "initial", "refined").
            
        Returns:
            Path to the saved snapshot file.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{run_id}_iter{iteration}_{tag}_{timestamp}.json"
        file_path = os.path.join(self.snapshot_dir, filename)
        
        try:
            # Add metadata to snapshot
            snapshot = {
                "run_id": run_id,
                "iteration": iteration,
                "tag": tag,
                "timestamp": timestamp,
                "data": proposal_data
            }
            
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(snapshot, f, indent=2, default=str)
            
            logger.info(f"Saved proposal snapshot to {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Failed to save proposal snapshot: {e}")
            raise
    
    def list_snapshots(self, run_id: str) -> List[Dict[str, Any]]:
        """
        List all snapshots for a specific run.
        
        Args:
            run_id: Unique identifier for the workflow run.
            
        Returns:
            List of snapshot metadata dictionaries, sorted by timestamp.
        """
        snapshots = []
        for filename in os.listdir(self.snapshot_dir):
            if filename.startswith(f"{run_id}_") and filename.endswith(".json"):
                file_path = os.path.join(self.snapshot_dir, filename)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        # Extract metadata only
                        snapshots.append({
                            "filename": filename,
                            "path": file_path,
                            "iteration": data.get("iteration"),
                            "tag": data.get("tag"),
                            "timestamp": data.get("timestamp")
                        })
                except Exception as e:
                    logger.warning(f"Failed to read snapshot {filename}: {e}")
        
        # Sort by timestamp
        return sorted(snapshots, key=lambda x: x.get("timestamp", ""))
