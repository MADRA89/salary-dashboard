import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from docx import Document
from docx.shared import Pt
import datetime

# --- PAGE CONFIG ---
st.set_page_config(page_title="HR Salary Evaluation", layout="wide")
st.title("Administrative Staff Salary Evaluation Dashboard")

# --- STAGE 1: CANDIDATE INFO ---
st.header("1. Candidate Information")
candidate_name = st.text_input("Candidate Name")
position_title = st.text_input("Position Title")
position_grade = st.text_input("Position Grade")

# --- STAGE 2: DOCUMENT UPLOADS ---
st.header("2. Upload Required Documents")
cv_file = st.file_uploader("Upload CV (PDF or DOCX)", type=["pdf", "docx"])
jd_file = st.file_uploader("Upload Job Description (PDF or DOCX)", type=["pdf", "docx"])
interview_file = st.file_uploader("Upload Interview Evaluation Sheet (PDF or DOCX)", type=["pdf", "docx"])
equity_file = st.file_uploader("Upload Internal Equity Sheet (Excel)", type=["xlsx"])

# --- STAGE 3: AI EVALUATION PLACEHOLDERS + MANUAL OVERRIDE ---
st.header("3. AI Evaluation Results (Editable by HR)")
education_score = st.slider("Education & Qualifications (Max 10)", 0, 10, 8)
experience_score = st.slider("Experience (Max 10)", 0, 10, 7)
performance_score = st.slider("Performance Potential (Max 10)", 0, 10, 7)

total_score = education_score + experience_score + performance_score
st.metric("Total Score", total_score)

# Step interval logic
if total_score >= 25:
    step_range = list(range(12, 16))
elif total_score >= 20:
    step_range = list(range(9, 12))
elif total_score >= 15:
    step_range = list(range(6, 9))
elif total_score >= 10:
    step_range = list(range(3, 6))
else:
    step_range = list(range(1, 3))

st.subheader(f"Suggested Step Interval: Steps {step_range[0]} to {step_range[-1]}")
final_step = st.selectbox("Select Final Step", step_range)
final_salary = st.number_input("Enter Final Recommended Salary (AED)", min_value=0, step=500)

# --- STAGE 4: INTERNAL EQUITY ANALYSIS ---
st.header("4. Internal Equity Comparison")

if equity_file:
    df = pd.read_excel(equity_file)
    filtered_df = df[df['Position Title'].str.lower() == position_title.strip().lower()]
    if not filtered_df.empty:
        avg_salary = filtered_df['Comp Rate'].mean()
        min_salary = filtered_df['Comp Rate'].min()
        max_salary = filtered_df['Comp Rate'].max()

        st.dataframe(filtered_df)

        st.markdown(f"""
        - **Average Peer Salary:** AED {avg_salary:,.2f}  
        - **Minimum Salary:** AED {min_salary:,.2f}  
        - **Maximum Salary:** AED {max_salary:,.2f}  
        - **Number of Peers:** {len(filtered_df)}
        """)

        fig, ax = plt.subplots()
        ax.bar(filtered_df['ID'].astype(str), filtered_df['Comp Rate'], color='skyblue', label='Peers')
        ax.axhline(y=final_salary, color='red', linestyle='--', label='Candidate Recommended Salary')
        ax.set_xlabel("Employee ID", fontsize=8)
        ax.set_ylabel("Compensation (AED)")
        ax.set_title("Candidate Salary vs Internal Peers")
        ax.legend()
        st.pyplot(fig)
else:
    st.info("Upload an Internal Equity Excel file to view comparison chart.")

# --- STAGE 5: SECONDARY FACTORS ---
st.header("5. Additional Adjustment Factors")
budget_flex = st.selectbox("Organizational Budget Flexibility", [
    "High Budget Flexibility",
    "Moderate Flexibility",
    "Minimal Flexibility"
])
candidate_expectations = st.selectbox("Candidate Salary Expectations", [
    "Expectations Aligned",
    "Slight Gap - Negotiable",
    "Significant Gap"
])

# --- STAGE 6: FINAL SUMMARY ---
st.header("6. Final Summary & Justification")

summary_text = f"""
Candidate: {candidate_name}
Position Title: {position_title}
Position Grade: {position_grade}

Evaluation Scores:
- Education & Qualifications: {education_score}/10
- Experience: {experience_score}/10
- Performance Potential: {performance_score}/10
- Total Score: {total_score}/30 → Step Interval: Steps {step_range[0]} to {step_range[-1]}

Final Decision:
- Selected Step: Step {final_step}
- Recommended Salary: AED {final_salary:,.2f}
- Budget Flexibility: {budget_flex}
- Candidate Expectations: {candidate_expectations}
"""

st.text_area("Editable Final Summary", value=summary_text, height=400)

# --- STAGE 7: FINAL REPORT DOWNLOAD AS WORD ---
st.header("7. Download Final Evaluation Report (Word DOCX)")

def create_word_report():
    doc = Document()
    doc.add_heading('HR Salary Evaluation Report', level=0)

    doc.add_heading('1. Candidate Information', level=1)
    doc.add_paragraph(f"Candidate Name: {candidate_name}")
    doc.add_paragraph(f"Position Title: {position_title}")
    doc.add_paragraph(f"Position Grade: {position_grade}")

    doc.add_heading('2. Evaluation Scores', level=1)
    doc.add_paragraph(f"Education & Qualifications: {education_score}/10")
    doc.add_paragraph(f"Experience: {experience_score}/10")
    doc.add_paragraph(f"Performance Potential: {performance_score}/10")
    doc.add_paragraph(f"Total Score: {total_score}/30")
    doc.add_paragraph(f"Suggested Step Interval: Steps {step_range[0]} to {step_range[-1]}")
    doc.add_paragraph(f"Selected Final Step: Step {final_step}")
    doc.add_paragraph(f"Recommended Salary: AED {final_salary:,.2f}")

    doc.add_heading('3. Additional Adjustment Factors', level=1)
    doc.add_paragraph(f"Budget Flexibility: {budget_flex}")
    doc.add_paragraph(f"Candidate Expectations: {candidate_expectations}")

    doc.add_heading('4. Final Summary & Justification', level=1)
    doc.add_paragraph(summary_text)

    doc.add_heading('5. Report Generated On', level=1)
    doc.add_paragraph(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # حفظ الملف في ذاكرة مؤقتة
    file_stream = BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream

word_report = create_word_report()

st.download_button(
    label="📄 Download Final Evaluation Report (Word DOCX)",
    data=word_report,
    file_name=f"Salary_Evaluation_{candidate_name.replace(' ', '_')}.docx",
    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)

