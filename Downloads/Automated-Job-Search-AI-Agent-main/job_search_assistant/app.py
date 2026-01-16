import streamlit as st
from config import APP_TITLE, APP_ICON, CUSTOM_CSS, OPENAI_API_KEY
from utils.resume_parser import ResumeParser
from utils.serp_api_searcher import SerpApiSearcher
from utils.job_storage import JobStorage
import json

def main():
    # 1. Page Configuration
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon=APP_ICON,
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # 2. Inject Custom CSS
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    # 3. Header Section (Gradient Banner)
    st.markdown("""
        <div class="main-header">
            <h1>Professional Job Search Assistant</h1>
            <div class="feature-badges">
                <span class="feature-badge">AI-powered job search</span>
                <span class="feature-badge">Resume analysis</span>
                <span class="feature-badge">Interview preparation</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Initialize Session State
    if "storage" not in st.session_state:
        st.session_state.storage = JobStorage()
    if "selected_platform" not in st.session_state:
        st.session_state.selected_platform = "All"

    # 4. Main Navigation Tabs
    tab_resume, tab_search, tab_interview, tab_saved = st.tabs([
        "📄 Resume Analysis", 
        "🔍 Job Search", 
        "🎤 Interview Preparation",
        "💾 Saved Jobs"
    ])

    # --- TAB 1: RESUME ANALYSIS ---
    with tab_resume:
        col_upload, col_result = st.columns([1, 2])
        
        with col_upload:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader("Upload Resume")
            uploaded_file = st.file_uploader("Upload PDF", type=['pdf'])
            
            analyze_btn = st.button("✨ Analyze with AI", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_result:
            if uploaded_file and analyze_btn:
                if not OPENAI_API_KEY:
                    st.error("Please configure your OpenAI API Key first!")
                else:
                    with st.spinner("Analyzing resume..."):
                        parser = ResumeParser()
                        temp_path = parser.save_upload_file(uploaded_file)
                        resume_data = parser.parse(temp_path)
                        
                    if "error" in resume_data:
                        st.error(f"Error parsing resume: {resume_data['error']}")
                    else:
                        st.success("Resume Parsed Successfully!")

                        # --- RESULT TABS ---
                        res_tab_summary, res_tab_skills, res_tab_analysis, res_tab_raw = st.tabs([
                            "Summary", "Skills & Experience", "Analysis", "Raw Text"
                        ])

                        # === TAB 1: SUMMARY ===
                        with res_tab_summary:
                            # Top Cards: Key Components & ATS Tips
                            st.markdown("""
                            <div style="display: flex; gap: 20px; flex-wrap: wrap; margin-bottom: 20px;">
                            <div style="display: flex; gap: 20px; margin-bottom: 20px;">
                                <div class="glass-card hover-effect" style="flex: 1; background-color: rgba(30, 58, 138, 0.6); border: 1px solid #3B82F6;">
                                    <h4 style="color: white; margin-bottom: 10px;">Key Resume Components</h4>
                                    <ul style="color: #CBD5E1; padding-left: 20px;">
                                        <li>Strong Action Verbs used</li>
                                        <li>Quantifiable achievements included</li>
                                        <li>Clear structure and formatting</li>
                                    </ul>
                                </div>
                                <div class="glass-card hover-effect" style="flex: 1; background-color: rgba(30, 58, 138, 0.6); border: 1px solid #3B82F6;">
                                    <h4 style="color: white; margin-bottom: 10px;">ATS Optimization Tips</h4>
                                    <ul style="color: #CBD5E1; padding-left: 20px;">
                                        <li>Use standard section headings</li>
                                        <li>Include industry-relevant keywords</li>
                                        <li>Keep formatting simple and clean</li>
                                    </ul>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                            st.markdown("### Resume Analysis Summary")
                            col_strength, col_improve = st.columns(2)
                            
                            with col_strength:
                                st.markdown("""
                                <h5 style="color: #3B82F6;">Strengths</h5>
                                <div style="background-color: #1E3A8A; padding: 15px; border-radius: 8px; border: 1px solid #1E40AF;">
                                    <p style="margin: 5px 0;">✅ Strong technical skills in programming and/or data science</p>
                                    <p style="margin: 5px 0;">✅ Cloud platform experience</p>
                                    <p style="margin: 5px 0;">✅ Machine learning knowledge</p>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            with col_improve:
                                st.markdown("""
                                <h5 style="color: #EF4444;">Areas to Improve</h5>
                                <div style="background-color: #3F2C2C; padding: 15px; border-radius: 8px; border: 1px solid #7F1D1D;">
                                    <p style="margin: 5px 0; color: #FCA5A5;">No obvious improvement areas identified</p>
                                </div>
                                """, unsafe_allow_html=True)

                        # === TAB 2: SKILLS & EXPERIENCE ===
                        with res_tab_skills:
                            # --- 1. CONTACT INFO ---
                            contact = resume_data.get("contact_info", {})
                            st.markdown("### 👤 Candidate Profile")
                            
                            # Note: Text colors updated to slate/dark for light theme
                            contact_html = f"""
                            <div class="glass-card" style="display: flex; gap: 20px; align-items: center; flex-wrap: wrap; margin-top: 10px;">
                                <div style="flex: 1; min-width: 200px;">
                                    <p style="color: #94A3B8; margin-bottom: 4px; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.5px;">Email</p>
                                    <p style="font-weight: 600; font-size: 1rem; color: #F8FAFC;">{contact.get('email', 'N/A')}</p>
                                </div>
                                <div style="flex: 1; min-width: 200px;">
                                    <p style="color: #94A3B8; margin-bottom: 4px; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.5px;">Phone</p>
                                    <p style="font-weight: 600; font-size: 1rem; color: #F8FAFC;">{contact.get('phone', 'N/A')}</p>
                                </div>
                                <div style="flex: 1; min-width: 200px;">
                                    <p style="color: #94A3B8; margin-bottom: 4px; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.5px;">Links</p>
                                    <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                            """
                            
                            if contact.get('linkedin'):
                                contact_html += f'<a href="{contact["linkedin"]}" target="_blank" style="text-decoration: none; background: #1E293B; color: #3B82F6; padding: 4px 12px; border-radius: 15px; font-size: 0.85rem; border: 1px solid #334155;">LinkedIn ↗</a>'
                            if contact.get('github'):
                                contact_html += f'<a href="{contact["github"]}" target="_blank" style="text-decoration: none; background: #1E293B; color: #3B82F6; padding: 4px 12px; border-radius: 15px; font-size: 0.85rem; border: 1px solid #334155;">GitHub ↗</a>'
                            if contact.get('portfolio'):
                                contact_html += f'<a href="{contact["portfolio"]}" target="_blank" style="text-decoration: none; background: #1E293B; color: #3B82F6; padding: 4px 12px; border-radius: 15px; font-size: 0.85rem; border: 1px solid #334155;">Portfolio ↗</a>'
                            
                            contact_html += """
                                    </div>
                                </div>
                            </div>
                            """
                            st.markdown(contact_html, unsafe_allow_html=True)
                            
                            # --- 2. SKILLS ---
                            skills = resume_data.get("skills", {})
                            if skills:
                                st.markdown("### 🛠️ Skills Matrix")
                                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                                for category, items in skills.items():
                                    if items:
                                        cat_title = category.replace('_', ' ').title()
                                        st.markdown(f"<p style='margin-bottom: 8px; font-weight: 600; color: #F1F5F9;'>{cat_title}</p>", unsafe_allow_html=True)
                                        # Render pills
                                        pill_html = "".join([f'<span style="background: #3B82F6; color: white; padding: 6px 14px; border-radius: 12px; font-size: 0.85rem; margin-right: 6px; margin-bottom: 8px; display: inline-block;">{item}</span>' for item in items])
                                        st.markdown(f'<div style="margin-bottom: 16px;">{pill_html}</div>', unsafe_allow_html=True)
                                st.markdown('</div>', unsafe_allow_html=True)

                            # --- 3. EXPERIENCE & EDUCATION ---
                            col_exp, col_edu = st.columns(2)
                            
                            with col_exp:
                                st.markdown("### 💼 Experience")
                                experience = resume_data.get("experience", [])
                                if experience:
                                    for exp in experience:
                                        st.markdown(f"""
                                        <div class="glass-card hover-effect" style="padding: 20px; border-left: 4px solid #3B82F6; margin-bottom: 15px;">
                                            <h4 style="margin: 0; color: #F8FAFC; font-size: 1.1rem;">{exp.get('job_title', 'Role')}</h4>
                                            <p style="color: #60A5FA; font-weight: 600; margin: 4px 0;">{exp.get('company', 'Company')}</p>
                                            <p style="color: #94A3B8; font-size: 0.9rem; margin-bottom: 10px;">{exp.get('duration', 'Dates')}</p>
                                            <p style="font-size: 0.95rem; line-height: 1.6; color: #CBD5E1;">{exp.get('description', '')}</p>
                                        </div>
                                        """, unsafe_allow_html=True)
                                else:
                                    st.info("No experience found.")

                            with col_edu:
                                st.markdown("### 🎓 Education")
                                education = resume_data.get("education", [])
                                if education:
                                    for edu in education:
                                        st.markdown(f"""
                                        <div class="glass-card hover-effect" style="padding: 20px; border-left: 4px solid #8B5CF6; margin-bottom: 15px;">
                                            <h4 style="margin: 0; color: #F8FAFC; font-size: 1.1rem;">{edu.get('degree', 'Degree')}</h4>
                                            <p style="color: #A78BFA; font-weight: 600; margin: 4px 0;">{edu.get('institution', 'University')}</p>
                                            <p style="color: #94A3B8; font-size: 0.9rem;">{edu.get('year', 'Year')}</p>
                                        </div>
                                        """, unsafe_allow_html=True)
                                else:
                                    st.info("No education found.")
                        
                        # === TAB 3: ANALYSIS ===
                        with res_tab_analysis:
                            # Extract Keywords
                            from utils.resume_keyword_extractor import ResumeKeywordExtractor
                            
                            extractor = ResumeKeywordExtractor()
                            extracted_info = extractor.extract_keywords(resume_data)
                            suggested_query = extractor.get_search_query(extracted_info)

                            st.markdown("### 📊 Detailed AI Analysis")
                            
                            # Display Search Query Suggestion
                            st.info(f"💡 **Suggested Job Search Query:** `{suggested_query}`")
                            
                            col_analysis_1, col_analysis_2 = st.columns(2)
                            
                            with col_analysis_1:
                                st.markdown("#### 🎯 Identified Job Titles")
                                if extracted_info['job_titles']:
                                    for title in extracted_info['job_titles']:
                                        st.markdown(f"- **{title.title()}**")
                                else:
                                    st.write("No specific job titles found.")

                                st.markdown("#### 🧠 Key Technical Concepts")
                                if extracted_info['concepts']:
                                    st.markdown(", ".join([f"`{c}`" for c in extracted_info['concepts']]))
                                else:
                                    st.write("No technical concepts identified.")

                            with col_analysis_2:
                                st.markdown("#### 💻 Tech Stack & Tools")
                                if extracted_info['tech_stack']:
                                    tech_html = "".join([f'<span style="background: rgba(59, 130, 246, 0.2); color: #93C5FD; padding: 4px 10px; border-radius: 12px; font-size: 0.85rem; margin-right: 6px; margin-bottom: 6px; display: inline-block; border: 1px solid rgba(59, 130, 246, 0.3);">{tech}</span>' for tech in extracted_info['tech_stack'][:20]]) # Limit to 20 to avoid clutter
                                    st.markdown(tech_html, unsafe_allow_html=True)
                                else:
                                    st.write("No specific tech stack identified.")
                            
                        # === TAB 4: RAW TEXT ===
                        with res_tab_raw:
                            st.markdown("### 📝 Extracted Text")
                            st.text_area("Raw Resume Text", value=resume_data.get('raw_text', 'No text extracted'), height=400)

    # --- TAB 2: JOB SEARCH ---
    with tab_search:
        # 1. Main Header for Tab (Matches Screenshot)
        st.markdown("""
            <div class="main-header" style="text-align: left; padding: 15px 20px; background: #1E3A8A; margin-bottom: 20px;">
                <h2 style="margin:0; font-size: 1.8rem;">Job Search</h2>
            </div>
        """, unsafe_allow_html=True)

        # 2. Search Mode Toggle (Custom visual simulation)
        col_mode1, col_mode2 = st.columns(2)
        with col_mode1:
            if st.button("📄 Resume-Based Search", use_container_width=True, key="mode_resume", 
                       help="Generate query from your uploaded resume"):
                 st.session_state.search_mode = "resume"
        with col_mode2:
            # Highlight this button to look selected by default or based on state, simplified for now
            if st.button("🔍 Custom Search", use_container_width=True, key="mode_custom"):
                 st.session_state.search_mode = "custom"
        
        # Visual separator
        st.markdown("---")

        # 3. Search Criteria Section
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<h4 style="color:white; border-bottom: 2px solid #3B82F6; padding-bottom: 10px; margin-bottom: 20px;">Search Criteria</h4>', unsafe_allow_html=True)
        
        col_input1, col_input2 = st.columns(2)
        with col_input1:
            query = st.selectbox(
                "Job Title:", 
                options=["Software Engineer", "Data Scientist", "Product Manager", "DevOps Engineer", "Full Stack Developer", "AI Engineer", "Frontend Developer", "Backend Developer"],
                index=5 # Default to AI Engineer
            )
        with col_input2:
            location = st.selectbox(
                "Location:", 
                options=["Remote", "United States", "India", "Canada", "United Kingdom", "Germany", "Hybrid"],
                index=0
            )
        
        # 4. Advanced Filters
        with st.expander("Advanced Filters", expanded=True):
            st.markdown("##### Job Types (optional):")
            job_types = st.multiselect(
                "Job Types",
                options=["Full-time", "Contract", "Internship", "Part-time", "Temporary"],
                default=["Full-time", "Contract", "Internship"],
                label_visibility="collapsed"
            )

            st.markdown("##### Years of experience:")
            experience = st.select_slider(
                "Years of experience",
                options=["0-1", "1-3", "3-5", "5-10", "10+"],
                value="0-1",
                label_visibility="collapsed"
            )
            
            st.markdown("##### Show jobs posted within:")
            posted_date = st.select_slider(
                "Posted date",
                options=["1 day", "3 days", "7 days", "14 days", "Any time"],
                value="1 day",
                label_visibility="collapsed"
            )

            st.markdown("##### Job Platforms:")
            platforms = st.multiselect(
                "Job Platforms",
                options=["Indeed", "LinkedIn", "ZipRecruiter", "Glassdoor", "Monster"],
                default=["Indeed", "LinkedIn", "ZipRecruiter", "Glassdoor", "Monster"],
                label_visibility="collapsed"
            )
            
            st.markdown("##### Jobs per platform:")
            limit = st.slider("Jobs per platform", 1, 20, 5, label_visibility="collapsed")
            
            use_serp = st.checkbox("Use SerpAPI for real job listings", value=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # 5. Search Action
        search_btn = st.button("Find Jobs", use_container_width=True, type="primary")
        
        if search_btn:
            with st.spinner(f"Searching for {query} jobs in {location}..."):
                searcher = SerpApiSearcher()
                
                # Platform logic
                selected_platform = "All" # Simplified for this UI as it handles multiple internally if needed
                
                results = searcher.search_jobs(query=query, location=location, platform=selected_platform, count=limit)
                
                if results:
                    st.success(f"Found {len(results)} jobs!")
                    for job in results:
                        with st.expander(f"{job['title']} at {job['company']}"):
                            st.markdown(f"**Location:** {job['location']}")
                            st.markdown(f"**Platform:** {job['platform']}")
                            st.markdown(job.get('snippet', ''))
                            
                            col_apply, col_save = st.columns([1, 4])
                            with col_apply:
                                st.markdown(f"[👉 Apply Now]({job['apply_link']})")
                            with col_save:
                                if st.button("💾 Save Job", key=f"save_{job.get('link', job['title'])}"):
                                    saved = st.session_state.storage.save_job(job)
                                    if saved:
                                        st.toast(f"Saved: {job['title']}", icon="✅")
                                    else:
                                        st.toast("Job already saved!", icon="⚠️")
                else:
                    st.warning("No jobs found.")

    # --- TAB 3: INTERVIEW PREPARATION ---
    with tab_interview:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("Coming Soon: AI Interview Coach")
        st.write("Mock interviews with real-time feedback.")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- TAB 4: SAVED JOBS ---
    with tab_saved:
        st.markdown("## Saved Jobs")
        
        saved_jobs = st.session_state.storage.get_saved_jobs()
        
        if not saved_jobs:
            st.info("You haven't saved any jobs yet. Use the Job Search tab to find and save jobs.")
        else:
            for i, job in enumerate(saved_jobs):
                with st.container():
                    st.markdown(f"""
                    <div class="glass-card" style="padding: 15px; margin-bottom: 10px;">
                        <h4 style="margin:0; color:#1E293B;">{job['title']}</h4>
                        <p style="color: #64748B; margin-bottom: 5px;">{job['company']} • {job['location']}</p>
                        <div style="display: flex; gap: 10px; align-items: center; margin-top: 10px;">
                            <a href="{job['apply_link']}" target="_blank" style="text-decoration: none; color: #007AFF; font-weight:600;">Apply Link ↗</a>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("Remove", key=f"remove_{i}"):
                        st.session_state.storage.remove_job(job)
                        st.experimental_rerun()

if __name__ == "__main__":
    main()
