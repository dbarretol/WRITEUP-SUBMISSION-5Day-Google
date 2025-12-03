# 🎯 Objectives Agent

The **Objectives Agent** is responsible for Stage 2 of the research pipeline. It transforms the broad "Problem Definition" (from Stage 1) into a set of concrete, actionable goals. It ensures that the research doesn't just ask questions, but has a clear plan to answer them.

## 🧠 Core Responsibilities

1.  **SMART Generation**: Creates 3-5 Specific Objectives that are Specific, Measurable, Achievable, Relevant, and Time-bound.
2.  **Feasibility Check**: Validates that these objectives can actually be achieved given the user's `weekly_hours` and `total_timeline`.
3.  **Alignment Mapping**: Performs a logical audit—checking that every Research Question (Main & Secondary) is addressed by at least one Specific Objective.
4.  **Skill & Constraint Analysis**: Flags if an objective requires skills the user doesn't have yet.

## ⚙️ Inputs & Outputs

### Inputs
The agent consumes the output of Stage 1 and the User Profile:
1.  **User Profile**: Specifically `timeline` and `skills` (to determine "Achievable").
2.  **Problem Definition**: `problem_statement`, `main_research_question`, and `secondary_questions`.

### Output Schema (`ResearchObjectives`)
The agent produces a structured JSON object containing:

```json
{
  "general_objective": "To develop a novel multi-agent coordination protocol...",
  "specific_objectives": [
    "To design a decentralized algorithm for agent negotiation by Month 2.",
    "To evaluate the algorithm against baseline X using Python simulations by Month 4."
  ],
  "feasibility_notes": {
    "timeline_assessment": "Tight timeline; simulation phase is critical.",
    "skills_required": ["Advanced Python", "Game Theory"],
    "risk_factors": ["Computational resource limits"]
  },
  "alignment_check": {
    "general_to_problem": "Directly addresses the scalability issue identified...",
    "objectives_to_questions": {
      "main_question": ["Specific Objective 1", "Specific Objective 2"]
    },
    "coherence_score": "High"
  }
}
```

## 💻 Usage

### 1. Initialization
Use the factory function to create the agent instance.

```python
from aida.sub_agents.objectives import (
    create_objectives_agent,
    format_prompt_for_objectives
)

# Create the agent
agent = create_objectives_agent(model="gemini-2.0-flash-lite")
```

### 2. Prompt Formatting

```python
prompt = format_prompt_for_objectives(
    user_profile=user_profile,
    problem_definition=problem_def  # Output from Stage 1
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
*   **`prompt.py`**: Contains `SYSTEM_INSTRUCTION` which strictly enforces the "SMART" criteria and the structure of the feasibility/alignment checks.

## 🔍 Key Logic & Constraints

*   **One-to-One Mapping**: The prompt explicitly asks the model to map specific objectives to specific secondary questions. If a question is left orphaned (no objective covers it), the `alignment_check.coverage_analysis` field will flag it.
*   **Feasibility Notes**: The agent is instructed to look at the `constraints` field (e.g., "No budget") and ensure the objectives don't violate it (e.g., "Conduct paid user study" would be flagged).
*   **Count Constraint**: The prompt strictly limits output to **3-5 specific objectives** to keep the scope manageable for student researchers.