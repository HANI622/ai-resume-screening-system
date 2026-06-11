import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import webbrowser
import re

from difflib import SequenceMatcher
from reportlab.pdfgen import canvas
from pdf_reader import extract_text
from skill_extractor import extract_skills
from matcher import calculate_match
from candidate_parser import (
    extract_name,
    extract_email,
    extract_phone
)

# ==========================
# PAGE CONFIG
# ==========================

st.set_page_config(
    page_title="AI Resume Screening System",
    page_icon="📄",
    layout="wide"
)

# ==========================
# CUSTOM CSS
# ==========================

st.markdown("""
<style>

.main{
    background-color:#F8FAFC;
}

h1{
    color:#1E3A8A;
    text-align:center;
    font-weight:700;
}
            
div[data-testid="stMetric"]{
    background:white;
    border-radius:15px;
    padding:15px;
    box-shadow:0 4px 10px rgba(0,0,0,0.1);
    transition:0.3s;
}

div[data-testid="stMetric"]:hover{
    transform:translateY(-5px);
}

div.stButton > button{
    width:100%;
    border-radius:12px;
    background:#2563EB;
    color:white;
    border:none;
    font-weight:bold;
    padding:10px;
}
            
.stButton button{
    background:linear-gradient(90deg,#2563EB,#3B82F6);
    color:white;
    border:none;
    border-radius:10px;
    font-weight:bold;
}  

.stButton button:hover{
    background:#1D4ED8;
    color:white;
}                 
            
section[data-testid="stSidebar"]{
    background: linear-gradient(
        180deg,
        #111827,
        #1F2937,
        #374151
    );
}
h2{
    color:#FBBF24;
}
            
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: white !important;
    font-weight: bold;
}     

input {
    border-radius: 10px !important;
    border: 1px solid #334155 !important;
}   

label {
    color: white !important;
    font-weight: 600 !important;
}      

.stTextInput input{
    background:white !important;
    color:black !important;
    border-radius:12px !important;
    border:1px solid #CBD5E1 !important;
}      

</style>
""", unsafe_allow_html=True)

def extract_experience(text):

    pattern = r'(\d+)\+?\s*(year|years|yr|yrs)'

    matches = re.findall(
        pattern,
        text.lower()
    )

    if matches:

        years = [
            int(match[0])
            for match in matches
        ]

        return max(years)

    return 0

# ==========================
# LOGIN SYSTEM
# ==========================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:


    st.sidebar.markdown("""
    <h2 style='text-align:center;color:white;'>
    🔐 Admin Login
    </h2>
    """, unsafe_allow_html=True)
    
    username = st.sidebar.text_input("Username")

    password = st.sidebar.text_input(
        "Password",
        type="password"
    )

    if st.sidebar.button("Login"):

        if username == "admin" and password == "admin123":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.sidebar.error("Invalid Credentials")

    st.stop()

# ==========================
# SIDEBAR
# ==========================

st.sidebar.markdown("""
<h2 style='color:white; text-align:center;'>
📊 ATS Dashboard
</h2>
""", unsafe_allow_html=True)

if st.sidebar.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.rerun()

st.sidebar.info("""
📄 Upload Resumes

📝 Paste Job Description

🏆 Get Rankings

📊 Download Reports
""")


# ==========================
# HEADER
# ==========================

st.markdown("""
<h1 style='text-align:center; color:#1E3A8A;'>
📄 AI Resume Screening System
</h1>

<p style='text-align:center; font-size:18px;'>
Smart Resume Ranking & Candidate Shortlisting Platform
</p>
""", unsafe_allow_html=True)

# ==========================
# INPUTS
# ==========================

