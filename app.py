"""
Streamlit UI for Academic Research Proposal Multi-Agent System

This app provides a user-friendly interface for:
1. Interactive interview to gather user profile
2. Autonomous multi-agent workflow execution
3. Display and download of research proposal
"""

import asyncio
import json
import sys
import time
import platform
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

import streamlit as st
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter, A4

# Fix for Windows Event Loop Policy
if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, ListFlowable, ListItem
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from io import BytesIO

# Setup environment
load_dotenv()
sys.path.insert(0, ".")

# Import system components
from aida.sub_agents.interviewer.agent import InterviewerAgent
from aida.data_models import InterviewState, UserProfile, Timeline
from aida.config import DEFAULT_MODEL
from aida.sub_agents.problem_formulation import create_problem_formulation_agent
from aida.sub_agents.objectives import create_objectives_agent
from aida.sub_agents.methodology import create_methodology_agent
from aida.sub_agents.data_collection import create_data_collection_agent
from aida.sub_agents.quality_control import create_quality_control_agent
from aida.orchestrator import ResearchProposalOrchestrator
from aida.pdf_generator import generate_pdf_proposal
from google.adk.runners import InMemoryRunner


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Academic Research Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for professional appearance
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .question-box {
        background-color: #f0f2f6;
        color: #1f77b4;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin-bottom: 1rem;
    }
    .progress-text {
        font-size: 0.9rem;
        color: #666;
        margin-bottom: 0.5rem;
    }
    .success-box {
        background-color: #d4edda;
        color:#006100;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        color: #800404;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-weight: 600;
    }
    .stButton>button:hover {
        background-color: #155a8a;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def initialize_session_state():
    """Initialize session state variables"""
    if 'phase' not in st.session_state:
        st.session_state.phase = 'welcome'  # welcome, interview, workflow, results
    
    if 'interview_state' not in st.session_state:
        st.session_state.interview_state = InterviewState(
            current_question_index=0,
            profile_data={},
            is_complete=False
        )
    
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = None
    
    if 'proposal' not in st.session_state:
        st.session_state.proposal = None
    
    if 'workflow_progress' not in st.session_state:
        st.session_state.workflow_progress = {
            'current_stage': '',
            'percentage': 0
        }
    
    if 'error_message' not in st.session_state:
        st.session_state.error_message = None


@st.cache_resource
def get_interviewer():
    """Get cached interviewer agent"""
    return InterviewerAgent(model=DEFAULT_MODEL)


def generate_markdown_proposal(proposal: Dict[str, Any]) -> str:
    """Generate Markdown format from proposal data"""
    md_lines = []
    
    # Header
    md_lines.append("# Academic Research Proposal")
    md_lines.append(f"\n*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
    md_lines.append("---\n")
    
    # Problem Definition
    if proposal.get('problem_definition'):
        pd = proposal['problem_definition']
        md_lines.append("## Problem Definition\n")
        md_lines.append(f"**Problem Statement:**\n{pd.get('problem_statement', 'N/A')}\n")
        md_lines.append(f"\n**Main Research Question:**\n{pd.get('main_research_question', 'N/A')}\n")
        
        if pd.get('secondary_questions'):
            md_lines.append("\n**Secondary Questions:**")
            for i, q in enumerate(pd['secondary_questions'], 1):
                md_lines.append(f"{i}. {q}")
            md_lines.append("")
        
        if pd.get('key_variables'):
            md_lines.append("\n**Key Variables:**")
            for var in pd['key_variables']:
                md_lines.append(f"- {var}")
            md_lines.append("")
        
        if pd.get('preliminary_literature'):
            md_lines.append("\n**Preliminary Literature:**")
            for lit in pd['preliminary_literature']:
                title = lit.get('title', 'Unknown')
                url = lit.get('url', '#')
                md_lines.append(f"- [{title}]({url})")
            md_lines.append("")
    
    # Research Objectives
    if proposal.get('research_objectives'):
        ro = proposal['research_objectives']
        md_lines.append("\n---\n## Research Objectives\n")
        md_lines.append(f"**General Objective:**\n{ro.get('general_objective', 'N/A')}\n")
        
        if ro.get('specific_objectives'):
            md_lines.append("\n**Specific Objectives:**")
            for i, obj in enumerate(ro['specific_objectives'], 1):
                md_lines.append(f"{i}. {obj}")
            md_lines.append("")
    
    # Methodology
    if proposal.get('methodology'):
        meth = proposal['methodology']
        md_lines.append("\n---\n## Methodology\n")
        md_lines.append(f"**Recommended Methodology:**\n{meth.get('recommended_methodology', 'N/A')}\n")
        md_lines.append(f"\n**Type:** {meth.get('methodology_type', 'N/A')}\n")
        md_lines.append(f"\n**Justification:**\n{meth.get('justification', 'N/A')}\n")
    
    # Data Collection
    if proposal.get('data_collection_plan'):
        dc = proposal['data_collection_plan']
        md_lines.append("\n---\n## Data Collection Plan\n")
        
        if dc.get('collection_techniques'):
            md_lines.append("\n**Collection Techniques:**")
            for tech in dc['collection_techniques']:
                md_lines.append(f"- {tech}")
            md_lines.append("")
        
        if dc.get('recommended_tools'):
            md_lines.append("\n**Recommended Tools:**")
            for tool in dc['recommended_tools']:
                name = tool.get('name', 'Unknown')
                purpose = tool.get('purpose', 'N/A')
                md_lines.append(f"- **{name}**: {purpose}")
            md_lines.append("")
    
    # Quality Validation
    if proposal.get('quality_validation'):
        qv = proposal['quality_validation']
        md_lines.append("\n---\n## Quality Validation\n")
        md_lines.append(f"**Overall Quality Score:** {qv.get('overall_quality_score', 'N/A')}/100\n")
        md_lines.append(f"**Coherence Score:** {qv.get('coherence_score', 'N/A')}\n")
        md_lines.append(f"**Feasibility Score:** {qv.get('feasibility_score', 'N/A')}\n")
        md_lines.append(f"**Validation Passed:** {qv.get('validation_passed', 'N/A')}\n")
        
        if qv.get('recommendations'):
            md_lines.append("\n**Recommendations:**")
            for rec in qv['recommendations']:
                md_lines.append(f"- {rec}")
            md_lines.append("")
    
    return "\n".join(md_lines)


def reset_app():
    """Reset the app to start a new proposal"""
    st.session_state.phase = 'welcome'
    st.session_state.interview_state = InterviewState(
        current_question_index=0,
        profile_data={},
        is_complete=False
    )
    st.session_state.user_profile = None
    st.session_state.proposal = None
    st.session_state.workflow_progress = {
        'current_stage': '',
        'percentage': 0
    }
    st.session_state.error_message = None
    st.rerun()


# ============================================================================
# PHASE HANDLERS
# ============================================================================

def show_welcome():
    """Display welcome screen"""
    st.markdown('<div class="main-header">🎓 Academic Research Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">AI-Powered Research Proposal Generation</div>', unsafe_allow_html=True)
    
    st.markdown("""
    ### Welcome!
    
    This tool will help you create a comprehensive research proposal through:
    
    1. **Quick Profile Form** - Fill out a single form with your specific details and current condition
    2. **AI Analysis** - The multi-agent system will:
       - Conduct a preliminar literature review
       - Formulate research problem
       - Define objectives
       - Recommend methodology
       - Plan data collection
       - Validate quality
    3. **Get Your Proposal** - Download in JSON or Markdown format
    
    **Estimated Time:** 5-10 minutes
    
    ---
    """)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Start Interview", use_container_width=True):
            st.session_state.phase = 'interview'
            st.rerun()


def show_interview():
    """Display interview phase with all questions in a single form"""
    st.markdown('<div class="main-header">📋 Research Profile Interview</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Please fill out all fields to create your research profile</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Create form with all questions
    with st.form("interview_form"):
        st.markdown("### 📚 Academic Information")
        
        academic_program = st.selectbox(
            "What is your current academic program?",
            options=["Bachelor's", "Master's", "PhD", "Postdoc"],
            help="Select your current academic level"
        )
        
        field_of_study = st.text_input(
            "What is your general field of study?",
            placeholder="e.g., Computer Science, Biology, Psychology",
            help="Enter your broad academic field"
        )
        
        research_area = st.text_input(
            "What is your specific research area of interest?",
            placeholder="e.g., Machine Learning, Genomics, Cognitive Behavioral Patterns",
            help="Be as specific as possible about your research focus"
        )
        
        st.markdown("---")
        st.markdown("### ⏱️ Time & Resources")
        
        col1, col2 = st.columns(2)
        with col1:
            weekly_hours = st.number_input(
                "How many hours per week can you dedicate to this research?",
                min_value=1,
                max_value=80,
                value=20,
                step=1,
                help="Typical range: 10-40 hours/week"
            )
        
        with col2:
            timeline_value = st.number_input(
                "What is your total timeline (in months)?",
                min_value=1,
                max_value=60,
                value=6,
                step=1,
                help="How many months do you have to complete this research?"
            )
        
        st.markdown("---")
        st.markdown("### 🛠️ Skills & Constraints")
        
        existing_skills = st.text_area(
            "What relevant skills do you currently possess?",
            placeholder="e.g., Python, Statistics, Qualitative Analysis, Data Visualization\n(Separate with commas or new lines)",
            help="List your current skills relevant to your research",
            height=100
        )
        
        missing_skills = st.text_area(
            "Are there any specific skills you are looking to develop or currently lack?",
            placeholder="e.g., Machine Learning, Advanced Statistics, Survey Design\n(Separate with commas or new lines)",
            help="List skills you need to acquire",
            height=100
        )
        
        constraints = st.text_area(
            "Do you have any specific constraints?",
            placeholder="e.g., No fieldwork, Limited software access, Remote only, Budget constraints\n(Separate with commas or new lines)",
            help="List any limitations or constraints on your research",
            height=100
        )
        
        additional_context = st.text_area(
            "Is there any other context or information you'd like to share? (Optional)",
            placeholder="Any additional details that might help us understand your research needs...",
            help="Optional: Provide any other relevant information",
            height=100
        )
        
        st.markdown("---")
        
        # Submit button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button("🚀 Generate Research Proposal", use_container_width=True)
        
        if submitted:
            # Validate required fields
            if not field_of_study.strip():
                st.error("❌ Please enter your field of study")
            elif not research_area.strip():
                st.error("❌ Please enter your research area")
            else:
                # Parse skills and constraints (split by commas or newlines)
                def parse_list_input(text):
                    if not text.strip():
                        return []
                    # Split by comma or newline, strip whitespace, filter empty
                    items = [item.strip() for item in text.replace('\n', ',').split(',')]
                    return [item for item in items if item]
                
                # Create UserProfile
                st.session_state.user_profile = UserProfile(
                    academic_program=academic_program,
                    field_of_study=field_of_study.strip(),
                    research_area=research_area.strip(),
                    weekly_hours=int(weekly_hours),
                    total_timeline=Timeline(value=int(timeline_value), unit="months"),
                    existing_skills=parse_list_input(existing_skills),
                    missing_skills=parse_list_input(missing_skills),
                    constraints=parse_list_input(constraints),
                    additional_context=additional_context.strip() if additional_context.strip() else None
                )
                
                st.session_state.phase = 'workflow'
                st.rerun()



def show_workflow():
    """Display workflow execution phase"""
    st.markdown('<div class="main-header">⚙️ Generating Research Proposal</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Our AI agents are working on your proposal...</div>', unsafe_allow_html=True)
    
    # Progress container
    progress_container = st.container()
    
    with progress_container:
        progress_bar = st.progress(0)
        status_text = st.empty()
        refinement_info = st.empty()  # Placeholder for refinement messages
        
        # Define progress callback
        def progress_callback(step: str, pct: int):
            progress_bar.progress(pct / 100)
            status_text.markdown(f"**{step}** ({pct}%)")
            
            # Show refinement info box when in refinement loop
            if "🔄 Refinement Loop" in step:
                refinement_info.info(
                    "ℹ️ **Quality Check:** The proposal didn't meet quality standards on the first attempt. "
                    "The system is automatically refining it to improve coherence and feasibility. "
                    "This is normal and ensures you get the best possible proposal!"
                )
            else:
                refinement_info.empty()  # Clear the message when not refining
            
            # Force UI update
            time.sleep(0.05)
        
        # Execute workflow
        try:
            # Define async wrapper to ensure agents are created INSIDE the loop
            # This prevents "Event Loop is closed" errors during cleanup
            async def _run_workflow_async():
                # Initialize agents INSIDE the loop
                backend_agents = {
                    'problem_formulation': create_problem_formulation_agent(model=DEFAULT_MODEL),
                    'objectives': create_objectives_agent(model=DEFAULT_MODEL),
                    'methodology': create_methodology_agent(model=DEFAULT_MODEL),
                    'data_collection': create_data_collection_agent(model=DEFAULT_MODEL),
                    'quality_control': create_quality_control_agent(model=DEFAULT_MODEL)
                }
                
                # Initialize orchestrator
                orchestrator = ResearchProposalOrchestrator(progress_callback=progress_callback)
                
                # Run workflow
                return await orchestrator.run_workflow(
                    agents=backend_agents,
                    runner=None,
                    initial_profile=st.session_state.user_profile
                )

            # Run the async wrapper
            result = asyncio.run(_run_workflow_async())
            
            if result["success"]:
                st.session_state.proposal = result["proposal"]
                st.session_state.phase = 'results'
                st.rerun()
            else:
                st.session_state.error_message = result.get("error", "Unknown error occurred")
                st.session_state.phase = 'error'
                st.rerun()
                
        except Exception as e:
            st.session_state.error_message = str(e)
            st.session_state.phase = 'error'
            st.rerun()


def show_results():
    """Display results phase"""
    st.markdown('<div class="main-header">✅ Research Proposal Complete!</div>', unsafe_allow_html=True)
    
    proposal = st.session_state.proposal
    
    # Success message
    st.markdown('<div class="success-box">Your research proposal has been successfully generated!</div>', unsafe_allow_html=True)
    
    # Download buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        json_str = json.dumps(proposal, indent=2)
        st.download_button(
            label="📥 Download JSON",
            data=json_str,
            file_name=f"research_proposal_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col2:
        md_str = generate_markdown_proposal(proposal)
        st.download_button(
            label="📥 Download Markdown",
            data=md_str,
            file_name=f"research_proposal_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown",
            use_container_width=True
        )
    
    with col3:
        # Generate comprehensive PDF
        try:
            pdf_buffer = generate_pdf_proposal(proposal)
            st.download_button(
                label="📄 Download Full PDF",
                data=pdf_buffer,
                file_name=f"research_proposal_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf",
                use_container_width=True,
                help="Comprehensive PDF with all proposal details"
            )
        except Exception as e:
            st.error(f"PDF generation failed: {str(e)}")

    
    st.markdown("---")
    
    # Display proposal sections
    if proposal.get('problem_definition'):
        with st.expander("📄 Problem Definition", expanded=True):
            pd = proposal['problem_definition']
            st.markdown(f"**Problem Statement:**\n\n{pd.get('problem_statement', 'N/A')}")
            st.markdown(f"\n**Main Research Question:**\n\n{pd.get('main_research_question', 'N/A')}")
            
            if pd.get('secondary_questions'):
                st.markdown("\n**Secondary Questions:**")
                for i, q in enumerate(pd['secondary_questions'], 1):
                    st.markdown(f"{i}. {q}")
    
    if proposal.get('problem_definition', {}).get('preliminary_literature'):
        with st.expander("📚 Preliminary Literature", expanded=False):
            lit_list = proposal['problem_definition']['preliminary_literature']
            st.markdown(f"Found **{len(lit_list)}** relevant papers:")
            for i, lit in enumerate(lit_list, 1):
                title = lit.get('title', 'Unknown')
                url = lit.get('url', '#')
                st.markdown(f"{i}. [{title}]({url})")
    
    if proposal.get('research_objectives'):
        with st.expander("🎯 Research Objectives", expanded=False):
            ro = proposal['research_objectives']
            st.markdown(f"**General Objective:**\n\n{ro.get('general_objective', 'N/A')}")
            
            if ro.get('specific_objectives'):
                st.markdown("\n**Specific Objectives:**")
                for i, obj in enumerate(ro['specific_objectives'], 1):
                    st.markdown(f"{i}. {obj}")
    
    if proposal.get('methodology'):
        with st.expander("📊 Methodology", expanded=False):
            meth = proposal['methodology']
            st.markdown(f"**Recommended Methodology:** {meth.get('recommended_methodology', 'N/A')}")
            st.markdown(f"\n**Type:** {meth.get('methodology_type', 'N/A')}")
            st.markdown(f"\n**Justification:**\n\n{meth.get('justification', 'N/A')}")
    
    if proposal.get('data_collection_plan'):
        with st.expander("📁 Data Collection Plan", expanded=False):
            dc = proposal['data_collection_plan']
            
            if dc.get('collection_techniques'):
                st.markdown("**Collection Techniques:**")
                for tech in dc['collection_techniques']:
                    st.markdown(f"- {tech}")
            
            if dc.get('recommended_tools'):
                st.markdown("\n**Recommended Tools:**")
                for tool in dc['recommended_tools']:
                    st.markdown(f"- **{tool.get('name', 'Unknown')}**: {tool.get('purpose', 'N/A')}")
    
    if proposal.get('quality_validation'):
        with st.expander("✅ Quality Validation", expanded=False):
            qv = proposal['quality_validation']
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Overall Quality", f"{qv.get('overall_quality_score', 'N/A')}/100")
            with col2:
                st.metric("Coherence", f"{qv.get('coherence_score', 'N/A')}")
            with col3:
                st.metric("Feasibility", f"{qv.get('feasibility_score', 'N/A')}")
            
            st.markdown(f"\n**Validation Passed:** {qv.get('validation_passed', 'N/A')}")
            
            if qv.get('recommendations'):
                st.markdown("\n**Recommendations:**")
                for rec in qv['recommendations']:
                    st.markdown(f"- {rec}")
    
    # Start new proposal button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 Start New Proposal", use_container_width=True):
            reset_app()


def show_error():
    """Display error phase"""
    st.markdown('<div class="main-header">❌ Error Occurred</div>', unsafe_allow_html=True)
    
    st.markdown(f'<div class="error-box"><strong>Error:</strong> {st.session_state.error_message}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Start Over", use_container_width=True):
            reset_app()
    with col2:
        if st.button("← Back to Interview", use_container_width=True):
            st.session_state.phase = 'interview'
            st.session_state.error_message = None
            st.rerun()


# ============================================================================
# MAIN APP
# ============================================================================

def main():
    """Main application entry point"""
    initialize_session_state()
    
    # Route to appropriate phase
    if st.session_state.phase == 'welcome':
        show_welcome()
    elif st.session_state.phase == 'interview':
        show_interview()
    elif st.session_state.phase == 'workflow':
        show_workflow()
    elif st.session_state.phase == 'results':
        show_results()
    elif st.session_state.phase == 'error':
        show_error()


if __name__ == "__main__":
    main()
