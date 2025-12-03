# 🗣️ Interviewer Agent

The **Interviewer Agent** is the entry point of the system. Unlike the other agents which perform large-scale reasoning tasks, this agent operates as a **State Machine** to interactively gather structured data from the user.

It guides the user through a pre-defined questionnaire to build a complete `UserProfile` (Academic Program, Field of Study, Constraints, Skills, etc.) before the research generation process begins.

## 🧠 Core Responsibilities

1.  **Guided Data Collection**: Iterates through a fixed list of questions defined in `questionnaire.py`.
2.  **Input Extraction**: Uses the LLM to parse natural language (e.g., "I have about 3 months") into structured data (e.g., `{"value": 3, "unit": "months"}`).
3.  **Validation**: Checks if the user's answer is valid for the current field. If not, it generates a clarification request instead of moving to the next question.
4.  **State Management**: Tracks the `current_question_index` and the accumulating `profile_data`.

## ⚙️ Inputs & Outputs

### Input
The agent accepts a simple string `user_input` and the current `InterviewState` object.

### Output
The agent returns a dictionary containing the response text and the updated state.

```json
{
  "response": "Great! Next, what are your constraints?",
  "state": <InterviewState object>,
  "is_complete": false,
  "final_profile": { ... } // Only present if is_complete is True
}
```

### Internal Logic (Prompt Output)
Internally, the LLM is instructed to output JSON to separate the extraction logic from the conversation:

```json
{
  "extracted_value": ["Python", "SQL"],
  "next_message": "Got it. Now, what constraints do you have?",
  "is_valid": true,
  "explanation": "Extracted list of skills successfully."
}
```

## 💻 Usage

This agent is typically used in a `while` loop until `is_complete` becomes `True`.

### Initialization

```python
from aida.sub_agents.interviewer import InterviewerAgent
from aida.data_models import InterviewState

# Initialize
agent = InterviewerAgent(model="gemini-2.0-flash-lite")
state = InterviewState()  # Starts at question index 0
```

### Execution Loop

```python
print("System: " + agent.questions[0].text)  # Print first question

while not state.is_complete:
    user_input = input("User: ")
    
    result = agent.process_turn(user_input, state)
    
    # Update state reference
    state = result["state"]
    
    print("System: " + result["response"])

# When loop finishes, access the data
final_profile = result["final_profile"]
```

## 📂 File Structure

*   **`agent.py`**: Contains the `InterviewerAgent` class. It manages the `genai.Client` directly to perform the specific extraction/validation steps required for the state machine.
*   **`prompt.py`**: Contains `INTERVIEWER_PROMPT`, which dynamically updates with the current question text and validation rules.
*   **`../../questionnaire.py`**: (External dependency) Defines the list of `InterviewQuestion` objects (e.g., "What is your field of study?", "How many hours per week do you have?").

## 🔍 Key Logic & Validation

*   **State Machine**: The agent will **not** increment `state.current_question_index` unless the LLM returns `"is_valid": true`.
*   **Clarification Loop**: If the user answers "I don't know" to a required field, the LLM generates a helpful explanation (defined in the `next_message` field) and waits for a new input for the *same* question.
*   **Structured Extraction**: Special handling is applied to complex fields like `total_timeline` to convert natural language into the `Timeline(value, unit)` Pydantic model.