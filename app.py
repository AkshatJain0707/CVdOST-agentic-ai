# frontend.py
# -------------------------------------------------
# Investor-ready UI for ResuMate: AI Career Engine
# -------------------------------------------------
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
import io
import json
from datetime import datetime

st.set_page_config(
    page_title="CVdOST - AI Career Engine",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------- SESSION STATE INITIALIZATION --------------------
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = None

if "analysis_history" not in st.session_state:
    st.session_state.analysis_history = []

# -------------------- CUSTOM CSS --------------------
st.markdown("""
    <style>
    body {
        background: radial-gradient(circle at 25% 25%, #0f2027, #203a43, #2c5364);
        color: #FFFFFF;
    }
    .big-title {
        font-size: 2.6rem;
        font-weight: 800;
        text-align: center;
        color: #00FFC6;
        margin-top: 1rem;
    }
    .subtext {
        text-align: center;
        color: #cccccc;
        font-size: 1.1rem;
    }
    .stButton button {
        background: linear-gradient(90deg, #00c6ff, #0072ff);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.6rem 1.2rem;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton button:hover {
        transform: scale(1.05);
        background: linear-gradient(90deg, #0072ff, #00c6ff);
    }
    .metric-card {
        background: rgba(255,255,255,0.1);
        border-radius: 16px;
        padding: 1rem;
        text-align: center;
        margin: 0.5rem;
        box-shadow: 0px 0px 12px rgba(0,255,198,0.3);
    }
    .insight-box {
        background: rgba(0, 255, 198, 0.1);
        border-left: 4px solid #00FFC6;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    .warning-box {
        background: rgba(255, 193, 7, 0.1);
        border-left: 4px solid #FFC107;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------- HEADER --------------------
st.markdown("<h1 class='big-title'>CVdOST 🧠</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtext'>AI-Powered Resume Intelligence & Job Match Analytics</p>", unsafe_allow_html=True)
st.write("---")

# -------------------- SIDEBAR --------------------
st.sidebar.title("⚙️ Navigation")
section = st.sidebar.radio("Select Section", [
    "📊 Dashboard Overview",
    "📄 Resume Enhancer",
    "📈 Analytics & Insights",
    "📥 Download Report"
])

st.sidebar.info("Built by Akshat AI Labs | Transforming life with Intelligence ⚡")

# -------------------- API Base --------------------
API_URL = "http://localhost:8000/api/analyze"

# -------------------- DASHBOARD --------------------
if section == "📊 Dashboard Overview":
    st.header("📊 AI-Driven Career Intelligence Dashboard")
    uploaded_resume = st.file_uploader("Upload Resume (PDF/DOCX)", type=["pdf", "docx"])
    jd_text = st.text_area("Paste Job Description Here")

    if st.button("Analyze Resume"):
        if uploaded_resume and jd_text:
            with st.spinner("AI is analyzing your resume..."):
                files = {"resume_file": uploaded_resume}
                data = {"job_description": jd_text}
                try:
                    response = requests.post(API_URL, files=files, data=data, timeout=60)
                except requests.exceptions.ConnectionError as e:
                    st.error("❌ Backend server not running! Please start the backend first.")
                    st.code("uvicorn backend.main:app --reload", language="bash")
                    st.stop()

                if response.status_code == 200:
                    result = response.json()
                    st.success("✅ Analysis complete!")
                    
                    # Store result in session state and history
                    st.session_state.analysis_results = result
                    st.session_state.analysis_history.append({
                        "timestamp": datetime.now().isoformat(),
                        "data": result
                    })

                    # Extract scores safely
                    ats_final_score = result.get("ats", {}).get("ats", {}).get("final_score", 0)
                    semantic_match = result.get("matcher", {}).get("semantic", {}).get("overall_score", 0) * 100
                    skill_fit = result.get("matcher", {}).get("skill_comparator", {}).get("skill_fit_index", 0) * 100

                    # Key Metrics
                    col1, col2, col3 = st.columns(3)
                    col1.metric("ATS Score", f"{ats_final_score:.1f}%", "AI Precision")
                    col2.metric("Semantic Match", f"{semantic_match:.1f}%", "Content Relevance")
                    col3.metric("Skill Fit", f"{skill_fit:.1f}%", "Technical Alignment")

                    # Display components breakdown
                    st.subheader("📊 Scoring Breakdown")
                    components = result.get("ats", {}).get("ats", {}).get("components", {})
                    if components:
                        breakdown_df = pd.DataFrame({
                            "Component": list(components.keys()),
                            "Score": list(components.values())
                        })
                        fig = px.bar(breakdown_df, x="Component", y="Score", 
                                     title="ATS Score Components", template="plotly_dark",
                                     color="Score", color_continuous_scale="Viridis")
                        st.plotly_chart(fig, use_container_width=True)

                    # Display suggestions
                    st.subheader("💡 Improvement Suggestions")
                    suggestions = result.get("ats", {}).get("ats", {}).get("suggestions", [])
                    if suggestions:
                        for i, suggestion in enumerate(suggestions, 1):
                            st.markdown(f"✅ **{i}. {suggestion}**")
                    else:
                        st.info("✨ Great match! No major improvements needed.")
                    
                    st.info("💡 **Tip:** Navigate to '📈 Analytics & Insights' tab to see detailed analytics and advanced insights about this analysis!")
                else:
                    st.error(f"❌ Backend error ({response.status_code})")
                    st.info("Try these steps:")
                    st.code("1. Check if backend server is running: uvicorn backend.main:app --reload", language="bash")
                    st.code("2. Check logs in data/logs/ directory", language="bash")
                    st.json(response.json() if response.text else "No error details")
        else:
            st.warning("Please upload resume and paste a job description first.")

# -------------------- RESUME ENHANCER --------------------
elif section == "📄 Resume Enhancer":
    st.header("💡 AI Resume Optimizer")
    text_input = st.text_area("Paste your Resume Content Here")
    target_role = st.text_input("Target Role (e.g., Data Scientist, Project Manager)")

    if st.button("Enhance Resume"):
        if text_input:
            st.info("📝 Note: Use the Dashboard Overview tab to upload your resume and job description for optimization via AI analysis.")
            st.markdown("""
                The optimizer works best when you:
                1. Upload your actual resume file (PDF/DOCX)
                2. Paste the target job description
                3. Click "Analyze Resume" in the Dashboard
                
                The system will then provide optimization recommendations based on your specific match.
            """)
        else:
            st.warning("Paste your resume content first.")

# -------------------- ANALYTICS & INSIGHTS --------------------
elif section == "📈 Analytics & Insights":
    st.header("📈 Career & Skill Analytics")
    st.markdown("Gain deep insights into your career positioning using advanced AI-driven graphs and embeddings.")
    
    # Check if analysis has been performed
    if st.session_state.analysis_results is None:
        st.warning("⚠️ No analysis data available yet!")
        st.info("📊 **To see analytics:**\n1. Go to '📊 Dashboard Overview'\n2. Upload your resume and job description\n3. Click 'Analyze Resume'\n4. Return here to see your personalized analytics!")
    else:
        result = st.session_state.analysis_results
        
        # Extract key scores
        ats_final_score = result.get("ats", {}).get("ats", {}).get("final_score", 0)
        semantic_match = result.get("matcher", {}).get("semantic", {}).get("overall_score", 0) * 100
        skill_fit = result.get("matcher", {}).get("skill_comparator", {}).get("skill_fit_index", 0) * 100
        
        # Get components and suggestions
        components = result.get("ats", {}).get("ats", {}).get("components", {})
        suggestions = result.get("ats", {}).get("ats", {}).get("suggestions", [])
        
        # TAB 1: Score Overview
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Score Overview", "🎯 Skill Gap Analysis", "💡 Recommendations", "📈 Comparison"])
        
        with tab1:
            st.subheader("Overall Performance Metrics")
            
            # Create funnel chart from real data
            funnel_data = pd.DataFrame({
                "Category": ["ATS Score", "Semantic Match", "Skill Fit"],
                "Score": [ats_final_score, semantic_match, skill_fit]
            })
            fig_funnel = px.funnel(
                funnel_data, 
                x="Score", 
                y="Category",
                title="🎯 Performance Funnel: Resume Match Scores",
                template="plotly_dark"
            )
            fig_funnel.update_traces(marker=dict(color=funnel_data["Score"], 
                                                 colorscale="Viridis",
                                                 showscale=True))
            st.plotly_chart(fig_funnel, use_container_width=True)
            
            # Radar chart with actual data
            if components:
                component_names = list(components.keys())
                component_scores = list(components.values())
                
                # Add overall score to radar
                radar_values = component_scores + [ats_final_score]
                radar_labels = component_names + ["Overall"]
                
                fig_radar = go.Figure(data=go.Scatterpolar(
                    r=radar_values,
                    theta=radar_labels,
                    fill='toself',
                    name='Resume Fit'
                ))
                fig_radar.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                    showlegend=False,
                    title="📡 Resume Fitness Radar",
                    template="plotly_dark"
                )
                st.plotly_chart(fig_radar, use_container_width=True)
            
            # Components breakdown
            if components:
                st.subheader("Score Components Breakdown")
                col1, col2, col3 = st.columns(3)
                
                sorted_components = sorted(components.items(), key=lambda x: x[1], reverse=True)
                for idx, (name, score) in enumerate(sorted_components):
                    if idx % 3 == 0:
                        col = col1
                    elif idx % 3 == 1:
                        col = col2
                    else:
                        col = col3
                    
                    with col:
                        st.metric(name.replace("_", " ").title(), f"{score:.1f}%")
        
        with tab2:
            st.subheader("🎯 Skill Gap Analysis")
            
            # Extract skill comparison data
            skill_data = result.get("matcher", {}).get("skill_comparator", {})
            
            if skill_data:
                matched_skills = skill_data.get("matched_skills", [])
                missing_skills = skill_data.get("missing_skills", [])
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### ✅ Matched Skills")
                    if matched_skills:
                        st.success(f"**{len(matched_skills)} skills matched**")
                        for skill in matched_skills[:10]:  # Show top 10
                            st.write(f"  • {skill}")
                        if len(matched_skills) > 10:
                            st.write(f"  ... and {len(matched_skills) - 10} more")
                    else:
                        st.info("No matched skills found in data")
                
                with col2:
                    st.markdown("### ⚠️ Missing Skills (Gap)")
                    if missing_skills:
                        st.warning(f"**{len(missing_skills)} skills to develop**")
                        for skill in missing_skills[:10]:  # Show top 10
                            st.write(f"  • {skill}")
                        if len(missing_skills) > 10:
                            st.write(f"  ... and {len(missing_skills) - 10} more")
                    else:
                        st.success("Great! No major skill gaps detected")
                
                # Skill gap visualization
                if matched_skills and missing_skills:
                    skill_stats = pd.DataFrame({
                        "Category": ["Matched", "Gap"],
                        "Count": [len(matched_skills), len(missing_skills)]
                    })
                    fig_skills = px.pie(
                        skill_stats,
                        names="Category",
                        values="Count",
                        title="Skill Coverage Distribution",
                        template="plotly_dark",
                        color_discrete_map={"Matched": "#00d084", "Gap": "#ff6b6b"}
                    )
                    st.plotly_chart(fig_skills, use_container_width=True)
            else:
                st.info("Skill comparison data not available")
        
        with tab3:
            st.subheader("💡 AI-Generated Recommendations")
            
            if suggestions:
                st.success(f"**{len(suggestions)} recommendations to improve your match**")
                for i, suggestion in enumerate(suggestions, 1):
                    st.markdown(f"""
                    <div class='insight-box'>
                    <strong>#{i}</strong> {suggestion}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("✨ **Excellent match!** Your resume aligns well with the job description. No major improvements needed!")
            
            # Score interpretation
            st.divider()
            st.subheader("📋 Score Interpretation")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div class='insight-box'>
                <strong>ATS Score: {ats_final_score:.1f}%</strong><br>
                {'🟢 Strong' if ats_final_score >= 75 else '🟡 Moderate' if ats_final_score >= 50 else '🔴 Needs work'}<br>
                Your resume's technical alignment with job requirements.
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class='insight-box'>
                <strong>Semantic Match: {semantic_match:.1f}%</strong><br>
                {'🟢 Strong' if semantic_match >= 75 else '🟡 Moderate' if semantic_match >= 50 else '🔴 Needs work'}<br>
                Content relevance and meaning alignment.
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class='insight-box'>
                <strong>Skill Fit: {skill_fit:.1f}%</strong><br>
                {'🟢 Strong' if skill_fit >= 75 else '🟡 Moderate' if skill_fit >= 50 else '🔴 Needs work'}<br>
                How well your skills match requirements.
                </div>
                """, unsafe_allow_html=True)
        
        with tab4:
            st.subheader("📊 Analysis History & Comparison")
            
            if len(st.session_state.analysis_history) > 1:
                st.info(f"**{len(st.session_state.analysis_history)} analyses performed**")
                
                # Create comparison chart
                history_scores = []
                for entry in st.session_state.analysis_history:
                    data = entry["data"]
                    timestamp = entry["timestamp"][:16]  # Format timestamp
                    
                    ats = data.get("ats", {}).get("ats", {}).get("final_score", 0)
                    sem = data.get("matcher", {}).get("semantic", {}).get("overall_score", 0) * 100
                    skill = data.get("matcher", {}).get("skill_comparator", {}).get("skill_fit_index", 0) * 100
                    
                    history_scores.append({
                        "Timestamp": timestamp,
                        "ATS Score": ats,
                        "Semantic Match": sem,
                        "Skill Fit": skill
                    })
                
                history_df = pd.DataFrame(history_scores)
                
                # Line chart showing progression
                fig_history = px.line(
                    history_df.melt(id_vars=['Timestamp'], var_name='Metric', value_name='Score'),
                    x='Timestamp',
                    y='Score',
                    color='Metric',
                    title="Score Progression Over Time",
                    template="plotly_dark",
                    markers=True
                )
                st.plotly_chart(fig_history, use_container_width=True)
                
                # History table
                st.dataframe(history_df, use_container_width=True)
            else:
                st.info("👉 Perform multiple analyses to see comparison trends!")

# -------------------- REPORT DOWNLOAD --------------------
elif section == "📥 Download Report":
    st.header("📄 Export AI Report")
    st.markdown("Generate and download a comprehensive analysis report.")
    
    if st.session_state.analysis_results is None:
        st.warning("⚠️ No analysis data available yet!")
        st.info("📊 **To generate a report:**\n1. Go to '📊 Dashboard Overview'\n2. Upload your resume and job description\n3. Click 'Analyze Resume'\n4. Return here to download the report")
    else:
        result = st.session_state.analysis_results
        
        # Extract all data
        ats_final_score = result.get("ats", {}).get("ats", {}).get("final_score", 0)
        semantic_match = result.get("matcher", {}).get("semantic", {}).get("overall_score", 0) * 100
        skill_fit = result.get("matcher", {}).get("skill_comparator", {}).get("skill_fit_index", 0) * 100
        components = result.get("ats", {}).get("ats", {}).get("components", {})
        suggestions = result.get("ats", {}).get("ats", {}).get("suggestions", [])
        skill_data = result.get("matcher", {}).get("skill_comparator", {})
        
        # Generate report content
        report_content = f"""
================================================================================
                    CVdOST AI ANALYSIS REPORT
================================================================================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

================================================================================
                        EXECUTIVE SUMMARY
================================================================================

Overall ATS Score:        {ats_final_score:.1f}%
Semantic Match Score:     {semantic_match:.1f}%
Skill Fit Score:          {skill_fit:.1f}%

Overall Assessment: {'🟢 STRONG' if ats_final_score >= 75 else '🟡 MODERATE' if ats_final_score >= 50 else '🔴 NEEDS IMPROVEMENT'}

================================================================================
                    DETAILED SCORE BREAKDOWN
================================================================================

"""
        
        if components:
            for component, score in sorted(components.items(), key=lambda x: x[1], reverse=True):
                report_content += f"{component.replace('_', ' ').title():<40} {score:>6.1f}%\n"
        
        report_content += f"""
================================================================================
                        SKILL ANALYSIS
================================================================================

"""
        
        if skill_data:
            matched = skill_data.get("matched_skills", [])
            missing = skill_data.get("missing_skills", [])
            
            report_content += f"Matched Skills ({len(matched)}):\n"
            for skill in matched[:20]:
                report_content += f"  ✓ {skill}\n"
            if len(matched) > 20:
                report_content += f"  ... and {len(matched) - 20} more\n"
            
            report_content += f"\nSkill Gaps to Address ({len(missing)}):\n"
            for skill in missing[:20]:
                report_content += f"  ✗ {skill}\n"
            if len(missing) > 20:
                report_content += f"  ... and {len(missing) - 20} more\n"
        
        report_content += f"""
================================================================================
                    RECOMMENDATIONS
================================================================================

"""
        
        if suggestions:
            for i, suggestion in enumerate(suggestions, 1):
                report_content += f"{i}. {suggestion}\n\n"
        else:
            report_content += "No major improvements needed. Your resume is well-aligned with the job description.\n"
        
        report_content += f"""
================================================================================
                        SCORE GUIDANCE
================================================================================

ATS Score (Technical Alignment):
  80-100%:  Excellent match - Strong technical fit
  60-79%:   Good match - Minor improvements recommended
  40-59%:   Fair match - Significant improvements needed
  0-39%:    Poor match - Major rework required

Semantic Match (Content Relevance):
  80-100%:  Perfect alignment of meaning and context
  60-79%:   Good alignment with minor gaps
  40-59%:   Fair alignment, consider rewording
  0-39%:    Poor alignment, significant rewording needed

Skill Fit (Technical Skills Match):
  80-100%:  Excellent skill coverage
  60-79%:   Good coverage with minor gaps
  40-59%:   Fair coverage, skill development needed
  0-39%:    Major skill gaps, significant learning required

================================================================================
                        END OF REPORT
================================================================================
CVdOST - AI Career Engine
For more insights, visit the Analytics & Insights section.
"""
        
        # Create download button
        st.download_button(
            label="📊 Download Full AI Report",
            data=report_content,
            file_name=f"ResuMate_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )
        
        # Also offer JSON export for advanced users
        st.divider()
        st.subheader("📋 Advanced Export Formats")
        
        col1, col2 = st.columns(2)
        
        with col1:
            json_data = json.dumps(result, indent=2, default=str)
            st.download_button(
                label="📦 Export as JSON",
                data=json_data,
                file_name=f"ResuMate_Data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        with col2:
            # CSV export of scores
            scores_df = pd.DataFrame({
                "Metric": ["ATS Score", "Semantic Match", "Skill Fit"],
                "Score": [ats_final_score, semantic_match, skill_fit]
            })
            if components:
                for comp_name, comp_score in components.items():
                    scores_df = pd.concat([scores_df, pd.DataFrame({
                        "Metric": [comp_name],
                        "Score": [comp_score]
                    })], ignore_index=True)
            
            csv_data = scores_df.to_csv(index=False)
            st.download_button(
                label="📊 Export Scores as CSV",
                data=csv_data,
                file_name=f"CVdOST_Scores_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        st.success("✅ Ready to export! Choose your preferred format above.")
