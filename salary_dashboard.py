import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from docx import Document
import datetime

# --- PAGE CONFIG & STYLE ---
st.set_page_config(page_title="HR Salary Evaluation", layout="wide", page_icon="📊")

st.markdown("""
    <style>
    .main { background-color: #f9fbfd; }
    h1, h2, h3, .stTextInput>label, .stSlider>label, .stSelectbox>label { color: #003566; }
    .stButton>button { background-color: #0077b6; color: white; border-radius: 8px; }
    .stDownloadButton>button { background-color: #00b4d8; color: white; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

st.title("💼 Administrative Staff Salary Evaluation Dashboard v2")

# --- SECTION 1: CANDIDATE INFO ---
st.header("1. Candidate Information")
candidate_name = st.text_input("Candidate Name")
position_title = st.text_input("Position Title")
position_grade = st.text_input("Position Grade")

# --- SECTION 2: DOCUMENT UPLOADS ---
st.header("2. Upload Required Documents")
cv_file = st.file_uploader("Upload CV (PDF or DOCX)", type=["pdf", "docx"])
jd_file = st.file_uploader("Upload Job Description (PDF or DOCX)", type=["pdf", "docx"])
interview_file = st.file_uploader("Upload Interview Evaluation Sheet (PDF or DOCX)", type=["pdf", "docx"])
equity_file = st.file_uploader("Upload Internal Equity Sheet (Excel)", type=["xlsx"])

# --- SECTION 3: SCORING ---
st.header("3. Evaluation Scores (Editable)")
education_score = st.slider("🎓 Education & Qualifications", 0, 10, 8)
experience_score = st.slider("💼 Experience", 0, 10, 7)
performance_score = st.slider("🚀 Performance Potential", 0, 10, 7)

total_score = education_score + experience_score + performance_score
st.metric("Total Score", total_score)

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

st.subheader(f"📈 Suggested Step Interval: Steps {step_range[0]} to {step_range[-1]}")
final_step = st.selectbox("Select Final Step", step_range)
final_salary = st.number_input("💰 Final Recommended Salary (AED)", min_value=0, step=500)

# --- SECTION 4: INTERNAL EQUITY ---
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

        fig, ax = plt.subplots(figsize=(8, 4))  # Smaller size
        ax.bar(filtered_df['ID'].astype(str), filtered_df['Comp Rate'], color='skyblue', label='Peers')
        ax.axhline(y=final_salary, color='red', linestyle='--', label='Candidate Recommended Salary')
        ax.set_xlabel("Employee ID", fontsize=6)
        ax.set_ylabel("Compensation (AED)", fontsize=6)
        ax.set_title("Candidate Salary vs Internal Peers", fontsize=8)
        ax.tick_params(axis='x', labelrotation=45, labelsize=6)
        ax.tick_params(axis='y', labelsize=6)
        ax.legend(fontsize=6)
        st.pyplot(fig)
    else:
        st.warning("No matching records found in Internal Equity Sheet.")
else:
    st.info("Upload an Excel file to analyze internal equity.")

# --- SECTION 5: OTHER FACTORS ---
st.header("5. Additional Adjustment Factors")
budget_flex = st.selectbox("📊 Organizational Budget Flexibility", [
    "High Budget Flexibility", "Moderate Flexibility", "Minimal Flexibility"
])
candidate_expectations = st.selectbox("🧾 Candidate Salary Expectations", [
    "Expectations Aligned", "Slight Gap - Negotiable", "Significant Gap"
])

# --- SECTION 6: FINAL SUMMARY ---
st.header("6. Final Summary & Justification")

summary_text = f"""
Candidate: {candidate_name}
Position Title: {position_title}
Position Grade: {position_grade}

Evaluation Scores:
- Education: {education_score}/10
- Experience: {experience_score}/10
- Performance: {performance_score}/10
- Total Score: {total_score}/30 → Step Range: {step_range[0]} to {step_range[-1]}

Final Decision:
- Final Step: Step {final_step}
- Recommended Salary: AED {final_salary:,.2f}
- Budget Flexibility: {budget_flex}
- Candidate Expectations: {candidate_expectations}
"""

st.text_area("📝 Editable Summary", value=summary_text, height=350)

# --- SECTION 7: WORD REPORT ---
st.header("7. Download Final Report (Word DOCX)")

def generate_word_report():
    doc = Document()
    doc.add_heading("HR Salary Evaluation Report", 0)

    doc.add_heading("1. Candidate Info", level=1)
    doc.add_paragraph(f"Candidate Name: {candidate_name}")
    doc.add_paragraph(f"Position Title: {position_title}")
    doc.add_paragraph(f"Position Grade: {position_grade}")

    doc.add_heading("2. Evaluation Scores", level=1)
    doc.add_paragraph(f"Education: {education_score}/10")
    doc.add_paragraph(f"Experience: {experience_score}/10")
    doc.add_paragraph(f"Performance: {performance_score}/10")
    doc.add_paragraph(f"Total Score: {total_score}/30")
    doc.add_paragraph(f"Step Range: Steps {step_range[0]} to {step_range[-1]}")
    doc.add_paragraph(f"Selected Final Step: Step {final_step}")
    doc.add_paragraph(f"Final Recommended Salary: AED {final_salary:,.2f}")

    doc.add_heading("3. Other Factors", level=1)
    doc.add_paragraph(f"Budget Flexibility: {budget_flex}")
    doc.add_paragraph(f"Candidate Expectations: {candidate_expectations}")

    doc.add_heading("4. Final Summary", level=1)
    doc.add_paragraph(summary_text)

    doc.add_heading("5. Generated On", level=1)
    doc.add_paragraph(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

word_file = generate_word_report()

st.download_button(
    label="📥 Download Word Report",
    data=word_file,
    file_name=f"{candidate_name.replace(' ', '_')}_Salary_Evaluation.docx",
    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)
