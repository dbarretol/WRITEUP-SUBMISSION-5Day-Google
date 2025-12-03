"""Research Proposal Orchestrator - coordinates all agents in the workflow."""

import asyncio
import json
import logging
import gc
from typing import Dict, Any, Optional, Callable
from datetime import datetime

from google.genai import types
from google.adk.runners import InMemoryRunner 
from .workflow_state import WorkflowState, WorkflowContext, is_valid_transition
from .data_models import (
    UserProfile,
    ProblemDefinition,
    ResearchObjectives,
    MethodologyRecommendation,
    DataCollectionPlan,
    QualityValidation
)
from .sub_agents.problem_formulation import format_prompt_for_user_profile
from .sub_agents.objectives import format_prompt_for_objectives
from .sub_agents.methodology import format_prompt_for_methodology
from .sub_agents.data_collection import format_prompt_for_data_collection
from .sub_agents.quality_control import format_prompt_for_quality_control

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResearchProposalOrchestrator:
    """
    Orchestrates the complete research proposal generation workflow.
    
    Coordinates all agents from WP2.1 to WP2.6 in sequence, manages state,
    handles refinement loops, and tracks progress.
    """
    
    def __init__(
        self,
        progress_callback: Optional[Callable[[str, float], None]] = None
    ):
        """
        Initialize the orchestrator.
        
        Args:
            progress_callback: Optional callback for progress updates.
                               Signature: callback(step_name: str, percentage: float)
        """
        self.context = WorkflowContext()
        self.progress_callback = progress_callback
        
        # Storage for agent outputs
        self.user_profile: Optional[UserProfile] = None
        self.problem_definition: Optional[ProblemDefinition] = None
        self.research_objectives: Optional[ResearchObjectives] = None
        self.methodology: Optional[MethodologyRecommendation] = None
        self.data_collection: Optional[DataCollectionPlan] = None
        self.quality_validation: Optional[QualityValidation] = None
        
        logger.info("Orchestrator initialized")
    
    def _report_progress(self) -> None:
        """Report current progress to callback if provided."""
        if self.progress_callback:
            step_name = self.context.get_current_step_name()
            
            # Add refinement iteration info if in refinement state
            if self.context.current_state == WorkflowState.REFINEMENT:
                step_name = f"🔄 Refinement Loop {self.context.refinement_count}/{self.context.max_refinements} - {step_name}"
            
            percentage = self.context.get_progress_percentage()
            self.progress_callback(step_name, percentage)
            logger.info(f"Progress: {step_name} ({percentage}%)")
    
    def _transition_to(self, new_state: WorkflowState, metadata: Dict = None) -> None:
        """
        Transition to a new state with validation.
        
        Args:
            new_state: The state to transition to.
            metadata: Optional metadata about the transition.
            
        Raises:
            ValueError: If the transition is invalid.
        """
        if not is_valid_transition(self.context.current_state, new_state):
            raise ValueError(
                f"Invalid transition from {self.context.current_state} to {new_state}"
            )
        
        self.context.transition_to(new_state, metadata)
        self._report_progress()
        logger.info(f"Transitioned to state: {new_state}")
    
    def _extract_json_from_response(self, response_text: str, required_keys: Optional[list] = None) -> Dict[str, Any]:
        """
        Extract JSON from agent response, handling various formats.
        
        Tries multiple strategies to extract valid JSON:
        1. Direct parsing (if response is pure JSON)
        2. Remove markdown code fences
        3. Extract JSON object from mixed content
        
        Args:
            response_text: The raw response from the agent
            required_keys: Optional list of keys that must be present in the extracted JSON
            
        Returns:
            Parsed JSON as a dictionary
            
        Raises:
            ValueError: If no valid JSON can be extracted
        """
        import re
        
        # Strategy 1: Try direct parsing
        try:
            data = json.loads(response_text.strip())
            if not required_keys or all(key in data for key in required_keys):
                return data
        except json.JSONDecodeError:
            pass
        
        # Strategy 2: Remove markdown code fences
        cleaned = response_text.replace("```json", "").replace("```", "").strip()
        try:
            data = json.loads(cleaned)
            if not required_keys or all(key in data for key in required_keys):
                return data
        except json.JSONDecodeError:
            pass
        
        # Strategy 3: Extract JSON object using regex
        # Look for content between { and } that appears to be JSON
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(json_pattern, response_text, re.DOTALL)
        
        for match in matches:
            try:
                # Try to parse this potential JSON
                data = json.loads(match)
                # Verify it has expected keys for our use case
                if isinstance(data, dict) and len(data) > 0:
                    if required_keys:
                        if all(key in data for key in required_keys):
                            logger.info(f"Successfully extracted JSON with required keys: {required_keys}")
                            return data
                        else:
                            # Continue searching if keys are missing
                            continue
                    else:
                        logger.info(f"Successfully extracted JSON from mixed content")
                        return data
            except json.JSONDecodeError:
                continue
        
        # If all strategies fail, raise an error with helpful context
        raise ValueError(
            f"Could not extract valid JSON from response. "
            f"Response preview (first 300 chars): {response_text[:300]}"
        )
    

    async def _execute_agent(self, agent, prompt: str, runner_unused=None) -> str:
        """
        Helper to execute a non-interactive agent.
        Creates a temporary runner to ensure Tools (like Google Search) are executed.
        """
        APP_NAME = "orchestrator_execution"

        # 1. Initialize Runner with context manager for cleanup
        async with InMemoryRunner(agent=agent, app_name=APP_NAME) as temp_runner:
            # 2. Create Session
            session = await temp_runner.session_service.create_session(
                app_name=APP_NAME,
                user_id="orchestrator"
            )
            
            content = types.Content(parts=[types.Part(text=prompt)])
            
            final_response_text = ""
            
            logger.info(f"--- Executing Agent: {agent.name} ---")

            # 3. Run the agent loop
            async for event in temp_runner.run_async(
                user_id=session.user_id,
                session_id=session.id,
                new_message=content
            ):
                # DEBUG LOGGING: See what the agent is emitting
                if event.content and event.content.parts:
                     for part in event.content.parts:
                        # Check for Function Calls (Tools)
                        if part.function_call:
                            logger.info(f"[Agent Tool Call] {part.function_call.name}")
                        
                        # Check for Function Response (Tool Output)
                        if part.function_response:
                            resp_content = part.function_response.response
                            logger.info(f"[Agent Tool Output] {part.function_response.name}: {str(resp_content)[:500]}...")

                        # Check for Text (The answer)
                        if hasattr(part, 'text') and part.text:
                            text_preview = part.text[:50].replace('\n', ' ')
                            logger.info(f"[Agent Text Event] Length: {len(part.text)} chars | Preview: {text_preview}...")
                            
                            # We overwrite the final response with the latest text we see.
                            # As the agent works (Think -> Tool -> Think -> Answer), 
                            # the last text event is usually the final answer.
                            if part.text.strip():
                                final_response_text = part.text

            logger.info(f"--- Agent {agent.name} Finished ---")

            # 4. Validation
            if not final_response_text:
                 # If we got no text, the agent might have failed silently or only returned tool outputs.
                 logger.error(f"Agent {agent.name} returned NO text. Checking history...")
                 
                 # Fallback: Check session history as a last resort
                 history = await temp_runner.session_service.get_history(
                     app_name=APP_NAME, 
                     session_id=session.id
                 )
                 if history and history[-1].parts:
                     last_part = history[-1].parts[0]
                     if hasattr(last_part, 'text') and last_part.text:
                         final_response_text = last_part.text
                         logger.info("Recovered text from history.")
                 
                 if not final_response_text:
                     raise ValueError(f"Agent {agent.name} did not return any text response (Empty Output).")

        # CRITICAL: Sleep AFTER the async with block exits
        # The context manager closes the session, but aiohttp needs time to release TCP connectors
        await asyncio.sleep(0.25)
        
        if not final_response_text:
            raise ValueError(f"Agent {agent.name} did not return any text response.")
        
        return final_response_text

    async def run_interviewer(self, interviewer_agent, runner) -> UserProfile:
        """
        Run the interviewer agent to collect user profile.
        
        Args:
            interviewer_agent: The interviewer agent instance.
            runner: The ADK runner instance.
            
        Returns:
            UserProfile: The collected user profile.
        """
        self._transition_to(WorkflowState.INTERVIEWING)
        
        try:
            logger.info("Running Interviewer Agent...")
            
            # NOTE: The Interviewer is interactive. In a full system, this would 
            # hand off control to the UI loop.
            # For this orchestration logic, we assume the interview is either:
            # 1. Already done and we have the profile (passed in or mocked)
            # 2. Or we are in a mode where we can't easily run it non-interactively.
            
            # For the purpose of this implementation, if self.user_profile is set (e.g. by a test or pre-fill), return it.
            if self.user_profile:
                return self.user_profile
                
            raise NotImplementedError(
                "Interactive interview execution not implemented in autonomous orchestrator. "
                "Please provide a UserProfile."
            )
            
        except Exception as e:
            logger.error(f"Error in interviewer: {e}")
            self._transition_to(WorkflowState.ERROR, {"error": str(e)})
            raise
    
    async def run_problem_formulation(
        self,
        problem_agent,
        runner,
        refinement_feedback: Optional[str] = None
    ) -> ProblemDefinition:
        """
        Run the problem-formulation agent.
        """
        self._transition_to(WorkflowState.PROBLEM_FORMULATION)
        
        try:
            logger.info("Running Problem-Formulation Agent...")
            
            prompt = format_prompt_for_user_profile(
                self.user_profile,
                feedback=refinement_feedback,
                current_definition=self.problem_definition if refinement_feedback else None
            )
            
            response_text = await self._execute_agent(problem_agent, prompt, runner)
            
            # Extract and parse JSON using robust helper
            logger.info(f"[DEBUG] Response text length: {len(response_text)} chars")
            logger.info(f"[DEBUG] Response preview (first 300 chars): {response_text[:300]}")
            
            data = self._extract_json_from_response(
                response_text, 
                required_keys=["problem_statement", "main_research_question"]
            )
            
            self.problem_definition = ProblemDefinition(**data)
            return self.problem_definition
            
        except Exception as e:
            logger.error(f"Error in problem formulation: {e}")
            self._transition_to(WorkflowState.ERROR, {"error": str(e)})
            raise

    
    async def run_objectives(self, objectives_agent, runner) -> ResearchObjectives:
        """Run the objectives agent."""
        self._transition_to(WorkflowState.OBJECTIVES)
        
        try:
            logger.info("Running Objectives Agent...")
            
            prompt = format_prompt_for_objectives(
                self.user_profile,
                self.problem_definition
            )
            
            response_text = await self._execute_agent(objectives_agent, prompt, runner)
            
            data = self._extract_json_from_response(
                response_text,
                required_keys=["general_objective", "specific_objectives"]
            )
            
            self.research_objectives = ResearchObjectives(**data)
            return self.research_objectives
            
        except Exception as e:
            logger.error(f"Error in objectives: {e}")
            self._transition_to(WorkflowState.ERROR, {"error": str(e)})
            raise
    
    async def run_methodology(self, methodology_agent, runner) -> MethodologyRecommendation:
        """Run the methodology agent."""
        self._transition_to(WorkflowState.METHODOLOGY)
        
        try:
            logger.info("Running Methodology Agent...")
            
            prompt = format_prompt_for_methodology(
                self.user_profile,
                self.problem_definition,
                self.research_objectives
            )
            
            response_text = await self._execute_agent(methodology_agent, prompt, runner)
            
            data = self._extract_json_from_response(
                response_text,
                required_keys=["recommended_methodology", "methodology_type"]
            )
            
            self.methodology = MethodologyRecommendation(**data)
            return self.methodology
            
        except Exception as e:
            logger.error(f"Error in methodology: {e}")
            self._transition_to(WorkflowState.ERROR, {"error": str(e)})
            raise
    
    async def run_data_collection(self, data_collection_agent, runner) -> DataCollectionPlan:
        """Run the data-collection agent."""
        self._transition_to(WorkflowState.DATA_COLLECTION)
        
        try:
            logger.info("Running Data-Collection Agent...")
            
            prompt = format_prompt_for_data_collection(
                self.user_profile,
                self.research_objectives,
                self.methodology
            )
            
            response_text = await self._execute_agent(data_collection_agent, prompt, runner)
            
            data = self._extract_json_from_response(
                response_text,
                required_keys=["collection_techniques", "timeline_breakdown"]
            )
            
            self.data_collection = DataCollectionPlan(**data)
            return self.data_collection
            
        except Exception as e:
            logger.error(f"Error in data collection: {e}")
            self._transition_to(WorkflowState.ERROR, {"error": str(e)})
            raise
    
    async def run_quality_control(self, quality_agent, runner) -> QualityValidation:
        """Run the quality-control agent."""
        self._transition_to(WorkflowState.QUALITY_CONTROL)
        
        try:
            logger.info("Running Quality-Control Agent...")
            
            prompt = format_prompt_for_quality_control(
                self.user_profile,
                self.problem_definition,
                self.research_objectives,
                self.methodology,
                self.data_collection
            )
            
            response_text = await self._execute_agent(quality_agent, prompt, runner)
            
            data = self._extract_json_from_response(
                response_text,
                required_keys=["validation_passed", "overall_quality_score"]
            )
            
            self.quality_validation = QualityValidation(**data)
            return self.quality_validation
            
        except Exception as e:
            logger.error(f"Error in quality control: {e}")
            self._transition_to(WorkflowState.ERROR, {"error": str(e)})
            raise
    
    async def run_workflow(self, agents: Dict[str, Any], runner: Any, initial_profile: Optional[UserProfile] = None) -> Dict[str, Any]:
        """
        Run the complete workflow.
        
        Args:
            agents: Dictionary of agent instances keyed by name.
            runner: The ADK runner instance.
            initial_profile: Optional pre-collected user profile.
            
        Returns:
            Dictionary containing the final proposal and metadata.
        """
        try:
            # Step 1: Interviewer
            if initial_profile:
                self.user_profile = initial_profile
                # We still transition to INTERVIEWING then immediately complete it
                self._transition_to(WorkflowState.INTERVIEWING)
            else:
                self.user_profile = await self.run_interviewer(
                    agents['interviewer'],
                    runner
                )
            
            # Main workflow loop (allows for refinement)
            while True:
                # Step 2: Problem Formulation
                refinement_feedback = None
                if self.context.current_state == WorkflowState.REFINEMENT:
                    # Extract feedback from quality validation
                    refinement_feedback = "\n".join(self.quality_validation.recommendations)
                
                self.problem_definition = await self.run_problem_formulation(
                    agents['problem_formulation'],
                    runner,
                    refinement_feedback
                )
                
                # Step 3: Objectives
                self.research_objectives = await self.run_objectives(
                    agents['objectives'],
                    runner
                )
                
                # Step 4: Methodology
                self.methodology = await self.run_methodology(
                    agents['methodology'],
                    runner
                )
                
                # Step 5: Data Collection
                self.data_collection = await self.run_data_collection(
                    agents['data_collection'],
                    runner
                )
                
                # Step 6: Quality Control
                self.quality_validation = await self.run_quality_control(
                    agents['quality_control'],
                    runner
                )
                
                # Check quality validation results
                if self.quality_validation.validation_passed:
                    # Proposal passed quality control
                    self._transition_to(WorkflowState.COMPLETE)
                    break
                
                elif self.quality_validation.requires_refinement and self.context.can_refine():
                    # Refinement needed and allowed
                    logger.warning(
                        f"*******Quality validation failed. Starting refinement iteration "
                        f"{self.context.refinement_count + 1}/{self.context.max_refinements}*******"
                    )
                    self._transition_to(WorkflowState.REFINEMENT, {
                        "iteration": self.context.refinement_count + 1,
                        "issues": len(self.quality_validation.issues_identified)
                    })
                    # Loop will continue
                
                else:
                    # Max refinements reached or refinement not possible
                    logger.warning(
                        f"Max refinements ({self.context.max_refinements}) reached. "
                        "Completing with current proposal."
                    )
                    self._transition_to(WorkflowState.COMPLETE, {
                        "warning": "Max refinements reached",
                        "validation_passed": False
                    })
                    break
            
            # Generate final proposal
            final_proposal = self._generate_final_proposal()
            
            logger.info("Finalizing workflow...")
            
            # 1. Force Python to destroy unused session objects NOW
            gc.collect() 
            
            # 2. Give the loop a moment to process the close signals from the destroyed objects
            await asyncio.sleep(0.25)
            
            return {
                "success": True,
                "proposal": final_proposal,
                "metadata": {
                    "refinement_iterations": self.context.refinement_count,
                    "validation_passed": self.quality_validation.validation_passed,
                    "coherence_score": self.quality_validation.coherence_score,
                    "feasibility_score": self.quality_validation.feasibility_score,
                    "workflow_history": [
                        {
                            "from": t.from_state,
                            "to": t.to_state,
                            "timestamp": t.timestamp
                        }
                        for t in self.context.state_history
                    ]
                }
            }
            
        except Exception as e:
            logger.error(f"Workflow error: {e}")
            self.context.error_message = str(e)
            return {
                "success": False,
                "error": str(e),
                "state": self.context.current_state,
                "metadata": {
                    "refinement_iterations": self.context.refinement_count
                }
            }
    
    def _generate_final_proposal(self) -> Dict[str, Any]:
        """
        Generate the final proposal document from all components.
        
        Returns:
            Dictionary containing the complete proposal.
        """
        return {
            "user_profile": self.user_profile.model_dump() if self.user_profile else None,
            "problem_definition": self.problem_definition.model_dump() if self.problem_definition else None,
            "research_objectives": self.research_objectives.model_dump() if self.research_objectives else None,
            "methodology": self.methodology.model_dump() if self.methodology else None,
            "data_collection_plan": self.data_collection.model_dump() if self.data_collection else None,
            "quality_validation": self.quality_validation.model_dump() if self.quality_validation else None,
            "generated_at": datetime.now().isoformat()
        }
    
    def get_current_status(self) -> Dict[str, Any]:
        """
        Get the current workflow status.
        
        Returns:
            Dictionary with current status information.
        """
        return {
            "current_state": self.context.current_state,
            "current_step": self.context.get_current_step_name(),
            "progress_percentage": self.context.get_progress_percentage(),
            "refinement_count": self.context.refinement_count,
            "max_refinements": self.context.max_refinements,
            "can_refine": self.context.can_refine(),
            "error_message": self.context.error_message
        }
