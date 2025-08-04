import streamlit as st
import pandas as pd

st.set_page_config(page_title="Admin Staff Salary Evaluation", layout="wide")

st.title("Administrative Staff Salary Evaluation Dashboard")

st.header("1. Candidate Information")
candidate_name = st.text_input("Candidate Name")
position_title = st.text_input("Position Title")

st.header("2. Upload Documents")
cv_file = st.file_uploader("Upload CV", type=["pdf", "docx"])
jd_file = st.file_uploader("Upload Job Description", type=["pdf", "docx"])
interview_file = st.file_uploader("Upload Interview Evaluation", type=["pdf", "docx"])
equity_file = st.file_uploader("Upload Internal Equity Sheet (Excel)", type=["xlsx"])

st.header("3. Primary Scoring (AI-Powered Placeholder)")
st.write("📌 *Scores are auto-filled as placeholders. Adjust as needed.*")

education_score = st.slider("Education & Qualifications", 0, 10, 7)
experience_score = st.slider("Experience", 0, 10, 7)
performance_score = st.slider("Performance Potential", 0, 10, 7)

total_score = education_score + experience_score + performance_score
st.metric("Total Score", total_score)

if total_score >= 25:
    step_interval = "Top Range"
elif total_score >= 20:
    step_interval = "Mid-Upper Range"
elif total_score >= 15:
    step_interval = "Mid Range"
elif total_score >= 10:
    step_interval = "Lower-Mid Range"
else:
    step_interval = "Bottom Range"

st.subheader(f"Step Interval: {step_interval}")

st.header("4. Internal Equity Analysis")

if equity_file:
    try:
        df = pd.read_excel(equity_file)
        filtered_df = df[df['Position Title'].str.lower() == position_title.strip().lower()]
        if not filtered_df.empty:
            avg_salary = filtered_df['Comp Rate'].mean()
            min_salary = filtered_df['Comp Rate'].min()
            max_salary = filtered_df['Comp Rate'].max()

            st.dataframe(filtered_df)

            st.markdown(f'''
            - **Peer Average Salary:** ${avg_salary:,.2f}  
            - **Min Salary:** ${min_salary:,.2f}  
            - **Max Salary:** ${max_salary:,.2f}
            ''')

            equity_recommendation = st.selectbox("Internal Equity Placement", [
                "Above Peers (Higher in Interval)",
                "Aligned with Peers (Mid Interval)",
                "Below Peers (Lower in Interval)"
            ])
        else:
            st.warning("No matching records found for this position.")
            equity_recommendation = st.selectbox("Manual Equity Placement", [
                "Above Peers (Higher in Interval)",
                "Aligned with Peers (Mid Interval)",
                "Below Peers (Lower in Interval)"
            ])
    except Exception as e:
        st.error(f"Error reading the Excel file: {e}")
        equity_recommendation = "N/A"
else:
    equity_recommendation = st.selectbox("Internal Equity Placement (No file uploaded)", [
        "Above Peers (Higher in Interval)",
        "Aligned with Peers (Mid Interval)",
        "Below Peers (Lower in Interval)"
    ])

st.header("5. Additional Considerations")

budget = st.selectbox("Organizational Budget Flexibility", [
    "High Budget Flexibility",
    "Moderate Flexibility",
    "Minimal Flexibility"
])

negotiation = st.selectbox("Candidate Negotiation/Expectations", [
    "Expectations Aligned",
    "Slight Gap - Negotiable",
    "Significant Gap"
])

st.header("6. Final Recommendation")

final_summary = f"""
**Candidate:** {candidate_name}  
**Position Title:** {position_title}  

### Primary Scoring:
- Education Score: {education_score}
- Experience Score: {experience_score}
- Performance Potential: {performance_score}
- **Total Score:** {total_score} -> **{step_interval}**

### Internal Equity:
- Placement: {equity_recommendation}

### Budget & Negotiation:
- Budget: {budget}
- Negotiation: {negotiation}
"""

st.text_area("Final Justification Summary", value=final_summary, height=300)

st.markdown("---")
st.markdown("💡 *To save or share, copy the summary above or use your browser’s print-to-PDF feature.*")
