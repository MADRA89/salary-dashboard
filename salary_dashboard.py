import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
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
        ax.set_xlabel("Employee ID")
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
**Candidate:** {candidate_name}  
**Position Title:** {position_title}  
**Position Grade:** {position_grade}  

### Evaluation Scores:
- Education & Qualifications: {education_score}/10
- Experience: {experience_score}/10
- Performance Potential: {performance_score}/10
- **Total Score:** {total_score}/30 → Step Interval: Steps {step_range[0]} to {step_range[-1]}

### Final Decision:
- Selected Step: Step {final_step}
- Recommended Salary: AED {final_salary:,.2f}
- Budget Flexibility: {budget_flex}
- Candidate Expectations: {candidate_expectations}
"""

st.text_area("Editable Final Summary", value=summary_text, height=400)

# --- STAGE 7: FINAL REPORT DOWNLOAD ---
st.header("7. Download Final Evaluation Report")

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_page()
        self.set_auto_page_break(auto=True, margin=15)
        self.set_font("Arial", size=12)

    def add_title(self, title):
        self.set_font("Arial", 'B', 16)
        self.cell(0, 10, title, ln=True, align='C')
        self.ln(10)

    def add_section(self, header, content):
        self.set_font("Arial", 'B', 14)
        self.cell(0, 10, header, ln=True)
        self.set_font("Arial", size=12)
        self.multi_cell(0, 10, content)
        self.ln(5)

pdf = PDF()
pdf.add_title("HR Salary Evaluation Report")
pdf.add_section("1. Candidate Information", f"Candidate Name: {candidate_name}\nPosition Title: {position_title}\nPosition Grade: {position_grade}")

pdf.add_section("2. Evaluation Scores", f"""
Education & Qualifications: {education_score}/10
Experience: {experience_score}/10
Performance Potential: {performance_score}/10
Total Score: {total_score}/30
Suggested Step Interval: Steps {step_range[0]} to {step_range[-1]}
Selected Final Step: Step {final_step}
Recommended Salary: AED {final_salary:,.2f}
""")

pdf.add_section("3. Additional Adjustment Factors", f"Budget Flexibility: {budget_flex}\nCandidate Expectations: {candidate_expectations}")

pdf.add_section("4. Final Summary", summary_text)

pdf.add_section("5. Report Generated On", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

pdf_bytes = pdf.output(dest='S').encode('latin-1')

st.download_button(
    label="📄 Download Final PDF Report",
    data=pdf_bytes,
    file_name=f"Salary_Evaluation_{candidate_name.replace(' ', '_')}.pdf",
    mime='application/pdf'
)
