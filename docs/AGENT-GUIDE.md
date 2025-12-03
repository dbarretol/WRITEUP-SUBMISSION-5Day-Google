# 🤖 Agent Reference Guide

## Overview

This guide provides detailed technical specifications for the specialized agents within the Multi-Agent Research Proposal System. Each agent is designed to handle a specific stage of the academic research lifecycle.

---

## ⚡ Quick Reference

| Agent | Directory | Core Task | Input | Output Model |
|-------|-----------|-----------|-------|--------------|
| **Interviewer** | `sub_agents/interviewer` | Interactive user intake | User Input (String) | `UserProfile` |
| **Problem Formulation** | `sub_agents/problem_formulation` | Gap analysis & problem definition | `UserProfile` | `ProblemDefinition` |
| **Objectives** | `sub_agents/objectives` | SMART goal setting | `ProblemDefinition` | `ResearchObjectives` |
| **Methodology** | `sub_agents/methodology` | Study design & feasibility | `ResearchObjectives` | `MethodologyRecommendation` |
| **Data Collection** | `sub_agents/data_collection` | Operational planning | `MethodologyRecommendation` | `DataCollectionPlan` |
| **Quality Control** | `sub_agents/quality_control` | Validation & Scoring | **All Previous Outputs** | `QualityValidation` |

---

## 🗣️ Interviewer Agent

### Purpose
An interactive State Machine agent that interviews the user to build their academic profile.

### Location
[`aida/sub_agents/interviewer/`](../aida/sub_agents/interviewer/)

### Usage Logic
Unlike other agents, this uses a explicit state loop (`process_turn`).

```python
from aida.sub_agents.interviewer import InterviewerAgent
from aida.data_models import InterviewState

agent = InterviewerAgent(model="gemini-2.0-flash-lite")
state = InterviewState()

# Simulation loop
while not state.is_complete:
    user_input = input("User: ")
    result = agent.process_turn(user_input, state)
    state = result["state"]
    print(f"Agent: {result['response']}")

profile = result["final_profile"]
```

### Key Features
- **Validation**: Enforces types (e.g., ensures `weekly_hours` is an integer).
- **Clarification**: Generates helpful error messages if user input is ambiguous.
- **State Tracking**: Maintains the `InterviewState` object.

---

## 🔬 Problem Formulation Agent

### Purpose
The first reasoning step. Delegates to a **Literature Review** sub-agent to find real papers and defines the research gap.

### Location
[`aida/sub_agents/problem_formulation/`](../aida/sub_agents/problem_formulation/)

### Usage

```python
from aida.sub_agents.problem_formulation import (
    create_problem_formulation_agent,
    format_prompt_for_user_profile
)
from google.adk.runners import InMemoryRunner

# Factory creates the main agent AND the sub-agent
agent = create_problem_formulation_agent(model="gemini-2.0-flash-lite")

prompt = format_prompt_for_user_profile(user_profile)

# Must be run with a Runner to handle Tool Calls (Literature Search)
# Use async with for proper cleanup
async with InMemoryRunner(agent=agent, app_name="problem-formulation") as runner:
    session = await runner.session_service.create_session(
        app_name="problem-formulation",
        user_id="test_user"
    )
    
    async for event in runner.run_async(
        user_id=session.user_id,
        session_id=session.id,
        new_message=prompt
    ):
        pass # Handle output
```

### Tools Used
*   **`AgentTool(LiteratureReviewAgent)`**: The main agent does not search; it calls this tool.
*   The **LiteratureReviewAgent** calls `google_search`.

### Output Schema (`ProblemDefinition`)
```python
{
    "problem_statement": str,
    "main_research_question": str,
    "secondary_questions": List[str],
    "key_variables": List[str],
    "preliminary_literature": [
        { "title": str, "url": str, "relevance_note": str }
    ]
}
```

---

## 🎯 Objectives Agent

### Purpose
Translates the abstract problem into concrete, actionable SMART objectives.

### Location
[`aida/sub_agents/objectives/`](../aida/sub_agents/objectives/)

### Usage

```python
from aida.sub_agents.objectives import (
    create_objectives_agent,
    format_prompt_for_objectives
)

agent = create_objectives_agent(model="gemini-2.0-flash-lite")
prompt = format_prompt_for_objectives(user_profile, problem_definition)
# Execute via Runner...
```

### Output Schema (`ResearchObjectives`)
```python
{
    "general_objective": str,
    "specific_objectives": List[str], # 3-5 SMART objectives
    "feasibility_notes": {
        "timeline_assessment": str,
        "skills_required": List[str]
    },
    "alignment_check": {
        "coverage_analysis": str # Ensures all questions are answered
    }
}
```

