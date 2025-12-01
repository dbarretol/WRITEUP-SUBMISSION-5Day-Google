# 📚 Literature Review Agent

The **Literature Review Agent** is a specialist "sub-agent" designed to augment the Problem Formulation phase. It is the only agent in the system equipped with the **Google Search Tool**, allowing it to fetch real-time, grounded academic data rather than relying solely on the LLM's internal knowledge.

## 🧠 Core Responsibilities

1.  **Search Strategy**: Formulates multiple search queries (Broad, Recent, Specific) to get a comprehensive view of the topic.
2.  **Tool Execution**: Invokes the `google_search` tool to retrieve live search results from the web.
3.  **Source Filtering**: Prioritizes academic domains (e.g., `arxiv.org`, `ieee.org`, `.edu`) and recent publications (post-2020).
4.  **Data Structuring**: Parses raw search results into a clean JSON list of `literature_found`.

## ⚙️ Inputs & Outputs

### Inputs
The agent needs the research context to formulate queries:
*   `field_of_study` (e.g., "Computer Science")
*   `research_area` (e.g., "Multi-Agent Reinforcement Learning")
*   `additional_context` (e.g., "Focus on coordination mechanisms")

### Output Schema
The agent produces a JSON object (as text, not enforced schema) containing:

```json
{
  "queries_performed": [
    "Multi-Agent Reinforcement Learning coordination mechanisms site:arxiv.org",
    "recent advances in MARL coordination 2024"
  ],
  "literature_found": [
    {
      "title": "Coordination in Multi-Agent Reinforcement Learning: A Survey",
      "url": "https://arxiv.org/abs/2402.xxxxx",
      "relevance_note": "Provides a comprehensive overview of recent algorithms.",
      "source": "arxiv.org"
    }
  ],
  "search_summary": "Recent literature focuses heavily on decentralized training...",
  "gaps_identified": ["Limited research on real-time constraints"]
}
```

## 💻 Usage

### 1. Initialization
Use the factory function to create the agent. Note that this agent takes a `tools` parameter internally.

```python
from academic_research.sub_agents.literature_review import (
    create_literature_review_agent,
    format_prompt_for_literature_review
)

# Create the agent (automatically configures google_search tool)
agent = create_literature_review_agent(model="gemini-2.0-flash-lite")
```

### 2. Prompt Formatting

```python
prompt = format_prompt_for_literature_review(
    field_of_study="Biology",
    research_area="CRISPR gene editing applications",
    additional_context="Focus on ethical implications"
)
```

### 3. Execution
This agent **must** be run with a runner that supports tool execution (like `InMemoryRunner` in the Google Gen AI SDK).

```python
from google.adk.runners import InMemoryRunner
from google.genai import types

runner = InMemoryRunner(agent=agent)
session = await runner.session_service.create_session(user_id="test_user")

# The runner handles the loop: 
# 1. Agent calls tool -> Runner executes tool -> Runner feeds result back -> Agent formats final JSON.
response = await runner.run_async(
    user_id=session.user_id,
    session_id=session.id,
    new_message=types.Content(parts=[types.Part(text=prompt)])
)
```

## 📂 File Structure

*   **`agent.py`**:
    *   Configures the agent with `tools=[google_search]`.
    *   **Crucial Config**: `response_mime_type="application/json"` is **removed** here. Enabling JSON mode often conflicts with Tool Use (Function Calling), so this agent outputs raw text which is then parsed as JSON.
*   **`prompt.py`**:
    *   `SYSTEM_INSTRUCTION`: Explicitly commands the "Two-Step Process" (Search then Format) to prevent hallucination.
    *   Defines specific search operators (e.g., `site:arxiv.org`, `after:2020`) to ensure academic relevance.

## 🔍 Key Logic & Constraints

*   **No Hallucination**: The prompt strictly forbids inventing papers. It forces the model to use *only* what the `google_search` tool returns.
*   **Two-Step Execution**:
    1.  **Turn 1**: The model sees the user prompt and returns a `function_call` (Step 1).
    2.  **Turn 2**: The system provides the `function_response` (search results). The model then processes this data and generates the final JSON (Step 2).
*   **Temperature**: Set slightly higher (`0.2`) than other agents to encourage varied search query formulation.