# AIDA: Academic Ideation & Drafting Assistant

**Subtitle:**
Empowering students to generate feasible, personalized research proposals via a Gemini-powered multi-agent workflow.

**Project Description:**

### The Context: A Crisis of Confidence in Academic Research

I am a university professor in Peru responsible for coordinating and teaching research courses. In my region, we face a specific challenge: while our students are talented, we lack a deeply ingrained national culture of scientific investigation. For many students, the "Research Proposal" is not an exciting beginning to discovery; it is a terrifying bureaucratic hurdle required for graduation.

I currently witness a recurring cycle of failure: students delay starting because they feel overwhelmed. When they finally begin, they propose topics that are vastly out of scope, unachievable within the academic semester, or misaligned with their actual technical skills and resource constraints. Because of large class sizes, it is impossible for me to provide the 10-20 hours of personalized mentoring per student required to properly refine an initial idea.

The result? Students feel demotivated, view research as a "boredom" to be endured, and often produce low-quality work simply to pass. This stifles the development of critical thinking and scientific inquiry that our country desperately needs.

### The Solution: AIDA (Academic Ideation & Drafting Assistant)

To solve this, I built **AIDA**. AIDA is not merely a chatbot wrapper; it is a sophisticated **Multi-Agent System** designed to emulate a full Academic Advisory Committee.

Unlike a standard LLM session where a student might prompt "Write me a thesis proposal,"—resulting in a generic, often hallucinated project—AIDA flips the script. It acts as a guide, an interviewer, and a strict critic. It does not just *write* for the student; it *extracts* the research potential from the student, ensuring the final output is tailored to their specific reality.

### Why Agents? The Need for Specialized Personas

A single LLM prompt cannot sustain the context, nuance, and conflicting perspectives required for academic rigor. A robust research proposal requires distinct "hats":

1.  **The Interviewer:** Needs to be empathetic but inquisitive.
2.  **The Researcher:** Needs to be expansive and creative.
3.  **The Critic:** Needs to be restrictive and skeptical.

If you ask one model to do all three, the "Yes-Man" bias of LLMs often takes over. By using an **Agentic Architecture**, I was able to separate these concerns. I created distinct agents with distinct system instructions. The "Quality Control" agent, for example, is explicitly instructed *not* to generate text, but only to critique it. This separation ensures that the system checks for feasibility and alignment before the student ever sees the final draft.

### System Architecture & Technical Implementation

AIDA is built using **Python 3.10+**, leveraging **Google's Gemini** models for cognition and **Pydantic** for strict data validation. The system follows the **Orchestrator Pattern**, inspired by the Google Agent Development Kit (ADK) but significantly modified for this domain.

![](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F19372404%2F122a9fb28f40e412c00cb9b17ff2592b%2Facademic-research.svg?generation=1764615008251337&alt=media)

#### 1. The Orchestrator (State Management)

At the heart of the system is the Orchestrator. It acts as a finite state machine, managing the transition between different stages of the research workflow. It maintains the global state—the `StudentProfile`, the emerging `ProposalDraft`, and the `FeedbackHistory`. It routes messages via a custom Pub/Sub event bus, ensuring that agents only receive the information relevant to their specific task.

#### 2. The Agent Workflow

The system proceeds through a logical, academic pipeline:

*   **Step 1: The Interviewer Agent (Profile Gathering)**
    This agent initiates the conversation. It does not ask generic questions. It dynamically queries the student about their *constraints*: "How many months do you have?", "Do you have access to a lab?", "What is your budget?", "What programming languages do you know?". This creates a `UserProfile` object that serves as the boundary conditions for the rest of the agents.

*   **Step 2: Problem Formulation & Literature Review (Grounding)**
    Once the profile is set, the Problem Formulation Agent drafts a research gap. Crucially, it delegates tasks to a **Literature Review Sub-Agent**. This sub-agent utilizes **Tool Calling** (specifically Google Search integration) to validate that the problem hasn't already been solved and to find real, existing references. This reduces hallucination—a critical requirement in academia.

*   **Step 3: Objectives & Methodology (Feasibility Check)**
    Separate agents generate SMART objectives and a Methodology. The Methodology Agent is context-aware; if the `UserProfile` indicates the student has no budget, the agent will not propose a methodology requiring expensive paid datasets or proprietary software.

*   **Step 4: The Quality Control Loop (Self-Correction)**
    This is the most innovative feature of AIDA. Once a draft is compiled, it is passed to the **Quality Control (QC) Agent**. This agent acts as the "Strict Professor." It evaluates the proposal against a pre-defined rubric (Alignment, Feasibility, Novelty).

    *   **The Refinement Loop:** If the QC Agent assigns a failing grade, the draft is **not** shown to the student. Instead, the system enters a refinement loop. The QC Agent sends structured feedback back to the Problem Formulation or Methodology agents, forcing them to iterate and improve the draft. This mimics the drafting process of a real researcher.

#### 3. Technical Stack

*   **Core Logic:** Google Gemini (via Vertex AI).

*   **Data Validation:** **Pydantic**. I avoided using free-text dictionaries. Every agent outputs structured JSON that is validated against Pydantic models (e.g., `ResearchProposal`, `MethodologySection`). This ensures type safety and prevents the pipeline from breaking due to malformed LLM outputs.

*   **User Interface:** **Streamlit**. I built a web-based frontend that allows students to chat naturally with the Interviewer agent, visualizes the "thinking process" of the background agents via a progress bar, and renders the final proposal in clean Markdown.

*   **Deployment:** The project is containerized and configured for deployment on the **Cloud Run** serverless service, ensuring scalability for university-wide usage.

### Challenges and Learnings

The biggest challenge was prompt engineering the "Quality Control" agent. Initially, it was too lenient. I learned that for an agent to be a good critic, the prompt needs to explicitly forbid positive reinforcement and focus strictly on logical fallacies and resource mismatches.

Additionally, managing the context window was a technical hurdle. Passing the entire conversation history to every agent was inefficient and costly. I implemented a message router that selects only the relevant context (e.g., the Methodology agent needs the `ProblemStatement` and `UserProfile`, but doesn't need to know the student's greeting or small talk).

### Conclusion & Impact
AIDA is not designed to replace the work of the student; it is designed to replace the *barrier to entry*. By automating the structural and feasibility checks, AIDA allows students to skip the "blank page paralysis."

For a student in Peru, AIDA means the difference between a rejected proposal and a viable path to graduation. It teaches them that research is not about magic, but about structure. By interacting with the system, they unknowingly learn the scientific method—learning how to narrow a scope, how to define an objective, and how to match a method to a problem.

This project demonstrates the power of Gemini and multi-agent systems not just to generate text, but to structure thought and democratization access to high-quality academic mentorship.

Cloud Run: https://aida-research-agent-1006951032226.us-central1.run.app