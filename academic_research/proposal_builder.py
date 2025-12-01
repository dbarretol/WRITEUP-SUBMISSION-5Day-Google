"""Proposal builder for assembling and formatting research proposals."""

import json
from typing import Dict, Any, List

class ProposalBuilder:
    """Assembles and formats research proposals."""
    
    @staticmethod
    def assemble_proposal(
        user_profile: Any,
        problem_definition: Any,
        research_objectives: Any,
        methodology: Any,
        data_collection: Any,
        quality_validation: Any = None
    ) -> Dict[str, Any]:
        """
        Assemble all proposal components into a single dictionary.
        
        Args:
            user_profile: UserProfile object.
            problem_definition: ProblemDefinition object.
            research_objectives: ResearchObjectives object.
            methodology: MethodologyRecommendation object.
            data_collection: DataCollectionPlan object.
            quality_validation: Optional QualityValidation object.
            
        Returns:
            Dictionary containing the complete proposal.
        """
        return {
            "user_profile": user_profile.model_dump() if user_profile else None,
            "problem_definition": problem_definition.model_dump() if problem_definition else None,
            "research_objectives": research_objectives.model_dump() if research_objectives else None,
            "methodology": methodology.model_dump() if methodology else None,
            "data_collection_plan": data_collection.model_dump() if data_collection else None,
            "quality_validation": quality_validation.model_dump() if quality_validation else None
        }
    
    @staticmethod
    def to_markdown(proposal: Dict[str, Any]) -> str:
        """
        Convert proposal dictionary to a formatted Markdown string.
        
        Args:
            proposal: The proposal dictionary.
            
        Returns:
            Formatted Markdown string.
        """
        md = []
        
        # Title
        md.append("# Research Proposal Draft\n")
        
        # 1. Introduction & Problem Statement
        prob = proposal.get("problem_definition", {})
        md.append("## 1. Introduction\n")
        if prob:
            md.append(f"**Problem Statement:**\n{prob.get('problem_statement', 'N/A')}\n")
            md.append(f"**Main Research Question:**\n{prob.get('main_research_question', 'N/A')}\n")
            
            secondary = prob.get("secondary_questions", [])
            if secondary:
                md.append("**Secondary Questions:**")
                for q in secondary:
                    md.append(f"- {q}")
                md.append("")
        
        # 2. Research Objectives
        objs = proposal.get("research_objectives", {})
        md.append("## 2. Research Objectives\n")
        if objs:
            md.append(f"**General Objective:**\n{objs.get('general_objective', 'N/A')}\n")
            
            specific = objs.get("specific_objectives", [])
            if specific:
                md.append("**Specific Objectives:**")
                for o in specific:
                    md.append(f"- {o}")
                md.append("")
        
        # 3. Methodology
        meth = proposal.get("methodology", {})
        md.append("## 3. Methodology\n")
        if meth:
            md.append(f"**Recommended Approach:** {meth.get('recommended_methodology', 'N/A')} ({meth.get('methodology_type', 'N/A')})\n")
            md.append(f"**Justification:**\n{meth.get('justification', 'N/A')}\n")
        
        # 4. Data Collection
        data = proposal.get("data_collection_plan", {})
        md.append("## 4. Data Collection Plan\n")
        if data:
            techniques = data.get("collection_techniques", [])
            if techniques:
                md.append("**Techniques:**")
                for t in techniques:
                    md.append(f"- {t}")
                md.append("")
            
            md.append(f"**Sample Size:** {data.get('estimated_sample_size', 'N/A')}\n")
            
            resources = data.get("resource_requirements", [])
            if resources:
                md.append("**Resource Requirements:**")
                for r in resources:
                    md.append(f"- {r}")
                md.append("")
        
        # 5. Quality Assurance
        qc = proposal.get("quality_validation", {})
        if qc:
            md.append("## 5. Quality Assessment\n")
            md.append(f"- **Coherence Score:** {qc.get('coherence_score', 'N/A')}")
            md.append(f"- **Feasibility Score:** {qc.get('feasibility_score', 'N/A')}")
            
            issues = qc.get("issues_identified", [])
            if issues:
                md.append("\n**Identified Issues:**")
                for i in issues:
                    md.append(f"- [{i.get('severity', 'UNKNOWN')}] {i.get('description', '')}")
        
        return "\n".join(md)

    @staticmethod
    def to_json(proposal: Dict[str, Any]) -> str:
        """Convert proposal to JSON string."""
        return json.dumps(proposal, indent=2, default=str)
