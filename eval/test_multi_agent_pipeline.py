"""
Multi-Agent Research Proposal System - Single Test Case Evaluation

This script evaluates one test case at a time to avoid API rate limits.
Test cases are loaded from JSON files in the data/ directory.

Usage:
    python eval/test_multi_agent_pipeline.py scenario_1_ml_research
    python eval/test_multi_agent_pipeline.py scenario_2_bio_data
    python eval/test_multi_agent_pipeline.py --list
"""

import asyncio
import json
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from aida.data_models import UserProfile, Timeline
from aida.sub_agents.problem_formulation import (
    create_problem_formulation_agent,
    format_prompt_for_user_profile
)
from aida.sub_agents.objectives import (
    create_objectives_agent,
    format_prompt_for_objectives
)
from aida.sub_agents.methodology import (
    create_methodology_agent,
    format_prompt_for_methodology
)
from aida.sub_agents.data_collection import (
    create_data_collection_agent,
    format_prompt_for_data_collection
)
from aida.sub_agents.quality_control import (
    create_quality_control_agent,
    format_prompt_for_quality_control
)

from google.adk.runners import InMemoryRunner
from google.genai import types

# Load environment variables (force override of system variables)
load_dotenv(override=True)

# Directory containing test case JSON files
DATA_DIR = Path(__file__).parent / "data"


# ============================================================================
# TEST CASE LOADING
# ============================================================================

def load_test_case(scenario_id: str) -> Dict[str, Any]:
    """Load a test case from JSON file."""
    test_file = DATA_DIR / f"{scenario_id}.json"
    
    if not test_file.exists():
        raise FileNotFoundError(
            f"Test case '{scenario_id}' not found at {test_file}"
        )
    
    with open(test_file, 'r') as f:
        data = json.load(f)
    
    return data


def list_available_tests() -> List[str]:
    """List all available test cases."""
    test_files = list(DATA_DIR.glob("scenario_*.json"))
    return [f.stem for f in sorted(test_files)]


def create_user_profile_from_json(data: Dict[str, Any]) -> UserProfile:
    """Convert JSON data to UserProfile object."""
    profile_data = data["user_profile"]
    
    return UserProfile(
        academic_program=profile_data["academic_program"],
        field_of_study=profile_data["field_of_study"],
        research_area=profile_data["research_area"],
        weekly_hours=profile_data["weekly_hours"],
        total_timeline=Timeline(
            value=profile_data["total_timeline"]["value"],
            unit=profile_data["total_timeline"]["unit"]
        ),
        existing_skills=profile_data["existing_skills"],
        missing_skills=profile_data["missing_skills"],
        constraints=profile_data["constraints"],
        additional_context=profile_data.get("additional_context")
    )


# ============================================================================
# VALIDATION UTILITIES
# ============================================================================

