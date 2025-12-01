# 🔬 Problem-Formulation Agent

The **Problem-Formulation Agent** is the first intelligent reasoning step in the research pipeline (Stage 1). It takes the user's rough interests and transforms them into a rigorous academic problem definition.

## 🧠 Core Responsibilities

1.  **Literature Review Delegation**: Unlike other agents, this agent does **not** rely solely on its training data. It delegates the search task to a sub-agent (`LiteratureReviewAgent`) to find real, up-to-date papers.
2.  **Synthesis**: It analyzes the literature returned by the sub-agent to identify research gaps.
3.  **Formulation**: It constructs a clear "Problem Statement", "Main Research Question", and "Secondary Questions".
4.  **Refinement**: It supports iterative feedback loops (e.g., "Make the problem narrower") while preserving the context of previous drafts.

## ⚙️ Inputs & Outputs

### Inputs
The agent requires the `UserProfile` (specifically Research Area, Field of Study, and Constraints) and optionally a `refinement_context` if the user is asking for a revision.

### Output Schema (`ProblemDefinition`)
The agent produces a structured JSON object containing:

```json
{
  "problem_statement": "While Multi-Agent Reinforcement Learning (MARL) has shown promise, existing protocols struggle with scalability...",
  "main_research_question": "How can decentralized communication protocols improve scalability in cooperative MARL?",
  "secondary_questions": [
    "What is the impact of bandwidth constraints on convergence?",
    "How does agent heterogeneity affect protocol efficiency?"
  ],
  "key_variables": ["Bandwidth usage", "Convergence rate", "Agent count"],
  "preliminary_literature": [
    {
      "title": "Scalable MARL: A Survey",
      "url": "https://arxiv.org/...",
      "relevance_note": "Identifies communication overhead as a key bottleneck."
    }
  ]
}
```

## 💻 Usage

### 1. Initialization
Use the factory function. Note that this function *also* initializes the `LiteratureReviewAgent` internally.

```python
from academic_research.sub_agents.problem_formulation import (
    create_problem_formulation_agent,
    format_prompt_for_user_profile
)

# Create the agent (and its sub-agent)
agent = create_problem_formulation_agent(model="gemini-2.0-flash-lite")
```

### 2. Prompt Formatting

```python
prompt = format_prompt_for_user_profile(
    user_profile=user_profile,
    feedback="Focus specifically on resource-constrained environments"  # Optional
)
```

### 3. Execution (with `InMemoryRunner`)
Because this agent calls another agent (via `AgentTool`), you **must** use a runner that supports tool execution.

```python
from google.adk.runners import InMemoryRunner
from google.genai import types

runner = InMemoryRunner(agent=agent)
session = await runner.session_service.create_session(user_id="test_user")

# The runner handles the complex flow:
# 1. Main Agent calls LitReview Agent (Tool)
# 2. LitReview Agent calls Google Search (Tool)
# 3. Google Search returns data
# 4. LitReview Agent formats data
# 5. Main Agent synthesizes final Problem Definition
response = await runner.run_async(
    user_id=session.user_id,
    session_id=session.id,
    new_message=types.Content(parts=[types.Part(text=prompt)])
)
```

## 📂 File Structure

*   **`agent.py`**:
    *   Configures the agent with `tools=[AgentTool(agent=lit_review_agent)]`.
    *   **Configuration Note**: Like the LitReview agent, `response_mime_type="application/json"` is **removed** to prevent conflicts with Tool Calling. The agent is prompted to output raw JSON text instead.
*   **`prompt.py`**:
    *   `SYSTEM_INSTRUCTION`: Enforces a **Strict Two-Step Protocol**. The agent is forbidden from guessing papers; it *must* call the tool first.
    *   `USER_CONTEXT_TEMPLATE`: Includes logic for handling refinement history.

## 🔍 Key Logic & Constraints

*   **No Hallucination**: By delegating to the `LiteratureReviewAgent` (which uses Google Search), we ensure the "Preliminary Literature" section contains real, verifiable URLs.
*   **Refinement Context**: If `current_definition` and `feedback` are provided to the prompt formatter, the agent is instructed to modify the existing problem rather than starting from scratch.
*   **Academic Rigor**: The prompt instructs the agent to create questions that are "researchable" (not just yes/no questions) and aligned with the user's academic level (e.g., Master's vs. PhD).