# 📁 Data-Collection Agent

The **Data-Collection Agent** is the operational engine of the research proposal pipeline (Stage 4). Once the *Methodology* is defined, this agent determines the practical "how-to" of the research: identifying specific tools, estimating sample sizes, locating data sources, and planning the timeline.

## 🧠 Core Responsibilities

This agent bridges the gap between high-level methodology and execution. Its specific tasks are:

1.  **Technique Selection**: Identifying specific collection methods (e.g., "Semi-structured interviews" vs. "Likert-scale surveys") aligned with the methodology.
2.  **Tool Recommendation**: Suggesting software/hardware (e.g., SPSS, Python pandas, NVivo) that fits the user's existing skills and constraints.
3.  **Feasibility Estimation**: Calculating realistic sample sizes and data volumes based on field standards.
4.  **Operational Planning**: Breaking down the timeline into preparation, collection, and cleaning phases.

## ⚙️ Inputs & Outputs

### Inputs
The agent requires context from three previous sources:
1.  **User Profile**: Specifically `existing_skills` (to recommend tools the user knows), `constraints` (e.g., "free tools only"), and `weekly_hours`.
2.  **Research Objectives**: To ensure data sources can actually answer the research questions.
3.  **Methodology**: The type (Qual/Quant/Mixed) strictly dictates valid collection techniques.

### Output Schema (`DataCollectionPlan`)
The agent produces a structured JSON object containing:

```json
{
  "collection_techniques": ["Survey via Google Forms", "API Scraping"],
  "recommended_tools": [
    {
      "name": "Python (BeautifulSoup)",
      "purpose": "Web Scraping",
      "type": "software",
      "accessibility": "free",
      "learning_curve": "moderate",
      "alternatives": ["Octoparse"]
    }
  ],
  "data_sources": ["Twitter API", "Public Datasets"],
  "estimated_sample_size": "5000 tweets",
  "timeline_breakdown": {
    "preparation": { "duration": "2 weeks", "activities": [...] },
    "collection": { "duration": "4 weeks", "activities": [...] },
    "quality_check": { "duration": "1 week", "activities": [...] },
    "total_duration": "7 weeks"
  },
  "resource_requirements": ["Python environment", "API Developer Account"]
}
```

## 💻 Usage

### 1. Initialization
Use the factory function to create the agent instance.

```python
from aida.sub_agents.data_collection import (
    create_data_collection_agent, 
    format_prompt_for_data_collection
)

# Create the agent
agent = create_data_collection_agent(model="gemini-2.0-flash-lite")
```

### 2. Prompt Formatting
The agent needs a combined context of the User, Objectives, and Methodology.

```python
# Assuming you have these objects from previous steps
prompt = format_prompt_for_data_collection(
    user_profile=my_user_profile,
    research_objectives=my_objectives,  # Output from Stage 2
    methodology=my_methodology          # Output from Stage 3
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

*   **`agent.py`**: Contains the factory function `create_data_collection_agent` and the `format_prompt` helper. It also includes the legacy `DataCollectionAgent` class for backward compatibility.
*   **`prompt.py`**: Contains `SYSTEM_INSTRUCTION` (the "brain" of the agent) and the `USER_CONTEXT_TEMPLATE`.

## 🔍 Key Logic & Constraints

*   **Skill Matching**: The prompt explicitly instructs the LLM to prioritize tools that match the `existing_skills` in the User Profile.
*   **Timeline Logic**: The agent calculates the specific phases (`preparation` + `collection` + `quality_check`) to ensure they sum up to less than or equal to the User Profile's `total_timeline`.
*   **Methodology Alignment**: If the Methodology is "Qualitative", the agent is restricted from suggesting purely quantitative tools (like heavy statistical regression software) unless justified.