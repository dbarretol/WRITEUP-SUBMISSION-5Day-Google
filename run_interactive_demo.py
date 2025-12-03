import asyncio
import os
import sys
import json
from dotenv import load_dotenv

# 1. Setup Environment
load_dotenv()
sys.path.insert(0, ".")

# Import your Specific Class
from aida.sub_agents.interviewer.agent import InterviewerAgent
from aida.data_models import InterviewState, UserProfile, Timeline
from aida.config import DEFAULT_MODEL

# Import other agents (Factory functions for the backend workers)
from aida.sub_agents.problem_formulation import create_problem_formulation_agent
from aida.sub_agents.objectives import create_objectives_agent
from aida.sub_agents.methodology import create_methodology_agent
from aida.sub_agents.data_collection import create_data_collection_agent
from aida.sub_agents.quality_control import create_quality_control_agent

# Import Orchestrator
from aida.orchestrator import ResearchProposalOrchestrator
from google.adk.runners import InMemoryRunner

def print_agent(text):
    print(f"\n🤖 \033[94mAgent:\033[0m {text}")

def print_system(text):
    print(f"\n⚙️  \033[93mSystem:\033[0m {text}")

async def main():
    print("\n" + "="*60)
    print("  🎓 ACADEMIC RESEARCH ASSISTANT - LIVE DEMO")
    print("="*60)

    # ---------------------------------------------------------
    # PHASE 1: THE INTERVIEW (Interactive)
    # ---------------------------------------------------------
    print_system("Initializing Interviewer...")

    # 1. Instantiate your Custom Class
    interviewer = InterviewerAgent(model=DEFAULT_MODEL)
    
    # 2. Initialize State
    state = InterviewState(
        current_question_index=0, 
        profile_data={}, 
        is_complete=False
    )

    # 3. Trigger First Question (Send empty input to start)
    initial_turn = interviewer.process_turn("", state)
    print_agent(initial_turn["response"])
    state = initial_turn["state"]

    # 4. The Chat Loop
    while not state.is_complete:
        user_input = input("\n👤 \033[92mYou:\033[0m ").strip()
        
        if user_input.lower() in ['quit', 'exit']:
            print_system("Exiting demo.")
            return

        # Call your custom method
        result = interviewer.process_turn(user_input, state)
        
        state = result["state"]
        print_agent(result["response"])

    # ---------------------------------------------------------
    # PHASE 2: PREPARE DATA FOR ORCHESTRATOR
    # ---------------------------------------------------------
    print_system("Interview Complete. Compiling Profile...")
    
    raw = state.profile_data
    
    # Helper to parse the timeline dict/string safely
    t_val = 6
    t_unit = "months"
    if isinstance(raw.get("total_timeline"), dict):
        t_val = raw["total_timeline"].get("value", 6)
        t_unit = raw["total_timeline"].get("unit", "months")

    # Create the Pydantic Object
    user_profile = UserProfile(
        academic_program=raw.get("academic_program", "Master's"),
        field_of_study=raw.get("field_of_study", "General"),
        research_area=raw.get("research_area", "Unspecified"),
        weekly_hours=int(raw.get("weekly_hours", 20)),
        total_timeline=Timeline(value=t_val, unit=t_unit),
        existing_skills=raw.get("existing_skills", []),
        missing_skills=raw.get("missing_skills", []),
        constraints=raw.get("constraints", []),
        additional_context=raw.get("additional_context", "")
    )
    
    print_system(f"Profile Object Created: {user_profile.research_area}")

    # ---------------------------------------------------------
    # PHASE 3: ORCHESTRATION (Autonomous)
    # ---------------------------------------------------------
    print_system("Initializing Backend Agents for Research Workflow...")
    
    # Initialize backend agents using their factory functions
    backend_agents = {
        'interviewer': interviewer, 
        'problem_formulation': create_problem_formulation_agent(model=DEFAULT_MODEL),
        'objectives': create_objectives_agent(model=DEFAULT_MODEL),
        'methodology': create_methodology_agent(model=DEFAULT_MODEL),
        'data_collection': create_data_collection_agent(model=DEFAULT_MODEL),
        'quality_control': create_quality_control_agent(model=DEFAULT_MODEL)
    }

    # Initialize Runner (Required for the backend agents)
    runner = InMemoryRunner(agent=backend_agents['problem_formulation'])

    # Initialize Orchestrator
    def progress_callback(step, pct):
        print(f"  [Progress] {step}: {int(pct)}%")

    orchestrator = ResearchProposalOrchestrator(progress_callback=progress_callback)

    print_system("Running Workflow... (Please wait)")
    
    # Execute
    try:
        result = await orchestrator.run_workflow(
            agents=backend_agents,
            runner=runner,
            initial_profile=user_profile
        )

        if result["success"]:
            print("\n" + "="*60)
            print("  ✅ RESEARCH PROPOSAL GENERATED")
            print("="*60)
            
            p = result["proposal"]
            
            # 1. Problem Definition
            print(f"\n📄 \033[1mProblem Statement:\033[0m")
            if p.get('problem_definition'):
                print(p['problem_definition']['problem_statement'])
                
                # Print Literature Found
                lit = p['problem_definition'].get('preliminary_literature', [])
                if lit:
                    print(f"\n📚 \033[1mLiterature Found:\033[0m")
                    for item in lit:
                        print(f"  - {item.get('title', 'Unknown')} ({item.get('url', 'No URL')})")
            
            # 2. Objectives
            if p.get('research_objectives'):
                print(f"\n🎯 \033[1mObjectives:\033[0m")
                for obj in p['research_objectives']['specific_objectives']:
                    print(f"  - {obj}")
                
            # 3. Methodology
            if p.get('methodology'):
                print(f"\n🧪 \033[1mMethodology:\033[0m")
                print(f"  {p['methodology']['recommended_methodology']}")

            # 4. Validation
            if p.get('quality_validation'):
                quality_score = p['quality_validation'].get('overall_quality_score')
                if quality_score is None:
                    # Fallback calculation
                    coherence = p['quality_validation'].get('coherence_score', 0)
                    feasibility = p['quality_validation'].get('feasibility_score', 0)
                    quality_score = ((coherence + feasibility) / 2) * 100
                print(f"\n✅ \033[1mValidation Score:\033[0m {quality_score:.0f}/100")
            
            # Save file
            with open("final_proposal.json", "w") as f:
                json.dump(p, f, indent=2)
            print("\n💾 Saved to final_proposal.json")
            
        else:
            print(f"\n❌ Workflow Error: {result['error']}")

    except Exception as e:
        print(f"\n❌ Execution Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())