class AgentOutputValidator:
    """Validates outputs from each agent with specific criteria."""
    
    @staticmethod
    def validate_problem_definition(output: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Problem-Formulation Agent output."""
        issues = []
        warnings = []
        
        # Check required fields
        required_fields = ["problem_statement", "main_research_question", 
                          "secondary_questions", "key_variables", "preliminary_literature"]
        for field in required_fields:
            if field not in output:
                issues.append(f"Missing required field: {field}")
        
        # Validate problem statement length
        if "problem_statement" in output:
            if len(output["problem_statement"]) < 50:
                warnings.append("Problem statement seems too short (< 50 chars)")
            elif len(output["problem_statement"]) > 500:
                warnings.append("Problem statement seems too long (> 500 chars)")
        
        # Validate literature
        if "preliminary_literature" in output:
            lit_count = len(output["preliminary_literature"])
            if lit_count == 0:
                warnings.append("No literature found - google_search may have failed")
            elif lit_count < 3:
                warnings.append(f"Only {lit_count} literature entries (expected 3-5)")
            
            # Check for placeholder links
            for lit in output["preliminary_literature"]:
                if "link" in lit:
                    link = lit["link"].upper()
                    if any(p in link for p in ["N/A", "EXAMPLE", "PLACEHOLDER"]):
                        issues.append(f"Fabricated link detected: {lit['title']}")
                    if not link.startswith(("HTTP://", "HTTPS://")):
                        issues.append(f"Invalid URL format: {lit['link']}")
        
        # Validate secondary questions
        if "secondary_questions" in output:
            if len(output["secondary_questions"]) < 2:
                warnings.append("Only 1 secondary question (expected 2-4)")
            elif len(output["secondary_questions"]) > 5:
                warnings.append("Too many secondary questions (> 5)")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }
    
    @staticmethod
    def validate_objectives(output: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Objectives Agent output."""
        issues = []
        warnings = []
        
        # Check required fields
        required_fields = ["general_objective", "specific_objectives", "feasibility_notes"]
        for field in required_fields:
            if field not in output:
                issues.append(f"Missing required field: {field}")
        
        # Validate SMART criteria for specific objectives
        if "specific_objectives" in output:
            if len(output["specific_objectives"]) < 3:
                warnings.append("Less than 3 specific objectives")
            elif len(output["specific_objectives"]) > 6:
                warnings.append("More than 6 specific objectives (may be too many)")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }
    
    @staticmethod
    def validate_methodology(output: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Methodology Agent output."""
        issues = []
        warnings = []
        
        # Check required fields
        required_fields = ["recommended_methodology", "methodology_type", 
                          "justification", "required_skills"]
        for field in required_fields:
            if field not in output:
                issues.append(f"Missing required field: {field}")
        
        # Validate methodology type
        if "methodology_type" in output:
            valid_types = ["quantitative", "qualitative", "mixed-methods"]
            if output["methodology_type"].lower() not in valid_types:
                warnings.append(f"Unusual methodology type: {output['methodology_type']}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }
    
    @staticmethod
    def validate_data_collection(output: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Data-Collection Agent output."""
        issues = []
        warnings = []
        
        # Check required fields
        required_fields = ["collection_techniques", "recommended_tools", 
                          "estimated_sample_size", "timeline_breakdown"]
        for field in required_fields:
            if field not in output:
                issues.append(f"Missing required field: {field}")
        
        # Validate tools
        if "recommended_tools" in output:
            if len(output["recommended_tools"]) == 0:
                warnings.append("No tools recommended")
        
        # Validate sample size
        if "estimated_sample_size" in output:
            try:
                size = int(output["estimated_sample_size"])
                if size < 10:
                    warnings.append(f"Very small sample size: {size}")
            except (ValueError, TypeError):
                pass
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }
    
    @staticmethod
    def validate_quality_control(output: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Quality-Control Agent output."""
        issues = []
        warnings = []
        
        # Check required fields (based on actual QualityValidation model)
        required_fields = ["validation_passed", "coherence_score", "feasibility_score",
                          "issues_identified", "recommendations", "requires_refinement", "overall_quality_score"]
        for field in required_fields:
            if field not in output:
                issues.append(f"Missing required field: {field}")
        
        # Validate coherence score
        if "coherence_score" in output:
            score = output["coherence_score"]
            if not isinstance(score, (int, float)):
                issues.append(f"Coherence score should be numeric, got: {type(score)}")
            elif score < 0 or score > 1:
                issues.append(f"Coherence score out of range (0-1): {score}")
        
        # Validate feasibility score
        if "feasibility_score" in output:
            score = output["feasibility_score"]
            if not isinstance(score, (int, float)):
                issues.append(f"Feasibility score should be numeric, got: {type(score)}")
            elif score < 0 or score > 1:
                issues.append(f"Feasibility score out of range (0-1): {score}")

        # Validate overall quality score
        if "overall_quality_score" in output:
            score = output["overall_quality_score"]
            if not isinstance(score, (int, float)):
                issues.append(f"Overall quality score should be numeric, got: {type(score)}")
            elif score < 0 or score > 100:
                issues.append(f"Overall quality score out of range (0-100): {score}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }


# ============================================================================
# PIPELINE EXECUTOR
# ============================================================================

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _clean_json_response(text: str) -> str:
    """Clean markdown formatting from JSON response."""
    clean_text = text.strip()
    if clean_text.startswith("```json"):
        clean_text = clean_text[7:]
    elif clean_text.startswith("```"):
        clean_text = clean_text[3:]
    if clean_text.endswith("```"):
        clean_text = clean_text[:-3]
    return clean_text.strip()

# ============================================================================
# PIPELINE EXECUTOR
# ============================================================================

async def run_full_pipeline(
    test_case_data: Dict[str, Any],
    model: str = "gemini-2.0-flash-lite"
) -> Dict[str, Any]:
    """
    Run the complete multi-agent pipeline for a given test case.
    
    Returns a dictionary with outputs from all agents and validation results.
    """
    scenario_name = test_case_data["eval_id"]
    user_profile = create_user_profile_from_json(test_case_data)
    
    print(f"\n{'='*80}")
    print(f"TEST CASE: {test_case_data['name']}")
    print(f"{'='*80}")
    print(f"Description: {test_case_data['description']}")
    print(f"Program: {user_profile.academic_program}")
    print(f"Field: {user_profile.field_of_study}")
    print(f"Area: {user_profile.research_area}\n")
    
    results = {
        "scenario_name": scenario_name,
        "timestamp": datetime.now().isoformat(),
        "test_case": test_case_data,
        "agent_outputs": {},
        "validations": {},
        "errors": []
    }
    
    validator = AgentOutputValidator()
    
    try:
        # ====================================================================
        # AGENT 1: Problem Formulation
        # ====================================================================
        print("🔬 Stage 1/5: Problem Formulation...")
        
        problem_agent = create_problem_formulation_agent(model=model)
        async with InMemoryRunner(agent=problem_agent, app_name=f"eval-{scenario_name}-problem") as problem_runner:
            problem_session = await problem_runner.session_service.create_session(
                app_name=f"eval-{scenario_name}-problem",
                user_id="eval_user"
            )
            
            problem_prompt = format_prompt_for_user_profile(user_profile)
            problem_content = types.Content(parts=[types.Part(text=problem_prompt)])
            
            problem_response = ""
            
            # --- FIXED LOOP START ---
            async for event in problem_runner.run_async(
                user_id=problem_session.user_id,
                session_id=problem_session.id,
                new_message=problem_content
            ):
                # We iterate through every event.
                # If the event has text, we capture it. 
                # We verify part.text is not None and not empty.
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text and part.text.strip():
                            problem_response = part.text
            # --- FIXED LOOP END ---
        
        # If we didn't get a final response with text, log what we got
        if not problem_response:
            print(f"  ⚠️  Warning: No text response received from agent")
            raise ValueError("Agent did not return a text response")
        
        problem_response = _clean_json_response(problem_response)

        try:
            problem_def = json.loads(problem_response)
        except json.JSONDecodeError as e:
            print(f"  ❌ JSON Parse Error: {e}")
            print(f"  📄 Raw response (first 500 chars):")
            print(f"  {problem_response[:500]}")
            print(f"  💡 Tip: The LLM generated malformed JSON. Try running again or use a more reliable model.")
            raise
        
        results["agent_outputs"]["problem_formulation"] = problem_def
        results["validations"]["problem_formulation"] = validator.validate_problem_definition(problem_def)
        
        print(f"  ✓ Problem: {problem_def['problem_statement'][:80]}...")
        print(f"  ✓ Literature: {len(problem_def.get('preliminary_literature', []))} entries")
        
        # ====================================================================
        # AGENT 2: Objectives
        # ====================================================================
        print("\n🎯 Stage 2/5: Objectives...")
        
        from aida.data_models import ProblemDefinition
        problem_obj = ProblemDefinition(**problem_def)
        
        objectives_agent = create_objectives_agent(model=model)
        async with InMemoryRunner(agent=objectives_agent, app_name=f"eval-{scenario_name}-objectives") as objectives_runner:
            objectives_session = await objectives_runner.session_service.create_session(
                app_name=f"eval-{scenario_name}-objectives",
                user_id="eval_user"
            )
            
            objectives_prompt = format_prompt_for_objectives(user_profile, problem_obj)
            objectives_content = types.Content(parts=[types.Part(text=objectives_prompt)])
            
            objectives_response = ""
            async for event in objectives_runner.run_async(
                user_id=objectives_session.user_id,
                session_id=objectives_session.id,
                new_message=objectives_content
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            objectives_response = part.text
        
        objectives_response = _clean_json_response(objectives_response)
        objectives_output = json.loads(objectives_response)
        results["agent_outputs"]["objectives"] = objectives_output
        results["validations"]["objectives"] = validator.validate_objectives(objectives_output)
        
        print(f"  ✓ Specific objectives: {len(objectives_output.get('specific_objectives', []))}")
        
        # ====================================================================
        # AGENT 3: Methodology
        # ====================================================================
        print("\n📊 Stage 3/5: Methodology...")
        
        from aida.data_models import ResearchObjectives
        objectives_obj = ResearchObjectives(**objectives_output)
        
        methodology_agent = create_methodology_agent(model=model)
        async with InMemoryRunner(agent=methodology_agent, app_name=f"eval-{scenario_name}-methodology") as methodology_runner:
            methodology_session = await methodology_runner.session_service.create_session(
                app_name=f"eval-{scenario_name}-methodology",
                user_id="eval_user"
            )
            
            methodology_prompt = format_prompt_for_methodology(user_profile, problem_obj, objectives_obj)
            methodology_content = types.Content(parts=[types.Part(text=methodology_prompt)])
            
            methodology_response = ""
            async for event in methodology_runner.run_async(
                user_id=methodology_session.user_id,
                session_id=methodology_session.id,
                new_message=methodology_content
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            methodology_response = part.text
        
        methodology_response = _clean_json_response(methodology_response)
        methodology_output = json.loads(methodology_response)
        results["agent_outputs"]["methodology"] = methodology_output
        results["validations"]["methodology"] = validator.validate_methodology(methodology_output)
        
        print(f"  ✓ Type: {methodology_output.get('methodology_type', 'N/A')}")
        
        # ====================================================================
        # AGENT 4: Data Collection
        # ====================================================================
        print("\n📁 Stage 4/5: Data Collection...")
        
        from aida.data_models import MethodologyRecommendation
        methodology_obj = MethodologyRecommendation(**methodology_output)
        
        data_agent = create_data_collection_agent(model=model)
        async with InMemoryRunner(agent=data_agent, app_name=f"eval-{scenario_name}-data") as data_runner:
            data_session = await data_runner.session_service.create_session(
                app_name=f"eval-{scenario_name}-data",
                user_id="eval_user"
            )
            
            data_prompt = format_prompt_for_data_collection(user_profile, objectives_obj, methodology_obj)
            data_content = types.Content(parts=[types.Part(text=data_prompt)])
            
            data_response = ""
            async for event in data_runner.run_async(
                user_id=data_session.user_id,
                session_id=data_session.id,
                new_message=data_content
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            data_response = part.text
        
        data_response = _clean_json_response(data_response)
        data_output = json.loads(data_response)
        results["agent_outputs"]["data_collection"] = data_output
        results["validations"]["data_collection"] = validator.validate_data_collection(data_output)
        
        print(f"  ✓ Sample size: {data_output.get('estimated_sample_size', 'N/A')}")
        
        # ====================================================================
        # AGENT 5: Quality Control
        # ====================================================================
        print("\n✅ Stage 5/5: Quality Control...")
        
        from aida.data_models import DataCollectionPlan
        data_obj = DataCollectionPlan(**data_output)
        
        quality_agent = create_quality_control_agent(model=model)
        async with InMemoryRunner(agent=quality_agent, app_name=f"eval-{scenario_name}-quality") as quality_runner:
            quality_session = await quality_runner.session_service.create_session(
                app_name=f"eval-{scenario_name}-quality",
                user_id="eval_user"
            )
            
            quality_prompt = format_prompt_for_quality_control(
                user_profile, problem_obj, objectives_obj, methodology_obj, data_obj
            )
            quality_content = types.Content(parts=[types.Part(text=quality_prompt)])
            
            quality_response = ""
            async for event in quality_runner.run_async(
                user_id=quality_session.user_id,
                session_id=quality_session.id,
                new_message=quality_content
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            quality_response = part.text
        
        quality_response = _clean_json_response(quality_response)
        quality_output = json.loads(quality_response)
        results["agent_outputs"]["quality_control"] = quality_output
        results["validations"]["quality_control"] = validator.validate_quality_control(quality_output)
        
        print(f"  ✓ Quality score: {quality_output.get('overall_quality_score', 'N/A')}/100")
        print(f"  ✓ Passed: {quality_output.get('validation_passed', 'N/A')}")
        
    except Exception as e:
        results["errors"].append({
            "type": type(e).__name__,
            "message": str(e),
            "stage": "pipeline_execution"
        })
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    return results


# ============================================================================
# REPORT GENERATION
# ============================================================================

def generate_report(result: Dict[str, Any]) -> str:
    """Generate a report for a single test case."""
    lines = []
    lines.append("="*80)
    lines.append(f"EVALUATION REPORT: {result['scenario_name']}")
    lines.append("="*80)
    lines.append(f"Timestamp: {result['timestamp']}\n")
    
    # Summary
    total_validations = len(result["validations"])
    passed_validations = sum(1 for v in result["validations"].values() if v["valid"])
    
    lines.append("SUMMARY:")
    lines.append(f"  Validations: {passed_validations}/{total_validations} passed")
    lines.append(f"  Errors: {len(result['errors'])}\n")
    
    # Agent-by-agent results
    for agent_name, validation in result["validations"].items():
        lines.append(f"{agent_name.upper().replace('_', ' ')}:")
        if validation["valid"]:
            lines.append("  ✅ PASSED")
        else:
            lines.append("  ❌ FAILED")
            for issue in validation["issues"]:
                lines.append(f"    - {issue}")
        
        if validation["warnings"]:
            lines.append("  ⚠️  Warnings:")
            for warning in validation["warnings"]:
                lines.append(f"    - {warning}")
        lines.append("")
    
    # Errors
    if result["errors"]:
        lines.append("ERRORS:")
        for error in result["errors"]:
            lines.append(f"  - {error['type']}: {error['message']}")
    
    return "\n".join(lines)


# ============================================================================
# MAIN EXECUTION
# ============================================================================

async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Evaluate a single test case for the multi-agent system"
    )
    parser.add_argument(
        "scenario_id",
        nargs="?",
        help="Test scenario ID (e.g., scenario_1_ml_research)"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available test scenarios"
    )
    parser.add_argument(
        "--model",
        default="gemini-2.0-flash-lite",
        help="Gemini model to use (default: gemini-2.0-flash-lite)"
    )
    
    args = parser.parse_args()
    
    # List scenarios
    if args.list:
        print("\nAvailable Test Scenarios:")
        print("="*80)
        for scenario_id in list_available_tests():
            test_data = load_test_case(scenario_id)
            print(f"  • {scenario_id}")
            print(f"    Name: {test_data['name']}")
            print(f"    Description: {test_data['description']}")
            print()
        return
    
    # Validate scenario ID
    if not args.scenario_id:
        print("Error: Please specify a scenario ID or use --list to see available scenarios")
        print("\nUsage:")
        print("  python eval/test_multi_agent_pipeline.py scenario_1_ml_research")
        print("  python eval/test_multi_agent_pipeline.py --list")
        sys.exit(1)
    
    # Load and run test case
    try:
        test_data = load_test_case(args.scenario_id)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print(f"\nAvailable scenarios: {', '.join(list_available_tests())}")
        sys.exit(1)
    
    print("\n" + "="*80)
    print("MULTI-AGENT PIPELINE EVALUATION")
    print("="*80)
    
    result = await run_full_pipeline(test_data, model=args.model)

    # Define and create output directory
    output_dir = Path("eval/output")
    output_dir.mkdir(exist_ok=True)
    
    # Save result
    output_file = output_dir / f"results_{args.scenario_id}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)
    print(f"\n📄 Full results saved to: {output_file}")
    
    # Generate and display report
    report = generate_report(result)
    report_file = output_dir / f"report_{args.scenario_id}.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("\n" + "="*80)
    print(report)
    print("="*80)
    print(f"\n📊 Report saved to: {report_file}")
    
    # Final status
    if result["errors"]:
        print("\n❌ Evaluation completed with errors")
        sys.exit(1)
    else:
        passed = sum(1 for v in result["validations"].values() if v["valid"])
        total = len(result["validations"])
        if passed == total:
            print("\n✅ All validations passed!")
        else:
            print(f"\n⚠️  Evaluation completed: {passed}/{total} validations passed")


if __name__ == "__main__":
    asyncio.run(main())
