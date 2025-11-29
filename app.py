"""
CodeCrew - Multi-Agent Code Review System
Professional AI-powered code review with specialized agents
"""

import streamlit as st
from agents import SecurityAgent, PerformanceAgent, StyleAgent, MediatorAgent
from utils.parsers import count_lines, format_finding_html
import time

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="CodeCrew - AI Code Review",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Mobile viewport fix
st.markdown("""
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
""", unsafe_allow_html=True)

# ============================================================================
# CUSTOM CSS - PROFESSIONAL BRANDING (NO EMOJIS)
# ============================================================================

st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Fira+Code:wght@400;500&display=swap');
    
    /* Global Styles */
    .main {
        background-color: #ffffff;
    }
    
    /* Typography */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif;
        color: #1e293b;
    }
    
    p, div, span, label {
        font-family: 'Inter', sans-serif;
        color: #1e293b;
    }
    
    /* Sidebar text - light color for dark background */
    [data-testid="stSidebar"] {
        background-color: #1e293b;
    }
    
    [data-testid="stSidebar"] * {
        color: #f8fafc !important;
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4,
    [data-testid="stSidebar"] h5,
    [data-testid="stSidebar"] h6 {
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #e2e8f0 !important;
    }
    
    [data-testid="stSidebar"] hr {
        border-color: #475569 !important;
    }
    
    /* Code Text Areas */
    .stTextArea textarea {
        font-family: 'Fira Code', monospace !important;
        font-size: 14px !important;
        line-height: 1.6 !important;
        background-color: #f8fafc !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 8px !important;
        color: #1e293b !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1) !important;
    }
    
    /* Labels - Dark text on light background */
    .stTextArea label, .stSelectbox label, .stMultiSelect label {
        color: #1e293b !important;
        font-weight: 600 !important;
        font-size: 14px !important;
    }
    
    /* Primary Button */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        padding: 12px 32px !important;
        border: none !important;
        font-size: 16px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 6px rgba(99, 102, 241, 0.2) !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%) !important;
        box-shadow: 0 6px 12px rgba(99, 102, 241, 0.3) !important;
        transform: translateY(-2px) !important;
    }
    
    /* Select Boxes */
    .stSelectbox > div > div {
        background-color: #f8fafc !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 8px !important;
        color: #1e293b !important;
    }
    
    /* Sidebar Select Boxes - Light background with dark text */
    [data-testid="stSidebar"] .stSelectbox > div > div {
        background-color: #ffffff !important;
        border: 2px solid #94a3b8 !important;
        color: #1e293b !important;
    }
    
    [data-testid="stSidebar"] .stSelectbox label {
        color: #f8fafc !important;
    }
    
    /* Sidebar selectbox selected value - dark text */
    [data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #1e293b !important;
    }
    
    [data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] span {
        color: #1e293b !important;
    }
    
    /* Dropdown menu items */
    [data-testid="stSidebar"] [role="option"] {
        color: #1e293b !important;
        background-color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] [role="option"]:hover {
        background-color: #f1f5f9 !important;
        color: #1e293b !important;
    }
    
    /* Dropdown menu container */
    [data-testid="stSidebar"] [role="listbox"] {
        background-color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] [data-baseweb="popover"] {
        background-color: #ffffff !important;
    }
    
    /* Force dropdown menu content */
    [data-testid="stSidebar"] ul[role="listbox"] {
        background-color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] ul[role="listbox"] li {
        background-color: #ffffff !important;
        color: #1e293b !important;
    }
    
    [data-testid="stSidebar"] ul[role="listbox"] li:hover {
        background-color: #f1f5f9 !important;
        color: #1e293b !important;
    }
    
    /* Override any dark popover */
    [data-baseweb="popover"] {
        background-color: #ffffff !important;
    }
    
    [data-baseweb="popover"] [role="option"] {
        background-color: #ffffff !important;
        color: #1e293b !important;
    }
    
    /* Force all dropdown text to be dark */
    [data-testid="stSidebar"] .stSelectbox * {
        color: #1e293b !important;
    }
    
    /* But keep the label light */
    [data-testid="stSidebar"] .stSelectbox > label {
        color: #f8fafc !important;
    }
    
    /* Mobile Responsiveness */
    @media only screen and (max-width: 768px) {
        .codecrew-title {
            font-size: 32px !important;
        }
        
        .codecrew-subtitle {
            font-size: 14px !important;
        }
        
        .codecrew-header {
            padding: 1.5rem !important;
        }
        
        .stTextArea textarea {
            font-size: 12px !important;
        }
        
        [data-testid="stMetricValue"] {
            font-size: 24px !important;
        }
        
        .stButton > button {
            padding: 10px 20px !important;
            font-size: 14px !important;
        }
        
        /* Stack columns on mobile */
        [data-testid="column"] {
            width: 100% !important;
            flex: 100% !important;
        }
    }
    
    @media only screen and (max-width: 480px) {
        .codecrew-title {
            font-size: 24px !important;
        }
        
        .codecrew-subtitle {
            font-size: 12px !important;
        }
        
        h3 {
            font-size: 18px !important;
        }
        
        .stTextArea textarea {
            height: 250px !important;
        }
    }
    
    /* Multi-select */
    .stMultiSelect > div > div {
        background-color: #f8fafc !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 8px !important;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 32px !important;
        font-weight: 700 !important;
        color: #1e293b !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 14px !important;
        color: #64748b !important;
        font-weight: 500 !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #f8fafc !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        color: #1e293b !important;
        border: 1px solid #e2e8f0 !important;
    }
    
    .streamlit-expanderHeader:hover {
        background-color: #f1f5f9 !important;
    }
    
    /* Status Container */
    .element-container div[data-testid="stStatus"] {
        background-color: #f8fafc !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
    }
    
    /* Divider */
    hr {
        margin: 2rem 0 !important;
        border-color: #e2e8f0 !important;
    }
    
    /* Header Branding */
    .codecrew-header {
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
        padding: 2.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(99, 102, 241, 0.2);
    }
    
    .codecrew-title {
        color: white;
        font-size: 48px;
        font-weight: 700;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        letter-spacing: -0.5px;
    }
    
    .codecrew-subtitle {
        color: rgba(255, 255, 255, 0.95);
        font-size: 18px;
        margin: 8px 0 0 0;
        font-weight: 500;
    }
    
    /* Success State */
    .success-state {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 3rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(16, 185, 129, 0.2);
    }
    
    .success-state h2 {
        color: white !important;
        margin: 1rem 0 0.5rem 0;
    }
    
    /* Info messages */
    .stAlert {
        background-color: #f8fafc !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 8px !important;
        color: #1e293b !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# HEADER
# ============================================================================

st.markdown("""
<div class="codecrew-header">
    <h1 class="codecrew-title">CodeCrew</h1>
    <p class="codecrew-subtitle">Multi-Agent AI Code Review System • Powered by Specialized AI Agents</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# INITIALIZE AGENTS (CACHED)
# ============================================================================

@st.cache_resource
def initialize_agents():
    """Initialize all agents (cached for performance)"""
    return {
        'security': SecurityAgent(),
        'performance': PerformanceAgent(),
        'style': StyleAgent(),
        'mediator': MediatorAgent()
    }

agents = initialize_agents()

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.markdown("### About CodeCrew")
    st.markdown("""
    CodeCrew uses specialized AI agents to review your code:
    
    - **Security Agent**: Finds vulnerabilities
    - **Performance Agent**: Optimizes efficiency  
    - **Style Agent**: Ensures quality
    - **Mediator Agent**: Synthesizes feedback
    
    Powered by Hugging Face AI models (free and open-source).
    """)
    
    st.divider()
    
    st.markdown("### Supported Languages")
    st.markdown("""
    - Python
    - JavaScript
    - TypeScript
    - Java
    - Go
    - C++
    - Ruby
    - PHP
    """)
    
    st.divider()
    
    st.markdown("### How It Works")
    st.markdown("""
    1. Paste your code
    2. Select language
    3. Click "Start Review"
    4. Get instant analysis
    
    **Note**: First run may take 10-20 seconds while AI models load.
    """)

# ============================================================================
# MAIN INPUT SECTION
# ============================================================================

st.markdown("### Submit Code for Review")

col1, col2 = st.columns([3, 1])

with col1:
    code_input = st.text_area(
        "Paste your code here:",
        height=350,
        placeholder="""def process_user_input(user_id):
    # Example code with potential issues
    query = f"SELECT * FROM users WHERE id = {user_id}"
    result = db.execute(query)
    return result
        """,
        help="Paste the code you want reviewed"
    )

with col2:
    language = st.selectbox(
        "Programming Language:",
        ["Python", "JavaScript", "TypeScript", "Java", "Go", "C++", "Ruby", "PHP"],
        help="Select the programming language of your code"
    )
    
    st.markdown("---")
    
    if code_input:
        line_count = count_lines(code_input)
        st.metric("Lines of Code", line_count)
    
    st.markdown("---")
    
    severity_filter = st.multiselect(
        "Filter by Severity:",
        ["CRITICAL", "HIGH", "MEDIUM", "LOW"],
        default=["CRITICAL", "HIGH", "MEDIUM", "LOW"],
        help="Choose which severity levels to display"
    )

# ============================================================================
# REVIEW BUTTON & LOGIC
# ============================================================================

st.markdown("---")

if st.button("Start Code Review", type="primary", use_container_width=True):
    
    if not code_input.strip():
        st.error("Please paste some code to review!")
        
    else:
        # Progress tracking
        st.markdown("### Agent Activity")
        st.markdown("*Agents are analyzing your code...*")
        
        activity_placeholder = st.container()
        all_findings = {}
        
        with activity_placeholder:
            
            # SECURITY AGENT
            with st.status("Security Agent analyzing...", expanded=False) as security_status:
                start_time = time.time()
                security_findings = agents['security'].analyze(code_input, language)
                elapsed = time.time() - start_time
                all_findings['Security'] = security_findings
                
                security_status.update(
                    label=f"Security Agent - Complete ({len(security_findings)} issues found in {elapsed:.1f}s)",
                    state="complete"
                )
            
            # PERFORMANCE AGENT
            with st.status("Performance Agent analyzing...", expanded=False) as perf_status:
                start_time = time.time()
                perf_findings = agents['performance'].analyze(code_input, language)
                elapsed = time.time() - start_time
                all_findings['Performance'] = perf_findings
                
                perf_status.update(
                    label=f"Performance Agent - Complete ({len(perf_findings)} issues found in {elapsed:.1f}s)",
                    state="complete"
                )
            
            # STYLE AGENT
            with st.status("Style Agent analyzing...", expanded=False) as style_status:
                start_time = time.time()
                style_findings = agents['style'].analyze(code_input, language)
                elapsed = time.time() - start_time
                all_findings['Style'] = style_findings
                
                style_status.update(
                    label=f"Style Agent - Complete ({len(style_findings)} issues found in {elapsed:.1f}s)",
                    state="complete"
                )
            
            # MEDIATOR AGENT
            with st.status("Mediator Agent synthesizing results...", expanded=False) as mediator_status:
                start_time = time.time()
                final_report = agents['mediator'].synthesize(all_findings)
                elapsed = time.time() - start_time
                
                mediator_status.update(
                    label=f"Mediator Agent - Complete (synthesized in {elapsed:.1f}s)",
                    state="complete"
                )
        
        # RESULTS SECTION
        st.markdown("---")
        st.markdown("### Review Results")
        
        # Show success if no issues
        if final_report['total_issues'] == 0:
            st.markdown("""
            <div class="success-state">
                <h2>Excellent Work!</h2>
                <p style="margin: 8px 0 0 0; font-size: 18px; color: rgba(255,255,255,0.9);">
                    No issues found. Your code looks great!
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        else:
            # Metrics Row
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("Total Issues", final_report['total_issues'])
            
            with col2:
                critical = final_report['by_severity'].get('CRITICAL', 0)
                st.metric("Critical", critical, delta=None if critical == 0 else "Urgent", delta_color="inverse")
            
            with col3:
                high = final_report['by_severity'].get('HIGH', 0)
                st.metric("High", high, delta=None if high == 0 else "Important", delta_color="inverse")
            
            with col4:
                medium = final_report['by_severity'].get('MEDIUM', 0)
                st.metric("Medium", medium)
            
            with col5:
                low = final_report['by_severity'].get('LOW', 0)
                st.metric("Low", low)
            
            st.markdown("---")
            
            # FINAL RECOMMENDATIONS
            with st.expander("Final Recommendations", expanded=True):
                st.markdown(final_report['summary'])
                
                # Priority breakdown
                if final_report['priority_1']:
                    st.markdown("#### Priority 1: Immediate Action Required")
                    st.markdown(f"*{len(final_report['priority_1'])} critical/high severity issues*")
                
                if final_report['priority_2']:
                    st.markdown("#### Priority 2: Important Improvements")
                    st.markdown(f"*{len(final_report['priority_2'])} medium severity issues*")
                
                if final_report['priority_3']:
                    st.markdown("#### Priority 3: Nice to Have")
                    st.markdown(f"*{len(final_report['priority_3'])} low severity issues*")
            
            st.markdown("---")
            
            # INDIVIDUAL AGENT FINDINGS
            st.markdown("### Detailed Findings by Agent")
            
            agent_icons = {
                'Security': '🛡️',
                'Performance': '⚡',
                'Style': '✨'
            }
            
            for agent_name, findings in all_findings.items():
                
                # Filter by severity
                filtered_findings = [
                    f for f in findings 
                    if f.get('severity', 'LOW') in severity_filter
                ]
                
                icon = agent_icons.get(agent_name, '')
                
                if not filtered_findings and not findings:
                    # No findings at all
                    with st.expander(f"{agent_name} - No issues found", expanded=False):
                        st.success(f"The {agent_name} found no issues. Great job!")
                
                elif not filtered_findings:
                    # Has findings but filtered out
                    with st.expander(f"{agent_name} - {len(findings)} issues (filtered)", expanded=False):
                        st.info(f"All {len(findings)} issues are hidden by your severity filter.")
                
                else:
                    # Has findings to show
                    with st.expander(
                        f"{agent_name} - {len(filtered_findings)} issues found",
                        expanded=(agent_name == "Security" and len(filtered_findings) > 0)
                    ):
                        for finding in filtered_findings:
                            st.markdown(format_finding_html(finding), unsafe_allow_html=True)

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 14px; padding: 2rem 0;">
    <p style="margin: 0;">
        <strong>CodeCrew</strong> • Built with Streamlit & Hugging Face
    </p>
    <p style="margin: 4px 0 0 0;">
        Multi-agent AI code review system using specialized AI agents
    </p>
</div>
""", unsafe_allow_html=True)
