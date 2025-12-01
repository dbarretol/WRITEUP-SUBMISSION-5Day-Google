# ✅ Quality-Control Agent

The **Quality-Control Agent** is the final and most critical step in the research pipeline (Stage 5). It does not generate new research content; instead, it acts as a strict auditor. It aggregates the outputs from all previous agents (Problem, Objectives, Methodology, Data Collection) and evaluates them for internal coherence, feasibility, and alignment.

## 🧠 Core Responsibilities

1.  **Holistic Validation**: Checks if the *entire* proposal makes sense as a single unit (e.g., "Does the Data Collection plan actually answer the Research Questions defined in Stage 1?").
2.  **Scoring**: Calculates quantitative scores for **Coherence** (logical flow) and **Feasibility** (execution reality).
3.  **Issue Detection**: Identifies specific weaknesses, categorized by severity (Critical, Major, Minor).
4.  **Refinement Decision**: Determines if the proposal is "Ready" or if it needs to go back to a previous stage for revision.

## ⚙️ Inputs & Outputs

### Inputs
This agent requires the **entire state** of the research proposal:
1.  **User Profile** (Constraints & Skills)
2.  **Problem Definition** (from Stage 1)
3.  **Research Objectives** (from Stage 2)
4.  **Methodology** (from Stage 3)
5.  **Data Collection Plan** (from Stage 4)

### Output Schema (`QualityValidation`)
The agent produces a structured JSON object containing scores and refinement directives:

```json
{
  "validation_passed": false,
  "coherence_score": 0.8,
  "feasibility_score": 0.5,
  "overall_quality_score": 65,
  "issues_identified": [
    {
      "severity": "critical",
      "component": "data_collection",
      "description": "Sample size of 5000 is impossible given the 3-month timeline.",
      "impact": "Project will fail to complete."
    }
  ],
  "recommendations": ["Reduce sample size to 500", "Switch to automated scraping"],
  "requires_refinement": true,
  "refinement_targets": ["data_collection"]
}
```

## 📊 Scoring Logic

The logic defined in `prompt.py` enforces strict grading criteria:

*   **Coherence Score (0.0 - 1.0)**: Do the Objectives match the Problem? Does the Methodology match the Objectives?
*   **Feasibility Score (0.0 - 1.0)**: Can this be done in the user's `weekly_hours` + `total_timeline`?
*   **Thresholds**:
    *   If **Score < 0.65** (65%), `validation_passed` is automatically `false`.
    *   If **Any Critical Issue** is found, `validation_passed` is automatically `false`.

## 💻 Usage

### 1. Initialization
Use the factory function to create the agent instance.

```python
from academic_research.sub_agents.quality_control import (
    create_quality_control_agent,
    format_prompt_for_quality_control
)

agent = create_quality_control_agent(model="gemini-2.0-flash-lite")
```

### 2. Prompt Formatting
This formatter is the most complex in the system as it aggregates all previous data.

```python
prompt = format_prompt_for_quality_control(
    user_profile=user_profile,
    problem_definition=problem_def,
    research_objectives=objectives,
    methodology=methodology,
    data_collection=data_plan
)
```

### 3. Execution (with `InMemoryRunner`)

```python
from google.adk.runners import InMemoryRunner
from google.genai import types

runner = InMemoryRunner(agent=agent)
session = await runner.session_service.create_session(user_id="test_user")

response = await runner.run_async(
    user_id=session.user_id,
    session_id=session.id,
    new_message=types.Content(parts=[types.Part(text=prompt)])
)
```

## 📂 File Structure

*   **`agent.py`**: Contains the factory function and the aggregator prompt formatter.
*   **`prompt.py`**:
    *   **Logic**: Defines the "Chain of Logic" check (Problem -> Objectives -> Method -> Data).
    *   **Output Constraint**: Explicitly bans markdown formatting to ensure clean JSON parsing for the Orchestrator.

## 🔍 Key Logic & Constraints

*   **Refinement Signaling**: The `refinement_targets` list is crucial. If the agent returns `["methodology"]`, the Orchestrator knows to loop back to Stage 3, passing the "Recommendations" as feedback context.
*   **Raw JSON**: To prevent parsing errors during automated refinement loops, the system instruction explicitly demands `ONLY a valid JSON object` with no markdown code fences.
*   **Constraint Compliance**: The agent performs a final check against the User Profile's `constraints` list (e.g., "No budget") to ensure no previous agent "hallucinated" a resource (e.g., "Hire 3 assistants") that the user doesn't have.