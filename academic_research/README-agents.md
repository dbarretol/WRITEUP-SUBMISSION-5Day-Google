# 🏗️ Core Infrastructure & Orchestration

This directory contains the foundational Python modules that power the Multi-Agent Research Proposal System. While the `sub_agents/` directory contains the "brains" (LLM logic), these files provide the "skeleton" (coordination, state, data structures, and I/O).

## 🧩 Component Architecture

The system is organized into four logical layers:

### 1. Data Layer (The Contract)
*   **`data_models.py`**: The most critical file. It defines the Pydantic models (e.g., `UserProfile`, `ProblemDefinition`, `ResearchObjectives`) that serve as the **strict interface contracts** between agents. If an agent outputs JSON, it must validate against these schemas.
*   **`config.py`**: Central configuration for model names, API keys, and retry logic (using `google.genai.types.HttpRetryOptions` for resilience).

### 2. Orchestration Layer (The Brain)
*   **`orchestrator.py`**: The central controller. It implements the `ResearchProposalOrchestrator` class which:
    *   Sequentially executes agents (Interviewer → Problem → Objectives → ...).
    *   Manages the **Refinement Loop** (looping back if Quality Control fails).
    *   Handles JSON extraction from mixed LLM responses.
*   **`workflow_state.py`**: A Finite State Machine (FSM) definition. It defines valid states (`INIT`, `PROBLEM_FORMULATION`, `REFINEMENT`, etc.) and prevents illegal transitions (e.g., jumping from Interview to Data Collection).

### 3. State & Persistence Layer (The Memory)
*   **`state_manager.py`**: Handles file I/O.
    *   Saves the workflow state (`.json`).
    *   Saves "Snapshots" of the proposal at every iteration (`.gemini/snapshots/`).
*   **`proposal_builder.py`**: A utility class that takes the raw JSON outputs from all agents and assembles them into a final, formatted **Markdown** report.

### 4. Communication & Utility Layer
*   **`agent_registry.py`**: A pattern for registering and retrieving agent instances.
*   **`communication.py`**: Defines a Pub/Sub message bus and standardized `AgentMessage` envelope.
*   **`message_router.py`**: Routes messages between agents and logs all communication to `.gemini/logs` for debugging.
*   **`questionnaire.py`**: Defines the static list of questions and validation logic for the Interviewer Agent.

---

## 🚀 Key Workflows

### The Orchestrator Loop (`orchestrator.py`)

The `run_workflow` method is the heart of the system. It implements the following logic:

1.  **Transition** to `INTERVIEWING` -> Run Interviewer.
2.  **Transition** to `PROBLEM_FORMULATION` -> Run Problem Agent.
3.  ... (Execute Objectives, Methodology, Data Collection) ...
4.  **Transition** to `QUALITY_CONTROL`.
5.  **Check Validation**:
    *   If **Pass**: Transition to `COMPLETE`.
    *   If **Fail**: Check `refinement_count`.
        *   If limit not reached: Transition to `REFINEMENT` and loop back to Step 2 (passing feedback).
        *   If limit reached: Force complete with warnings.

### JSON Robustness
The Orchestrator includes a robust `_extract_json_from_response` method. Since LLMs sometimes wrap JSON in markdown (```json ... ```) or add conversational text, this method uses multiple strategies (regex, string cleaning) to ensure the system doesn't crash on slightly malformed outputs.

---

## 📂 File Summary

| File | Responsibility |
| :--- | :--- |
| **`data_models.py`** | **Crucial.** Pydantic schemas for all agent I/O. |
| **`orchestrator.py`** | **Crucial.** Runs the agents, handles errors, manages loops. |
| **`workflow_state.py`** | Defines valid states and tracks history. |
| **`config.py`** | Global settings and Retry configs. |
| **`proposal_builder.py`** | Formatting utility (JSON -> Markdown). |
| **`state_manager.py`** | Saves progress to disk (`.gemini/`). |
| **`questionnaire.py`** | Config for the Interviewer agent. |
| **`communication.py`** | (Advanced) Event bus definitions. |
| **`message_router.py`** | (Advanced) Logs interactions. |
| **`agent_registry.py`** | (Advanced) Service locator for agents. |

## 💻 Usage Example

```python
from academic_research.orchestrator import ResearchProposalOrchestrator
from academic_research.state_manager import StateManager
from academic_research.sub_agents.problem_formulation import create_problem_formulation_agent
# ... import other agents ...

# 1. Setup Agents
agents = {
    "problem_formulation": create_problem_formulation_agent(),
    # ...
}

# 2. Initialize Infrastructure
orchestrator = ResearchProposalOrchestrator()
state_manager = StateManager()

# 3. Run Workflow
result = await orchestrator.run_workflow(
    agents=agents,
    runner=my_runner,
    initial_profile=my_user_profile
)

# 4. Save Output
if result["success"]:
    state_manager.save_proposal_snapshot(
        result["proposal"], 
        run_id="run_123", 
        iteration=0
    )
```