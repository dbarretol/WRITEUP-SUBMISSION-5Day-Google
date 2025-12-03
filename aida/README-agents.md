# 🏗️ Core Infrastructure & Orchestration

This directory contains the foundational Python modules that power the Multi-Agent Research Proposal System. While the `sub_agents/` directory contains the "brains" (LLM logic), these files provide the "skeleton" (coordination, state, data structures, and I/O).

## 🧩 Component Architecture

The system is organized into four logical layers:

### 1. Data & Configuration Layer (The Contract)
*   **`data_models.py`**: The most critical file. It defines the Pydantic models (e.g., `UserProfile`, `ProblemDefinition`, `ResearchObjectives`) that serve as the **strict interface contracts** between agents.
    *   *Key Models*: `LiteratureReviewResult`, `MethodologyRecommendation`, `QualityValidation`.
*   **`config.py`**: Central configuration.
    *   Sets `DEFAULT_MODEL` (e.g., `gemini-2.0-flash-lite`).
    *   Defines `MAX_REFINEMENTS` (controlling the feedback loop limit).
    *   Configures `RETRY_CONFIG` using `google.genai.types.HttpRetryOptions` for API resilience (handling 429/503 errors).
*   **`__init__.py`**: Handles environment setup. It detects whether to use **Vertex AI** (defaulting to `us-central1`) or standard **Google Gen AI** via API keys, loading variables from `.env`.

### 2. Orchestration Layer (The Brain)
*   **`orchestrator.py`**: The central controller. It implements the `ResearchProposalOrchestrator` class which:
    *   Sequentially executes agents (Interviewer → Problem → Objectives → Method → Data → Quality).
    *   **Refinement Logic**: If Quality Control fails, it loops back to `PROBLEM_FORMULATION` with specific feedback, up to `MAX_REFINEMENTS` times.
    *   **Robust Execution**: Implements `_execute_agent` which creates ephemeral `InMemoryRunner` instances to ensure Tool Use (like Google Search) functions correctly for every step.
*   **`workflow_state.py`**: A Finite State Machine (FSM) definition.
    *   Defines `WorkflowState` (Enum) and `WorkflowContext`.
    *   Enforces `VALID_TRANSITIONS` to prevent illegal jumps (e.g., jumping from "Interview" to "Data Collection" without "Objectives").

### 3. User Interaction Layer
*   **`questionnaire.py`**: Defines the static list of `InterviewQuestion` objects used by the Interviewer Agent.
    *   Includes validation logic (e.g., `validate_positive_int` for weekly hours).

### 4. Output Generation Layer
*   **`pdf_generator.py`**: Replaces simple text output with a professional PDF report.
    *   Uses `reportlab` to render the JSON proposal into a formatted document.
    *   Generates sections for User Profile, Problem Definition, Methodology, etc., with clickable hyperlinks for literature references.

---

## 🚀 Key Workflows

### The Orchestrator Loop (`orchestrator.py`)

The `run_workflow` method is the heart of the system. It implements the following logic:

1.  **Initialization**: Sets up `UserProfile` (either via the Interviewer agent or passed statically).
2.  **Sequential Execution**:
    *   **Problem Formulation**: (Uses `LiteratureReview` tool).
    *   **Objectives**: (Validated against Problem).
    *   **Methodology**: (Validated against User Constraints).
    *   **Data Collection**: (Aligned with Methodology).
3.  **Quality Control & Refinement**:
    *   The system checks `QualityValidation.validation_passed`.
    *   **If Fail**: It increments `refinement_count`. If `< MAX_REFINEMENTS`, it loops back to **Problem Formulation**, injecting the "Recommendations" from Quality Control as user feedback context.
    *   **If Pass**: Transitions to `COMPLETE`.

### JSON Robustness Strategy
The Orchestrator includes a robust `_extract_json_from_response` method. Since LLMs sometimes wrap JSON in markdown or add conversational text, this method uses three strategies in order:
1.  **Direct Parse**: Attempts `json.loads(text)`.
2.  **Markdown Cleaning**: Removes \`\`\`json fences.
3.  **Regex Extraction**: Searches for `{...}` patterns using `r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'` to find the JSON object buried in text.

