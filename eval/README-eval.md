# Evaluation Suite

This documentation covers the evaluation scripts for the Multi-Agent Research Proposal System. The project uses this directory to quality assurance:

>**🧪 Evaluations (`eval/`)**: Full, end-to-end integration tests using real LLM calls against defined scenarios.
---

## 📋 Prerequisites

Before running any scripts, ensure your environment is set up correctly:

1.  **Environment Variables**: Ensure a `.env` file exists in the project root containing your Google Cloud credentials:
    ```bash
    GOOGLE_API_KEY=your_api_key_here (optional)
    GCP_PROJECT_ID=your_project_id
    ```
2.  **Dependencies**: The project must be installed with development dependencies.
    ```bash
    # Using uv (recommended)
    uv sync
    
    # Or standard pip
    pip install -r requirements.txt
    ```
3.  **Working Directory**: All commands below must be executed from the **project root directory** to ensure Python imports resolve correctly.

---

## 🧪 Evaluation Pipeline (`eval/`)

The evaluation system allows you to run the full Multi-Agent chain (Problem Formulation → Objectives → Methodology → Data Collection → Quality Control) against pre-defined user scenarios.

**Why this is important:** It ensures that changes to prompts or models do not break the JSON structure, chain-of-thought logic, or data passing between agents.

### Main Script: `test_multi_agent_pipeline.py`
This script evaluates one test case at a time to avoid API rate limits.

**Features:**
*   ✅ **JSON-based Test Cases**: Defined in `eval/data/`.
*   ✅ **Real API Calls**: Uses the actual Gemini models (not mocks).
*   ✅ **Validation**: Checks for valid JSON, required fields, and logical constraints (e.g., "Problem Statement must be > 50 chars").

### How to Run Evaluations

#### 1. List Available Scenarios
To see which test cases are available:
```bash
python eval/test_multi_agent_pipeline.py --list
```

**Available Scenarios:**
*   **`scenario_1_ml_research`**: Master's in CS (Multi-Agent Systems). Standard flow.
*   **`scenario_2_bio_data`**: PhD in Biology (Genomics). High complexity.
*   **`scenario_3_engineering`**: Master's in Engineering (Sustainable Energy).
*   **`scenario_4_tight_timeline`**: Undergrad in Psychology. Edge case: tight 3-month timeline.

#### 2. Run a Specific Scenario
Run the full pipeline for a specific test case:
```bash
python eval/test_multi_agent_pipeline.py scenario_1_ml_research
```

#### 3. Change the Model
By default, tests run on `gemini-2.0-flash-lite`. You can specify a different model:
```bash
python eval/test_multi_agent_pipeline.py scenario_1_ml_research --model gemini-1.5-pro
```

### Understanding the Output
Artifacts are automatically saved to the **`eval/output/`** directory:

1.  **Report (`report_*.txt`)**: A human-readable summary.
    *   **Note on "PASSED"**: This indicates the agent produced *valid structure* and met technical criteria.
    *   **Quality vs. Validity**: It is normal for the **Quality Control Agent** to output `Passed: False` (meaning the research needs refinement) while the Evaluation Report says `✅ PASSED` (meaning the agent successfully ran).
2.  **Results (`results_*.json`)**: The full raw JSON output from every agent, useful for debugging.

### Validation Criteria
Each agent output is strictly validated against these rules:

| Agent | Key Checks |
|-------|-----------|
| **Problem Formulation** | Required fields, literature count (3-5), no fabricated links, valid URLs. |
| **Objectives** | SMART criteria, specific objectives count (3-6), feasibility notes included. |
| **Methodology** | Valid type (quant/qual/mixed), justification provided. |
| **Data Collection** | Tools recommended, sample size is numeric and reasonable (≥10). |
| **Quality Control** | Numeric scores (0-100), validation boolean present. |

---

## ⚠️ Troubleshooting

**`ModuleNotFoundError: No module named 'aida'`**
*   **Cause**: You are likely running the script from inside the `eval/` or `demos/` folder.
*   **Fix**: Always run from the **project root**: `python eval/test_multi_agent_pipeline.py ...`.

**`429 Resource Exhausted`**
*   **Cause**: Hitting Gemini API rate limits.
*   **Fix**: Wait 60 seconds or switch to `gemini-2.0-flash-lite`.

**`App name mismatch detected...`**
*   **Cause**: A harmless warning from the `google.adk` library regarding agent initialization paths.
*   **Fix**: Ignore this warning; it does not affect execution.
```