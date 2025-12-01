# Demo Scripts

This directory contains demonstration scripts that show how to use the **Academic Research Proposal System** agents and tools.

## 📋 Table of Contents

- [Why Demos Matter](#why-demos-matter)
- [Available Demos](#available-demos)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Running the Demos](#running-the-demos)
- [Troubleshooting](#troubleshooting)

---

## Why Demos Matter

The demos in this directory serve three critical purposes:

1. **Learning Tool** - Understand how each agent works independently and how they coordinate in the full workflow
2. **Integration Examples** - See practical code examples for integrating agents into your own applications
3. **Manual Testing** - Verify agent functionality during development and after changes

Each demo is a standalone script that can be run independently, making it easy to explore specific components without running the entire system.

---

## Available Demos

### 🤖 Individual Agent Demos (Real API Calls)

These scripts demonstrate how to use each specialized agent independently. **Note**: These make real API calls to Google's Gemini API via Vertex AI.

#### `demo_problem_formulation.py`
**Purpose**: Demonstrates the Problem-Formulation Agent  
**What it does**:
- Generates research problem definitions based on user profile
- Uses Google Search tool for preliminary literature review
- Formats output as structured JSON with problem statement, research questions, and key variables
- Shows how to integrate search results into problem formulation

**Why it's important**: This is the foundation of the research proposal - understanding how to formulate a clear, researchable problem is critical.

#### `demo_objectives.py`
**Purpose**: Demonstrates the Objectives Agent  
**What it does**:
- Generates SMART (Specific, Measurable, Achievable, Relevant, Time-bound) objectives
- Performs feasibility checks against user constraints (time, skills, resources)
- Validates alignment with the research problem
- Provides both general and specific objectives

**Why it's important**: Shows how the system ensures objectives are realistic and achievable within student constraints.

#### `demo_methodology.py`
**Purpose**: Demonstrates the Methodology Agent  
**What it does**:
- Recommends appropriate research methodologies (qualitative, quantitative, mixed)
- Provides detailed justification for recommendations
- Analyzes timeline fit and required skills
- Suggests alternative methodologies with pros/cons

**Why it's important**: Illustrates how the system matches methodology to student skills and timeline constraints.

#### `demo_data_collection.py`
**Purpose**: Demonstrates the Data-Collection Agent  
**What it does**:
- Plans data collection strategies and techniques
- Recommends specific tools and data sources
- Estimates sample sizes and resource requirements
- Provides timeline breakdown for data collection phases

**Why it's important**: Shows how the system creates practical, actionable data collection plans.

#### `demo_quality_control.py`
**Purpose**: Demonstrates the Quality-Control Agent  
**What it does**:
- Validates proposal coherence and feasibility
- Provides numerical scores (coherence_score, feasibility_score, overall_quality_score)
- Identifies specific issues and inconsistencies
- Suggests targeted refinements when needed
- Determines if proposal requires iteration

**Why it's important**: Demonstrates the system's self-validation and refinement loop mechanism.

---

### 🔄 Full Workflow Demo (Mocked)

#### `demo_orchestrator.py`
**Purpose**: Demonstrates the complete multi-agent orchestration workflow  
**What it does**:
- Shows all state transitions (INIT → INTERVIEWING → PROBLEM_FORMULATION → OBJECTIVES → METHODOLOGY → DATA_COLLECTION → QUALITY_CONTROL → COMPLETE)
- Uses **mocked agent responses** (no API calls required)
- Demonstrates progress tracking and workflow coordination
- Shows how agents pass information between stages
- Illustrates the refinement loop (though mock uses 0 iterations)

**Why it's important**: This is the **best starting point** - it shows the entire system in action without consuming API quota. Essential for understanding system architecture and agent coordination.

---

### 🔧 Utility Demos

#### `demo_search_wrapper.py` (THIS IS NOT YET INTEGRATED IN THE MULTIAGENT SYSTEM!)
**Purpose**: Demonstrates the AcademicSearchWrapper tool  
**What it does**:
- Shows how to build optimized academic search queries
- Demonstrates parsing and structuring search results
- Illustrates relevance scoring and ranking algorithms
- Shows citation formatting in multiple styles (APA, IEEE, Chicago, Harvard)
- Formats results for the `preliminary_literature` field

**Why it's important**: The search wrapper is used by multiple agents. Understanding how it works helps you customize search behavior and citation formatting.

---

## Prerequisites

### 1. Python Version
- **Required**: Python 3.10, 3.11, or 3.12
- Check your version: `python --version`

### 2. Install Dependencies

This project uses `uv` as the package manager. Install dependencies:

```bash
# Install uv if you don't have it
pip install uv

# Install project dependencies
uv sync
```

### 3. Environment Configuration

Create a `.env` file in the project root with your Google Cloud credentials:

```bash
# Copy the example file
cp .env.example .env
```

Edit `.env` and fill in your values:

```env
GOOGLE_GENAI_USE_VERTEXAI=1
GOOGLE_CLOUD_PROJECT=<YOUR_PROJECT_ID>
GOOGLE_CLOUD_LOCATION=<YOUR_PROJECT_LOCATION>  # e.g., us-central1
GOOGLE_CLOUD_STORAGE_BUCKET=<YOUR_STORAGE_BUCKET>  # Only for deployment
```

**Required for demos**:
- `GOOGLE_CLOUD_PROJECT` - Your GCP project ID
- `GOOGLE_CLOUD_LOCATION` - Your GCP region (e.g., `us-central1`)

### 4. Google Cloud Setup

Ensure you have:
- A Google Cloud Project with Vertex AI API enabled
- Appropriate authentication configured (Application Default Credentials)
- Gemini API access in your project

---

## Quick Start

**Recommended order for first-time users**:

1. **Start with the orchestrator** (no API calls, fast):
   ```bash
   cd <project-root>
   .venv\Scripts\Activate.ps1  # Windows PowerShell
   # OR
   source .venv/bin/activate    # Linux/Mac
   
   python demos/demo_problem_formulation.py
   ```

2. **Run an individual agent demo** (real API call):
   ```bash
   python demos/demo_problem_formulation.py
   ```

---

## Running the Demos

### Standard Execution

From the project root directory:

```bash
# 1. Navigate to project root
cd <project-root>

# 2. Activate virtual environment
.venv\Scripts\Activate.ps1  # Windows PowerShell
# OR
source .venv/bin/activate    # Linux/Mac

# 3. Run any demo
python demos/<DEMO_SCRIPT>.py
```

### Examples

```bash
# Full workflow (mocked, no API calls)
python demos/demo_orchestrator.py

# Individual agents (real API calls)
python demos/demo_problem_formulation.py
python demos/demo_objectives.py
python demos/demo_methodology.py
python demos/demo_data_collection.py
python demos/demo_quality_control.py

```

---

## Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'academic_research'`

**Solution**: Make sure you're running from the project root and the virtual environment is activated:

```bash
cd <project-root>
.venv\Scripts\Activate.ps1  # Windows
python demos/demo_xxx.py
```

If the issue persists, set PYTHONPATH explicitly:

```bash
# Windows PowerShell
$env:PYTHONPATH="<project-root>"; python demos/demo_xxx.py

# Linux/Mac
PYTHONPATH=<project-root> python demos/demo_xxx.py
```

### Issue: API Authentication Errors

**Solution**: Verify your `.env` file is configured correctly and you have valid GCP credentials:

```bash
# Check if .env exists
ls .env

# Verify GCP authentication
gcloud auth application-default login
```

### Issue: Vertex AI API Not Enabled

**Solution**: Enable the Vertex AI API in your GCP project:

```bash
gcloud services enable aiplatform.googleapis.com --project=<YOUR_PROJECT_ID>
```

### Issue: Demo Output is Truncated

**Solution**: This is normal for terminal output. The demos complete successfully even if output appears truncated. Check the exit code:

```bash
python demos/demo_xxx.py
echo $?  # Linux/Mac
echo $LASTEXITCODE  # Windows PowerShell
# Should return 0 for success
```

---

## Expected Output

### Mocked Demos (`demo_orchestrator.py`)
- Completes in seconds
- Shows state transitions
- Displays final proposal summary
- Exit code: 0

### Real API Demos (individual agents)
- Takes 10-30 seconds depending on API response time
- Shows "[INFO] Configured for Vertex AI" message
- Displays structured JSON output
- Exit code: 0

### Utility Demos (`demo_search_wrapper.py`)
- Completes instantly (no API calls)
- Shows formatted examples
- Demonstrates tool capabilities
- Exit code: 0

---

## For Developers

### Usage Patterns

**When to use each demo**:

| Demo | Use Case |
|------|----------|
| `demo_orchestrator.py` | Understanding system architecture, testing workflow changes |
| Individual agent demos | Testing specific agent modifications, understanding agent inputs/outputs |
| `demo_search_wrapper.py` | Customizing search behavior, testing citation formatting |
| `debug_agent.py` | Debugging agent configuration issues |

### Integration Examples

Each demo shows how to:
- Initialize agents with proper configuration
- Use `InMemoryRunner` for agent execution
- Parse and validate agent responses
- Handle errors and edge cases

### Testing During Development

Use demos for manual testing:
1. Make changes to agent code
2. Run relevant demo to verify behavior
3. Check output format and content
4. Verify no regressions

For automated testing, see the `eval/` directory instead.

---

## Additional Resources

- **Main README**: [../README.md](../README.md) - Project overview and setup
- **Architecture Docs**: [../docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) - System design
- **Agent Guide**: [../docs/AGENT_GUIDE.md](../docs/AGENT_GUIDE.md) - Detailed agent documentation
- **Evaluation**: [../eval/README.md](../eval/README.md) - Automated testing and metrics