---

## 📂 File Summary

| File | Responsibility |
| :--- | :--- |
| **`data_models.py`** | **Crucial.** Pydantic schemas for all agent inputs/outputs. |
| **`orchestrator.py`** | **Crucial.** Runs the agents, handles errors, manages the refinement loop. |
| **`workflow_state.py`** | Defines valid states (`INIT`, `PROBLEM_...`, `COMPLETE`) and history. |
| **`config.py`** | Global settings, Model IDs, and Retry logic. |
| **`pdf_generator.py`** | Generates the final PDF report from the structured JSON. |
| **`questionnaire.py`** | Configuration/Questions for the Interviewer agent. |
| **`__init__.py`** | Environment variable loading and Project/Region setup. |

## 💻 Usage Example

```python
import asyncio
from aida.orchestrator import ResearchProposalOrchestrator
from aida.sub_agents.problem_formulation import create_problem_formulation_agent
from aida.sub_agents.objectives import create_objectives_agent
# ... import other factory functions ...

# 1. Initialize Agents
```python
agents = {
    "interviewer": None, # (Assumed handled or mocked for this example)
    "problem_formulation": create_problem_formulation_agent(),
    "objectives": create_objectives_agent(),
    "methodology": create_methodology_agent(),
    "data_collection": create_data_collection_agent(),
    "quality_control": create_quality_control_agent()
}
```
# 2. Initialize Orchestrator
```python
orchestrator = ResearchProposalOrchestrator(
    progress_callback=lambda step, pct: print(f"[{pct}%] {step}")
)
```
# 3. Define Initial Profile (Skipping interactive interview for this snippet)
```python
from aida.data_models import UserProfile, Timeline
profile = UserProfile(
    academic_program="PhD",
    field_of_study="Computer Science",
    research_area="LLM Agents",
    weekly_hours=20,
    total_timeline=Timeline(value=6, unit="months"),
    existing_skills=["Python", "GenAI"],
    constraints=["No budget"]
)
```
# 4. Run Workflow

```python
# Note: 'runner' is passed but orchestrator creates ephemeral runners internally for tools
async def main():
    result = await orchestrator.run_workflow(
        agents=agents,
        runner=None, 
        initial_profile=profile
    )

    if result["success"]:
        print(f"Workflow Complete! Refinement Loops: {result['metadata']['refinement_iterations']}")
```

# 5. Generate PDF Output
```python
from aida.pdf_generator import generate_pdf_proposal

pdf_buffer = generate_pdf_proposal(result["proposal"])

output_filename = "final_research_proposal.pdf"
with open(output_filename, "wb") as f:
f.write(pdf_buffer.getvalue())

print(f"📄 PDF saved to: {output_filename}")

else:
print(f"❌ Workflow failed: {result['error']}")

if __name__ == "__main__":
    asyncio.run(main())
```

## ⚙️ Environment Setup

The system is designed to run on either **Google Cloud Vertex AI** or via the **Google Gen AI SDK** (Gemini API). This logic is handled in `__init__.py`.

1.  **Create a `.env` file** in the project root:

```sh
    # Option A: Standard Gemini API (Simpler)
    GOOGLE_GENAI_USE_VERTEXAI=False
    GOOGLE_API_KEY=your_api_key_here

    # Option B: Vertex AI (Enterprise)
    # GOOGLE_GENAI_USE_VERTEXAI=True
    # GOOGLE_CLOUD_PROJECT=your-project-id
    # GOOGLE_CLOUD_LOCATION=us-central1
```

2.  **Configuration (`config.py`)**:
    You can adjust global parameters in this file:
    *   `DEFAULT_MODEL`: Currently set to `"gemini-2.0-flash-lite"`.
    *   `MAX_REFINEMENTS`: Controls how many times the Quality Control agent can send the proposal back for revision (default: 3).