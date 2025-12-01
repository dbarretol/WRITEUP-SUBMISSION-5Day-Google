# 📐 Methodology Agent

The **Methodology Agent** acts as the strategic architect of the research proposal (Stage 3). After the research objectives are defined, this agent determines the best scientific approach to achieve them, considering the user's specific constraints (time, skills, resources).

## 🧠 Core Responsibilities

1.  **Strategic Selection**: Recommends the single best methodology (e.g., "Mixed-Methods Sequential Explanatory Design") based on the research questions.
2.  **Feasibility Analysis**: Calculates if the chosen method fits within the user's `total_timeline` and `weekly_hours`.
3.  **Skill Gap Analysis**: Identifies what skills the user *has* vs. what they *need* to execute the method.
4.  **Alternative Generation**: Provides 3-4 backup methodologies with Pros/Cons, giving the user flexibility.

## ⚙️ Inputs & Outputs

### Inputs
The agent synthesizes data from the entire pipeline so far:
1.  **User Profile**: Time limits, skills, constraints.
2.  **Problem Definition**: The main research question (to infer Qual vs. Quant).
3.  **Research Objectives**: The specific goals the method must achieve.

### Output Schema (`MethodologyRecommendation`)
The agent produces a structured JSON object containing:

```json
{
  "recommended_methodology": "Semi-Structured Interviews and Thematic Analysis",
  "methodology_type": "qualitative",
  "justification": "Given the exploratory nature of user perceptions...",
  "required_skills": ["Interviewing", "Thematic Coding (NVivo)"],
  "timeline_fit": {
    "is_feasible": true,
    "estimated_duration": "4 months",
    "key_phases": [
      {"phase": "Recruitment", "duration": "2 weeks"},
      {"phase": "Data Collection", "duration": "8 weeks"}
    ],
    "risks": ["Participant dropout"],
    "optimization_strategies": ["Start recruitment early"]
  },
  "alternative_methodologies": [
    {
      "name": "Online Survey",
      "type": "quantitative",
      "pros": ["Faster data collection"],
      "cons": ["Lacks depth for 'why' questions"]
    }
  ]
}
```

## 💻 Usage

### 1. Initialization
Use the factory function to create the agent instance.

```python
from academic_research.sub_agents.methodology import (
    create_methodology_agent,
    format_prompt_for_methodology
)

# Create the agent
agent = create_methodology_agent(model="gemini-2.0-flash-lite")
```

### 2. Prompt Formatting
The helper function `format_prompt_for_methodology` automatically applies a heuristic to hint at the research type based on keywords in the Research Question (e.g., "How many..." -> "Likely quantitative").

```python
prompt = format_prompt_for_methodology(
    user_profile=user_profile,
    problem_definition=problem_def,  # Output from Stage 1
    research_objectives=objectives   # Output from Stage 2
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

*   **`agent.py`**: Contains the factory function and the prompt formatter.
    *   **Logic Note**: The `format_prompt_for_methodology` function includes simple keyword matching (e.g., "measure", "quantify") to inject a `research_type_hint` into the prompt.
*   **`prompt.py`**: Contains `SYSTEM_INSTRUCTION` which forces the model to evaluate the "Timeline Fit" rigorously.

## 🔍 Key Logic & Constraints

*   **Timeline Fit**: The agent is explicitly instructed to flag `is_feasible: false` if the estimated duration exceeds the user's `total_timeline`.
*   **Methodology Type**: Must strictly be one of `qualitative`, `quantitative`, or `mixed`.
*   **Constraint Checking**: If the user has a constraint like "Remote only", the agent will avoid recommending "In-person Ethnography".