uploaded_files = st.file_uploader(
    "Upload Resumes",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:

    st.sidebar.markdown("""
    <div style="
    background:#1E3A8A;
    padding:10px;
    border-radius:10px;
    text-align:center;
    color:white;
    font-size:20px;
    font-weight:bold;
    margin-bottom:10px;
    ">
    📊 Quick Stats
    </div>
    """, unsafe_allow_html=True)

    st.sidebar.write(
        f"📂 Uploaded Resumes: {len(uploaded_files)}"
    )

if uploaded_files:

    file_names = []

    duplicates = []

    for file in uploaded_files:

        if file.name in file_names:
            duplicates.append(file.name)

        else:
            file_names.append(file.name)

    if duplicates:

        st.error(
            f"⚠️ Duplicate Resume Found: {', '.join(duplicates)}"
        )
if uploaded_files:

    st.sidebar.markdown(f"""
    <div style="
    background:#0F766E;
    padding:15px;
    border-radius:12px;
    margin-bottom:10px;
    color:white;
    font-size:18px;
    font-weight:bold;
    ">
    📂 Uploaded Resumes: {len(uploaded_files)}
    </div>
    """, unsafe_allow_html=True)

job_description = st.text_area(
    "Paste Job Description"
)

st.subheader("🔍 Search Candidate")

search = st.text_input(
    "Enter Name or Email"
)

filter_option = st.selectbox(
    "Filter Candidates",
    ["All", "Selected", "Rejected"]
)

results = []
duplicate_resumes = []

# ==========================
# ANALYSIS
# ==========================

if uploaded_files and job_description:

    st.header("📋 Resume Analysis")

    for file in uploaded_files:

        resume_text = extract_text(file)

        name = extract_name(resume_text)
        email = extract_email(resume_text)
        phone = extract_phone(resume_text)

        skills = extract_skills(resume_text)

        experience = extract_experience(
            resume_text
        )

        matched, missing, score = calculate_match(
                    skills,
                    job_description
                )

        

        status = "🟢 Selected" if score >= 60 else "🔴 Rejected"

        if score >= 80:
            recommendation = "🌟 Strongly Recommended"

        elif score >= 60:
            recommendation = "✅ Recommended"

        else:
            recommendation = "❌ Not Suitable"

        results.append({
            "Rank": 0,
            "Name": name,
            "Email": email,
            "Phone": phone,
            "Experience": experience,
            "Resume": file.name,
            "Score": score,
            "Matched Skills": len(matched),
            "Status": status,
            "Recommendation": recommendation,
            "Skills": skills,
            "Matched": matched,
            "Missing": missing,
            "Resume Text": resume_text
        })

        for existing in results[:-1]:

            similarity = SequenceMatcher(
                None,
                existing["Resume Text"],
                resume_text
            ).ratio() * 100

            if similarity >= 80:

                duplicate_resumes.append({
                    "resume1": existing["Resume"],
                    "resume2": file.name,
                    "similarity": round(similarity, 2)
                })

    # ==========================
    # SORT RESULTS
    # ==========================
    if duplicate_resumes:

        st.error("⚠ Possible Duplicate Resumes Detected")

        for dup in duplicate_resumes:

            st.warning(
                f"{dup['resume1']} ↔ {dup['resume2']} | Similarity: {dup['similarity']}%"
            )

    results = sorted(
        results,
        key=lambda x: x["Score"],
        reverse=True
    )

    
    # SEARCH

    if search:

        search = search.lower()

        results = [
            r for r in results
            if search in r["Name"].lower()
            or search in r["Email"].lower()
        ]

    # FILTER

    if filter_option == "Selected":
        results = [
            r for r in results
            if r["Status"] == "🟢 Selected"
    ]

    elif filter_option == "Rejected":
        results = [
            r for r in results
            if r["Status"] == "🔴 Rejected"
    ]
        
    if len(results) == 0:

        if filter_option == "Selected":
            st.warning("⚠️ No Selected Candidates Found")

        elif filter_option == "Rejected":
            st.warning("⚠️ No Rejected Candidates Found")

        else:
            st.warning("⚠️ No Candidates Found")

    else:    
        
        st.header("📂 Candidate Details")

        for r in results:

            with st.expander(
                f"📄 {r['Resume']} | {r['Name']}"
                ):

                    st.write(f"👤 Name: {r['Name']}")
                    st.write(f"📧 Email: {r['Email']}")
                    st.write(f"📱 Phone: {r['Phone']}")
                    st.write(
                        f"💼 Experience: {r['Experience']} Years"
                    )
                    st.write(f"🎯 Score: {r['Score']}%")
                    st.write(f"📌 Status: {r['Status']}")    
        
    

    for r in results:

        st.markdown(
            f"""
            <div style="
            background:white;
            padding:15px;
            border-radius:12px;
            margin-top:10px;
            box-shadow:0 2px 8px rgba(0,0,0,0.1);
            ">
            <h3>👤 {r['Name']}</h3>
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.expander("📂 Candidate Details"):

            st.write(f"📧 Email: {r['Email']}")
            if st.button(
                f"📧 Email {r['Name']}",
                key=f"email_{r['Email']}"
            ):
                webbrowser.open(
                    f"mailto:{r['Email']}"
            )
            st.write(f"📱 Phone: {r['Phone']}")
            st.write(f"📌 Status: {r['Status']}")
            st.write(f"💡 Recommendation: {r['Recommendation']}")
            st.write(f"🎯 Score: {r['Score']}%")
            st.subheader("📄 Resume Preview")
            st.text_area(
                "Resume Content",
                r["Resume Text"][:2000],
                height=250,
                disabled=True,
                key=f"preview_{r['Email']}"
            )

        st.subheader("🛠 Detected Skills")

        for skill in r["Skills"]:
            st.write(f"✅ {skill}")

        st.subheader("✅ Matched Skills")

        if len(r["Matched"]) > 0:

            for skill in r["Matched"]:
                st.write(f"✅ {skill}")

        else:
            st.write("No Matched Skills Found") 

        st.subheader("❌ Missing Skills")

        if len(r["Missing"]) > 0:

            for skill in r["Missing"]:
                st.write(f"❌ {skill}")

        else:
            st.write("No Missing Skills")      

        st.subheader("📈 Match Score")

        st.progress(int(r["Score"]))

        st.success(f"{r['Score']}% Match Found")
        
        st.markdown("---")    

    # RANKING

    for i, candidate in enumerate(results, start=1):
        candidate["Rank"] = i

    # ==========================
    # METRICS
    # ==========================

    total_candidates = len(results)

    selected_count = len(
        [r for r in results if r["Status"] == "🟢 Selected"]
    )

    rejected_count = len(
        [r for r in results if r["Status"] == "🔴 Rejected"]
    )

    st.sidebar.markdown("### 📈 Analysis Stats")

    st.sidebar.markdown(f"""
    <div style="
    background:#14532D;
    padding:15px;
    border-radius:12px;
    margin-bottom:10px;
    color:white;
    font-size:18px;
    font-weight:bold;
    ">
    🟢 Selected: {selected_count}
    </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown(f"""
    <div style="
    background:#7F1D1D;
    padding:15px;
    border-radius:12px;
    margin-bottom:10px;
    color:white;
    font-size:18px;
    font-weight:bold;
    ">
    🔴 Rejected: {rejected_count}
    </div>
    """, unsafe_allow_html=True)

    if results:

        st.sidebar.markdown(f"""
        <div style="
        background:#1E40AF;
        padding:15px;
        border-radius:12px;
        margin-bottom:10px;
        color:white;
        font-size:18px;
        font-weight:bold;
        ">
        🏆 Top Score: {results[0]['Score']}%
        </div>
        """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "📄 Total Candidates",
        total_candidates
    )

    col2.metric(
        "🟢 Selected",
        selected_count
    )

    col3.metric(
        "🔴 Rejected",
        rejected_count
    )

    if results:
        col4.metric(
            "🏆 Top Score",
            f"{results[0]['Score']}%"
        )
    else:
        col4.metric(
            "🏆 Top Score",
            "0%"
        )

        

    # ==========================
    # RANKINGS
    # ==========================

    st.header("🏆 Resume Rankings")

    for i, r in enumerate(results, start=1):
        st.write(
            f"{i}. {r['Resume']} - {r['Score']}%"
        )

    # ==========================
    # TOP CANDIDATE
    # ==========================

    if results:

        best = results[0]

        st.markdown(
            f"""
            <div style="
            background:#DCFCE7;
            padding:20px;
            border-radius:15px;
            border-left:8px solid green;
            margin-top:10px;
            ">
            <h2>🥇 Top Candidate</h2>
            <h3>{best['Name']}</h3>
            <p>📧 {best['Email']}</p>
            <p>📄 {best['Resume']}</p>
            <p>🎯 Score: {best['Score']}%</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    else:
        st.warning("No candidate found")

    st.header("⭐ Interview Shortlist")

    selected_emails = [
        r["Email"]
        for r in results
        if r["Status"] == "🟢 Selected"
    ]

    if len(selected_emails) > 0:

        email_list = ";".join(selected_emails)

        if st.button("📧 Email All Selected Candidates"):

            webbrowser.open(
                f"mailto:{email_list}"
            )

    shortlisted = [
        r for r in results
        if r["Status"] == "🟢 Selected"
    ]

    shortlisted = sorted(
        shortlisted,
        key=lambda x: x["Score"],
        reverse=True
    )

    top3 = shortlisted[:3]

    if len(top3) > 0:
        medals = ["🥇", "🥈", "🥉"]
        for i, candidate in enumerate(top3):
                    st.success(
                        f"{medals[i]} {candidate['Name']} - {candidate['Score']}%"
        )
                    
    else:
        st.warning(
            "No Candidates Available For Interview"
        )                

    # ==========================
    # TABLE
    # ==========================
    if len(results) > 0:

        df = pd.DataFrame(results)

        selected_df = pd.DataFrame(
        [
            r for r in results
            if r["Status"] == "🟢 Selected"
        ]
        )

        

        report_df = df[
        [
            "Rank",
            "Name",
            "Email",
            "Phone",
            "Experience",
            "Score",
            "Matched Skills",
            "Status",
            "Recommendation"
        ]
    ]
        

        st.dataframe(
            df[
                [
                    "Rank",
                    "Name",
                    "Email",
                    "Phone",
                    "Experience",
                    "Score",
                    "Matched Skills",
                    "Status",
                    "Recommendation"
                ]
            ].style.highlight_max(
                subset=["Score"],
                color="lightgreen"
            ),
            use_container_width=True
        )

    # ==========================
    # DOWNLOAD EXCEL
    # ==========================
        if len(selected_df) > 0:

            selected_report_df = selected_df[
        [
            "Rank",
            "Name",
            "Email",
            "Phone",
            "Experience",
            "Score",
            "Matched Skills",
            "Status",
            "Recommendation"
        ]
    ]

            selected_excel = "selected_candidates.xlsx"

            selected_report_df.to_excel(
                selected_excel,
                index=False
            )

            with open(selected_excel, "rb") as file:

                st.download_button(
                    label="📥 Download Selected Candidates",
                    data=file,
                    file_name="selected_candidates.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="selected_download"
                )

        excel_file = "resume_rankings.xlsx"

        report_df.to_excel(
            excel_file,
            index=False
        )

        with open(excel_file, "rb") as file:

            st.download_button(
                label="📥 Download Excel Report",
                data=file,
                file_name="resume_rankings.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    # ==========================
    # DOWNLOAD PDF
    # ==========================

        pdf_file = "resume_report.pdf"

        c = canvas.Canvas(pdf_file)

        c.setFont("Helvetica-Bold", 16)
        c.drawString(
            50,
            800,
            "AI Resume Screening Report"
        )

        y = 760

        for r in results:

            c.setFont("Helvetica", 12)

            c.drawString(
                50,
                y,
                f"Name: {r['Name']}"
            )

            c.drawString(
                250,
                y,
                f"Score: {r['Score']}%"
            )

            c.drawString(
                400,
                y,
                f"Status: {r['Status']}"
            )

            y -= 30

            if y < 50:
                c.showPage()
                y = 800

        c.save()

        with open(pdf_file, "rb") as pdf:

            st.download_button(
                label="📄 Download PDF Report",
                data=pdf,
                file_name="resume_report.pdf",
                mime="application/pdf",
                key="pdf_download"
            )

        # ==========================
        # CHART
        # ==========================

        st.header("📊 Candidate Score Chart")

        fig, ax = plt.subplots(figsize=(8, 4))

        ax.bar(
            [r["Resume"] for r in results],
            [r["Score"] for r in results]
        )

        ax.set_ylabel("Score (%)")
        ax.set_xlabel("Candidates")
        ax.set_title("Resume Match Scores")

        plt.xticks(rotation=20)

        st.pyplot(fig)

    else:

        st.warning("⚠️ No Data Available")
else:

    st.info(
        "Please upload resumes and enter a Job Description."
    )