---

## 📐 Methodology Agent

### Purpose
Designing the "How". Determines the research type (Qual/Quant/Mixed) and validates timeline fit.

### Location
[`aida/sub_agents/methodology/`](../aida/sub_agents/methodology/)

### Usage

```python
from aida.sub_agents.methodology import (
    create_methodology_agent,
    format_prompt_for_methodology
)

agent = create_methodology_agent(model="gemini-2.0-flash-lite")
prompt = format_prompt_for_methodology(user_profile, problem_def, objectives)
```

### Output Schema (`MethodologyRecommendation`)
```python
{
    "recommended_methodology": str,
    "methodology_type": "qualitative" | "quantitative" | "mixed",
    "required_skills": List[str],
    "timeline_fit": {
        "is_feasible": bool,
        "estimated_duration": str,
        "risks": List[str]
    },
    "alternative_methodologies": List[Dict]
}
```

---

## 📁 Data Collection Agent

### Purpose
Operational planning. Selects tools, estimates sample sizes, and builds the schedule phase-by-phase.

### Location
[`aida/sub_agents/data_collection/`](../aida/sub_agents/data_collection/)

### Output Schema (`DataCollectionPlan`)
```python
{
    "collection_techniques": List[str],
    "recommended_tools": [
        { "name": str, "accessibility": "free"|"paid", "purpose": str }
    ],
    "estimated_sample_size": str, # e.g. "30 participants"
    "timeline_breakdown": {
        "preparation": { "duration": str },
        "collection": { "duration": str },
        "analysis": { "duration": str }
    }
}
```

---

## ✅ Quality Control Agent

### Purpose
The Gatekeeper. Scores the proposal and directs the Orchestrator on whether to finish or loop back for refinement.

### Location
[`aida/sub_agents/quality_control/`](../aida/sub_agents/quality_control/)

### Usage

```python
from aida.sub_agents.quality_control import (
    create_quality_control_agent,
    format_prompt_for_quality_control
)

agent = create_quality_control_agent(model="gemini-2.0-flash-lite")
# Requires inputs from ALL previous stages
prompt = format_prompt_for_quality_control(
    user_profile, problem, objectives, methodology, data_plan
)
```

### Output Schema (`QualityValidation`)
```python
{
    "validation_passed": bool,
    "coherence_score": float, # 0.0 - 1.0
    "feasibility_score": float, # 0.0 - 1.0
    "overall_quality_score": int, # 0 - 100
    "issues_identified": [
        { "severity": "critical"|"major", "component": str, "description": str }
    ],
    "requires_refinement": bool,
    "refinement_targets": ["problem_definition", "methodology"] # Orchestrator uses this
}
```

---

## 🎼 The Orchestrator

### Purpose
Coordinates the agents, manages state transitions, and handles the refinement loop.

### Location
[`aida/orchestrator.py`](../aida/orchestrator.py)

### Running the Full Pipeline

```python
import asyncio
from aida.orchestrator import ResearchProposalOrchestrator
from aida.sub_agents.problem_formulation import create_problem_formulation_agent
# ... import other create functions ...
from google.adk.runners import InMemoryRunner

async def run():
    # 1. Setup
    orchestrator = ResearchProposalOrchestrator()
    
    # 2. Define Agents Dictionary
    agents = {
        "interviewer": ..., # (Optional if profile provided)
        "problem_formulation": create_problem_formulation_agent(),
        "objectives": create_objectives_agent(),
        "methodology": create_methodology_agent(),
        "data_collection": create_data_collection_agent(),
        "quality_control": create_quality_control_agent()
    }

    # 3. Run (Runner is managed internally by orchestrator using async with)
    result = await orchestrator.run_workflow(
        agents=agents,
        runner=None, # Pass None as orchestrator creates its own scoped runner
        initial_profile=my_user_profile
    )

    if result["success"]:
        print("Proposal Generated Successfully!")
```

### State Management
The Orchestrator persists state to `.gemini/state/` and saves snapshots to `.gemini/snapshots/` using `state_manager.py`.

---

## 🛠️ Testing & Evaluation

### Integration Testing (Eval Pipeline)
Use the CLI tool to run end-to-end scenarios.
```bash
# List scenarios
python eval/test_multi_agent_pipeline.py --list

# Run specific scenario
python eval/test_multi_agent_pipeline.py scenario_1_ml_research
```

### Unit Testing
Run fast, mocked tests.
```bash
uv run pytest tests/
```

### Demos
Explore agents interactively.
```bash
python demos/demo_problem_formulation.py
```