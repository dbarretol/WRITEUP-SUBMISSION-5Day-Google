# Test Suite Documentation

This directory contains the comprehensive test suite for the **Academic Research Proposal System**. It includes unit tests for individual agents, integration tests for the orchestrator, and utility tests for infrastructure components.

## 📋 Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Test Inventory](#test-inventory)
- [Running Tests](#running-tests)
- [Best Practices](#best-practices)

---

## Overview

The test suite is designed to ensure the reliability and correctness of the multi-agent system. It primarily uses **mocked agents** to verify logic, state transitions, and data handling without incurring API costs.

**Key Features:**
- **Unit Tests**: Verify individual agent configuration and prompt formatting.
- **Integration Tests**: Verify the `ResearchProposalOrchestrator` workflow and state machine.
- **Infrastructure Tests**: Verify state persistence and communication protocols.
- **Async Support**: Fully supports asynchronous agent execution using `pytest-asyncio`.

---

## Prerequisites

To run the tests, you need the following environment setup:

1.  **Python Version**: 3.10 or higher
2.  **Package Manager**: `uv` (recommended) or `pip`
3.  **Dependencies**: Installed via `uv sync` or `pip install -r requirements.txt`

**Key Libraries:**
- `pytest`: The testing framework
- `pytest-asyncio`: For async test support
- `pytest-cov`: For code coverage reporting
- `unittest.mock`: For mocking external dependencies (LLMs, APIs)

---

## Test Inventory

The tests are organized by component:

### 🤖 Agent Tests
Verify agent initialization, configuration, and prompt generation.

| File | Component | Description |
|------|-----------|-------------|
| `test_problem_formulation_agent.py` | Problem Formulation | Tests prompt formatting and tool integration |
| `test_objectives_agent.py` | Objectives | Tests SMART objective generation logic |
| `test_methodology_agent.py` | Methodology | Tests methodology recommendation logic |
| `test_data_collection_agent.py` | Data Collection | Tests data plan generation |
| `test_quality_control_agent.py` | Quality Control | Tests validation scoring and feedback loops |
| `test_interviewer_agent.py` | Interviewer | Tests profile collection logic |
| `test_literature_review.py` | Literature Review | Tests the specialized literature review sub-agent |

### 🎼 Orchestration Tests
Verify the central coordination logic.

| File | Component | Description |
|------|-----------|-------------|
| `test_orchestrator.py` | Orchestrator | **Critical**: Tests full workflow, state transitions, and refinement loops |

### 🔧 Infrastructure & Tool Tests
Verify underlying systems and tools.

| File | Component | Description |
|------|-----------|-------------|
| `test_state_management.py` | State Manager | Tests persistence to `.gemini/` folder |
| `test_communication.py` | Messaging | Tests the internal message bus |
| `test_google_search.py` | Google Search | Tests the search tool integration |

---

## Running Tests

We recommend using `uv` to run tests in the virtual environment.

### 1. Run All Tests (Recommended)
Executes the entire suite.
```bash
uv run pytest tests/
```

### 2. Run with Coverage Report
Checks how much of the codebase is covered by tests.
```bash
uv run pytest tests/ --cov=academic_research
```

### 3. Run Specific Test File
Useful when working on a specific component.
```bash
uv run pytest tests/test_orchestrator.py
```

### 4. Run Verbose Mode
Shows detailed output for each test case.
```bash
uv run pytest tests/ -v
```

---

## Best Practices

1.  **Mock External APIs**: Always mock LLM responses and API calls in unit tests to ensure speed and avoid costs. Use `unittest.mock` or `AsyncMock`.
2.  **Test State Transitions**: When modifying workflow logic, add tests to `test_orchestrator.py` to verify valid/invalid transitions.
3.  **Async Tests**: Use `@pytest.mark.asyncio` decorator for any test involving `await`.
4.  **Coverage**: Aim for high coverage in `data_models.py` and `orchestrator.py` as they are the backbone of the system.

---

## Troubleshooting

### "Async def functions are not natively supported"
**Cause**: Missing `@pytest.mark.asyncio` decorator.
**Fix**: Ensure `pytest-asyncio` is installed and decorate your async test functions.

### "ModuleNotFoundError"
**Cause**: Python path issues.
**Fix**: Run tests using `uv run pytest` which handles python path automatically, or set `PYTHONPATH=.`
