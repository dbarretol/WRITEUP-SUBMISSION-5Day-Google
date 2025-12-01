"""Interviewer agent for academic research."""

import json
from typing import Dict, Any, List
from pydantic import PrivateAttr
from google import genai
from google.adk.agents import LlmAgent
from google.genai import types
from ...config import DEFAULT_MODEL

from ...data_models import UserProfile, InterviewState, Timeline
from ...questionnaire import QUESTIONS, InterviewQuestion

from .prompt import INTERVIEWER_PROMPT

class InterviewerAgent(LlmAgent):
    _client: genai.Client = PrivateAttr()
    _questions: List[InterviewQuestion] = PrivateAttr()

    def __init__(self, model: str = DEFAULT_MODEL, **kwargs):
        super().__init__(
            name="interviewer_agent",
            model=model,
            instruction=INTERVIEWER_PROMPT,
            **kwargs
        )
        self._questions = QUESTIONS
        # Initialize client. Assumes GOOGLE_API_KEY is set in environment.
        self._client = genai.Client()

    @property
    def client(self):
        return self._client

    @property
    def questions(self):
        return self._questions

    def _format_prompt(self, state: InterviewState) -> str:
        current_q = self._questions[state.current_question_index]
        return INTERVIEWER_PROMPT.format(
            question_index=state.current_question_index + 1,
            total_questions=len(self._questions),
            current_question_text=current_q.text,
            profile_data=json.dumps(state.profile_data, indent=2)
        )

    def process_turn(self, user_input: str, state: InterviewState) -> Dict[str, Any]:
        """
        Processes a single turn of the interview.
        Returns a dict with the agent's response and the updated state.
        """
        if state.is_complete:
            return {
                "response": "The interview is already complete. Thank you!",
                "state": state,
                "is_complete": True
            }

        # Prepare prompt for LLM
        prompt = self._format_prompt(state)
        
        # Call LLM (simulated here via super().process if we could, but we need specific prompting)
        # We will use the client directly or construct a message.
        # Since we are inheriting from LlmAgent, we can use `self.client` if initialized, 
        # but LlmAgent usually expects `process` to be called by a runner.
        # To make this testable and work with the runner, we might need to adjust.
        # However, for this specific "State Machine" logic, it's often easier to wrap the LLM call.
        
        # Let's construct the message content
        messages = [
            types.Content(role="user", parts=[types.Part(text=prompt)]),
            types.Content(role="user", parts=[types.Part(text=f"User Input: {user_input}")])
        ]

        # Generate content
        # Note: In a real ADK agent, we might rely on the runner to handle history.
        # Here we are manually managing the prompt context for the extraction task.
        response = self.client.models.generate_content(
            model=self.model,
            contents=messages,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        
        try:
            llm_output = json.loads(response.text)
        except json.JSONDecodeError:
            # Fallback error handling
            return {
                "response": "I'm sorry, I had trouble processing that. Could you please repeat?",
                "state": state,
                "is_complete": False
            }

        current_q = self.questions[state.current_question_index]
        
        if llm_output.get("is_valid"):
            # Update profile data
            state.profile_data[current_q.field_name] = llm_output["extracted_value"]
            
            # Move to next question
            state.current_question_index += 1
            
            if state.current_question_index >= len(self.questions):
                state.is_complete = True
                return {
                    "response": "Thank you! I have gathered all the necessary information.",
                    "state": state,
                    "is_complete": True,
                    "final_profile": state.profile_data
                }
            else:
                next_q = self.questions[state.current_question_index]
                return {
                    "response": next_q.text,
                    "state": state,
                    "is_complete": False
                }
        else:
            # Invalid or clarification needed
            return {
                "response": llm_output.get("next_message", current_q.clarification_prompt or current_q.text),
                "state": state,
                "is_complete": False
            }

