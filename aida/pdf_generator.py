"""Comprehensive PDF generator for research proposals."""

from typing import Dict, Any, List
from datetime import datetime
from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, 
    Table, TableStyle, ListFlowable, ListItem
)
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY


def generate_pdf_proposal(proposal: Dict[str, Any]) -> BytesIO:
    """
    Generate a comprehensive PDF research proposal from JSON data.
    
    Args:
        proposal: Complete proposal dictionary with all fields
        
    Returns:
        BytesIO object containing the PDF
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    heading1_style = ParagraphStyle(
        'CustomHeading1',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=12,
        spaceBefore=12
    )
    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2ca02c'),
        spaceAfter=10,
        spaceBefore=10
    )
    heading3_style = ParagraphStyle(
        'CustomHeading3',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#555555'),
        spaceAfter=8,
        spaceBefore=8
    )
    body_style = styles['BodyText']
    body_style.alignment = TA_JUSTIFY
    
    # Title (compact - no full page)
    elements.append(Paragraph("Academic Research Proposal", title_style))
    elements.append(Paragraph(
        f"Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')}",
        styles['Normal']
    ))
    elements.append(Spacer(1, 0.5*inch))
    
    # Table of Contents (compact - no page break)
    elements.append(Paragraph("Table of Contents", heading1_style))
    toc_items = [
        "1. User Profile",
        "2. Problem Definition",
        "3. Research Objectives",
        "4. Methodology",
        "5. Data Collection Plan",
        "6. Quality Validation",
    ]
    for item in toc_items:
        elements.append(Paragraph(item, styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    elements.append(PageBreak())
    
    # 1. USER PROFILE
    if proposal.get('user_profile'):
        _add_user_profile(elements, proposal['user_profile'], heading1_style, heading2_style, body_style)
        elements.append(Spacer(1, 0.3*inch))
    
    # 2. PROBLEM FORMULATION
    problem = proposal.get('problem_formulation') or proposal.get('problem_definition')
    if problem:
        _add_problem_definition(elements, problem, heading1_style, heading2_style, heading3_style, body_style)
        elements.append(Spacer(1, 0.3*inch))
    
    # 3. RESEARCH OBJECTIVES
    objectives = proposal.get('objectives') or proposal.get('research_objectives')
    if objectives:
        _add_research_objectives(elements, objectives, heading1_style, heading2_style, heading3_style, body_style)
        elements.append(Spacer(1, 0.3*inch))
    
    # 4. METHODOLOGY
    methodology = proposal.get('methodology')
    if methodology:
        _add_methodology(elements, methodology, heading1_style, heading2_style, heading3_style, body_style)
        elements.append(Spacer(1, 0.3*inch))
    
    # 5. DATA COLLECTION PLAN
    data_collection = proposal.get('data_collection') or proposal.get('data_collection_plan')
    if data_collection:
        _add_data_collection(elements, data_collection, heading1_style, heading2_style, heading3_style, body_style)
        elements.append(Spacer(1, 0.3*inch))
    
    # 6. QUALITY VALIDATION
    quality = proposal.get('quality_control') or proposal.get('quality_validation')
    if quality:
        _add_quality_validation(elements, quality, heading1_style, heading2_style, heading3_style, body_style)
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer


def _add_user_profile(elements, profile, h1, h2, body):
    """Add user profile section"""
    elements.append(Paragraph("1. User Profile", h1))
    elements.append(Spacer(1, 0.2*inch))
    
    elements.append(Paragraph(f"<b>Academic Program:</b> {profile.get('academic_program', 'N/A')}", body))
    elements.append(Paragraph(f"<b>Field of Study:</b> {profile.get('field_of_study', 'N/A')}", body))
    elements.append(Paragraph(f"<b>Research Area:</b> {profile.get('research_area', 'N/A')}", body))
    
    timeline = profile.get('total_timeline', {})
    if isinstance(timeline, dict):
        timeline_str = f"{timeline.get('value', 'N/A')} {timeline.get('unit', 'months')}"
    else:
        timeline_str = str(timeline)
    elements.append(Paragraph(f"<b>Timeline:</b> {timeline_str}", body))
    elements.append(Paragraph(f"<b>Weekly Hours:</b> {profile.get('weekly_hours', 'N/A')} hours/week", body))
    
    elements.append(Spacer(1, 0.15*inch))
    elements.append(Paragraph("<b>Existing Skills:</b>", body))
    for skill in profile.get('existing_skills', []):
        elements.append(Paragraph(f"• {skill}", body))
    
    elements.append(Spacer(1, 0.15*inch))
    elements.append(Paragraph("<b>Skills to Develop:</b>", body))
    for skill in profile.get('missing_skills', []):
        elements.append(Paragraph(f"• {skill}", body))
    
    elements.append(Spacer(1, 0.15*inch))
    elements.append(Paragraph("<b>Constraints:</b>", body))
    for constraint in profile.get('constraints', []):
        elements.append(Paragraph(f"• {constraint}", body))
    
    if profile.get('additional_context'):
        elements.append(Spacer(1, 0.15*inch))
        elements.append(Paragraph(f"<b>Additional Context:</b> {profile['additional_context']}", body))


def _add_problem_definition(elements, problem, h1, h2, h3, body):
    """Add problem definition section"""
    elements.append(Paragraph("2. Problem Definition", h1))
    elements.append(Spacer(1, 0.2*inch))
    
    elements.append(Paragraph("2.1 Problem Statement", h2))
    elements.append(Paragraph(problem.get('problem_statement', 'N/A'), body))
    elements.append(Spacer(1, 0.15*inch))
    
    elements.append(Paragraph("2.2 Main Research Question", h2))
    elements.append(Paragraph(problem.get('main_research_question', 'N/A'), body))
    elements.append(Spacer(1, 0.15*inch))
    
    elements.append(Paragraph("2.3 Secondary Research Questions", h2))
    for i, q in enumerate(problem.get('secondary_questions', []), 1):
        elements.append(Paragraph(f"{i}. {q}", body))
    elements.append(Spacer(1, 0.15*inch))
    
    elements.append(Paragraph("2.4 Key Variables", h2))
    for var in problem.get('key_variables', []):
        elements.append(Paragraph(f"• {var}", body))
    elements.append(Spacer(1, 0.15*inch))
    
    elements.append(Paragraph("2.5 Preliminary Literature Review", h2))
    for i, lit in enumerate(problem.get('preliminary_literature', []), 1):
        title = lit.get('title', 'Unknown')
        url = lit.get('url', '#')
        # Create clickable hyperlink for the title
        elements.append(Paragraph(f'<b>[{i}] <link href="{url}" color="blue">{title}</link></b>', body))
        elements.append(Paragraph(f"Source: {lit.get('source', 'N/A')}", body))
        elements.append(Paragraph(f"Relevance: {lit.get('relevance_note', 'N/A')}", body))
        elements.append(Spacer(1, 0.1*inch))


def _add_research_objectives(elements, objectives, h1, h2, h3, body):
    """Add research objectives section"""
    elements.append(Paragraph("3. Research Objectives", h1))
    elements.append(Spacer(1, 0.2*inch))
    
    elements.append(Paragraph("3.1 General Objective", h2))
    elements.append(Paragraph(objectives.get('general_objective', 'N/A'), body))
    elements.append(Spacer(1, 0.15*inch))
    
    elements.append(Paragraph("3.2 Specific Objectives", h2))
    for i, obj in enumerate(objectives.get('specific_objectives', []), 1):
        elements.append(Paragraph(f"{i}. {obj}", body))
    elements.append(Spacer(1, 0.15*inch))
    
    # Feasibility Notes
    feasibility = objectives.get('feasibility_notes', {})
    if feasibility:
        elements.append(Paragraph("3.3 Feasibility Assessment", h2))
        
        if feasibility.get('timeline_assessment'):
            elements.append(Paragraph("<b>Timeline Assessment:</b>", h3))
            elements.append(Paragraph(feasibility['timeline_assessment'], body))
            elements.append(Spacer(1, 0.1*inch))
        
        if feasibility.get('skills_required'):
            elements.append(Paragraph("<b>Skills Required:</b>", h3))
            for skill in feasibility['skills_required']:
                elements.append(Paragraph(f"• {skill}", body))
            elements.append(Spacer(1, 0.1*inch))
        
        if feasibility.get('constraint_compliance'):
            elements.append(Paragraph("<b>Constraint Compliance:</b>", h3))
            elements.append(Paragraph(feasibility['constraint_compliance'], body))
            elements.append(Spacer(1, 0.1*inch))
        
        if feasibility.get('risk_factors'):
            elements.append(Paragraph("<b>Risk Factors:</b>", h3))
            for risk in feasibility['risk_factors']:
                elements.append(Paragraph(f"• {risk}", body))
            elements.append(Spacer(1, 0.1*inch))
        
        if feasibility.get('mitigation_strategies'):
            elements.append(Paragraph("<b>Mitigation Strategies:</b>", h3))
            for strategy in feasibility['mitigation_strategies']:
                elements.append(Paragraph(f"• {strategy}", body))
    
    # Alignment Check
    alignment = objectives.get('alignment_check', {})
    if alignment:
        elements.append(Spacer(1, 0.15*inch))
        elements.append(Paragraph("3.4 Alignment Analysis", h2))
        
        if alignment.get('general_to_problem'):
            elements.append(Paragraph("<b>General Objective to Problem:</b>", h3))
            elements.append(Paragraph(alignment['general_to_problem'], body))
            elements.append(Spacer(1, 0.1*inch))
        
        if alignment.get('coverage_analysis'):
            elements.append(Paragraph("<b>Coverage Analysis:</b>", h3))
            elements.append(Paragraph(alignment['coverage_analysis'], body))
            elements.append(Spacer(1, 0.1*inch))
        
        if alignment.get('coherence_score'):
            elements.append(Paragraph(f"<b>Coherence Score:</b> {alignment['coherence_score']}", body))


def _add_methodology(elements, methodology, h1, h2, h3, body):
    """Add methodology section"""
    elements.append(Paragraph("4. Methodology", h1))
    elements.append(Spacer(1, 0.2*inch))
    
    elements.append(Paragraph("4.1 Recommended Methodology", h2))
    elements.append(Paragraph(f"<b>Approach:</b> {methodology.get('recommended_methodology', 'N/A')}", body))
    elements.append(Paragraph(f"<b>Type:</b> {methodology.get('methodology_type', 'N/A')}", body))
    elements.append(Spacer(1, 0.15*inch))
    
    elements.append(Paragraph("4.2 Justification", h2))
    elements.append(Paragraph(methodology.get('justification', 'N/A'), body))
    elements.append(Spacer(1, 0.15*inch))
    
    elements.append(Paragraph("4.3 Required Skills", h2))
    for skill in methodology.get('required_skills', []):
        elements.append(Paragraph(f"• {skill}", body))
    elements.append(Spacer(1, 0.15*inch))
    
    # Timeline Fit
    timeline_fit = methodology.get('timeline_fit', {})
    if timeline_fit:
        elements.append(Paragraph("4.4 Timeline Fit", h2))
        elements.append(Paragraph(f"<b>Feasible:</b> {timeline_fit.get('is_feasible', 'N/A')}", body))
        elements.append(Paragraph(f"<b>Estimated Duration:</b> {timeline_fit.get('estimated_duration', 'N/A')}", body))
        
        if timeline_fit.get('key_phases'):
            elements.append(Spacer(1, 0.1*inch))
            elements.append(Paragraph("<b>Key Phases:</b>", h3))
            for phase in timeline_fit['key_phases']:
                elements.append(Paragraph(
                    f"• {phase.get('phase', 'N/A')} - {phase.get('duration', 'N/A')}", 
                    body
                ))
    
    # Alternative Methodologies
    alternatives = methodology.get('alternative_methodologies', [])
    if alternatives:
        elements.append(Spacer(1, 0.15*inch))
        elements.append(Paragraph("4.5 Alternative Methodologies", h2))
        for i, alt in enumerate(alternatives, 1):
            elements.append(Paragraph(f"<b>Alternative {i}: {alt.get('name', 'N/A')}</b>", h3))
            elements.append(Paragraph(f"Type: {alt.get('type', 'N/A')}", body))
            elements.append(Paragraph(f"Description: {alt.get('description', 'N/A')}", body))
            
            if alt.get('pros'):
                elements.append(Paragraph("<b>Pros:</b>", body))
                for pro in alt['pros']:
                    elements.append(Paragraph(f"• {pro}", body))
            
            if alt.get('cons'):
                elements.append(Paragraph("<b>Cons:</b>", body))
                for con in alt['cons']:
                    elements.append(Paragraph(f"• {con}", body))
            
            elements.append(Spacer(1, 0.1*inch))


def _add_data_collection(elements, data_collection, h1, h2, h3, body):
    """Add data collection section"""
    elements.append(Paragraph("5. Data Collection Plan", h1))
    elements.append(Spacer(1, 0.2*inch))
    
    elements.append(Paragraph("5.1 Collection Techniques", h2))
    for technique in data_collection.get('collection_techniques', []):
        elements.append(Paragraph(f"• {technique}", body))
    elements.append(Spacer(1, 0.15*inch))
    
    elements.append(Paragraph("5.2 Recommended Tools", h2))
    for tool in data_collection.get('recommended_tools', []):
        elements.append(Paragraph(f"<b>{tool.get('name', 'Unknown')}</b>", h3))
        elements.append(Paragraph(f"Purpose: {tool.get('purpose', 'N/A')}", body))
        if tool.get('type'):
            elements.append(Paragraph(f"Type: {tool.get('type', 'N/A')}", body))
        if tool.get('accessibility'):
            elements.append(Paragraph(f"Accessibility: {tool.get('accessibility', 'N/A')}", body))
        if tool.get('learning_curve'):
            elements.append(Paragraph(f"Learning Curve: {tool.get('learning_curve', 'N/A')}", body))
        elements.append(Spacer(1, 0.1*inch))
    
    elements.append(Paragraph("5.3 Data Sources", h2))
    for source in data_collection.get('data_sources', []):
        elements.append(Paragraph(f"• {source}", body))
    elements.append(Spacer(1, 0.15*inch))
    
    elements.append(Paragraph("5.4 Sample Size", h2))
    elements.append(Paragraph(data_collection.get('estimated_sample_size', 'N/A'), body))
    elements.append(Spacer(1, 0.15*inch))
    
    # Timeline Breakdown
    timeline = data_collection.get('timeline_breakdown', {})
    if timeline:
        elements.append(Paragraph("5.5 Timeline Breakdown", h2))
        
        for phase_name in ['preparation', 'collection', 'quality_check']:
            phase = timeline.get(phase_name, {})
            if phase:
                elements.append(Paragraph(f"<b>{phase_name.title()}:</b> {phase.get('duration', 'N/A')}", h3))
                if phase.get('activities'):
                    for activity in phase['activities']:
                        elements.append(Paragraph(f"• {activity}", body))
                elements.append(Spacer(1, 0.1*inch))
        
        if timeline.get('total_duration'):
            elements.append(Paragraph(f"<b>Total Duration:</b> {timeline['total_duration']}", body))
    
    elements.append(Spacer(1, 0.15*inch))
    elements.append(Paragraph("5.6 Resource Requirements", h2))
    for resource in data_collection.get('resource_requirements', []):
        elements.append(Paragraph(f"• {resource}", body))


def _add_quality_validation(elements, quality, h1, h2, h3, body):
    """Add quality validation section"""
    elements.append(Paragraph("6. Quality Validation", h1))
    elements.append(Spacer(1, 0.2*inch))
    
    # Summary Metrics
    elements.append(Paragraph("6.1 Quality Metrics", h2))
    elements.append(Paragraph(f"<b>Validation Passed:</b> {'✓ Yes' if quality.get('validation_passed') else '✗ No'}", body))
    elements.append(Paragraph(f"<b>Overall Quality Score:</b> {quality.get('overall_quality_score', 'N/A')}/100", body))
    elements.append(Paragraph(f"<b>Coherence Score:</b> {quality.get('coherence_score', 'N/A')}", body))
    elements.append(Paragraph(f"<b>Feasibility Score:</b> {quality.get('feasibility_score', 'N/A')}", body))
    elements.append(Spacer(1, 0.15*inch))
    
    # Issues Identified
    issues = quality.get('issues_identified', [])
    if issues:
        elements.append(Paragraph("6.2 Issues Identified", h2))
        for issue in issues:
            severity = issue.get('severity', 'unknown').upper()
            component = issue.get('component', 'N/A')
            description = issue.get('description', 'N/A')
            impact = issue.get('impact', 'N/A')
            
            elements.append(Paragraph(f"<b>[{severity}] {component}</b>", h3))
            elements.append(Paragraph(f"Description: {description}", body))
            elements.append(Paragraph(f"Impact: {impact}", body))
            elements.append(Spacer(1, 0.1*inch))
    
    # Recommendations
    recommendations = quality.get('recommendations', [])
    if recommendations:
        elements.append(Paragraph("6.3 Recommendations", h2))
        for i, rec in enumerate(recommendations, 1):
            elements.append(Paragraph(f"{i}. {rec}", body))
    
    # Refinement Info
    if quality.get('requires_refinement'):
        elements.append(Spacer(1, 0.15*inch))
        elements.append(Paragraph("6.4 Refinement Required", h2))
        elements.append(Paragraph(f"<b>Requires Refinement:</b> Yes", body))
        if quality.get('refinement_targets'):
            elements.append(Paragraph("<b>Target Components:</b>", body))
            for target in quality['refinement_targets']:
                elements.append(Paragraph(f"• {target}", body))
