import streamlit as st
import pandas as pd
import altair as alt
import random
import time
from io import BytesIO
from pandas import ExcelWriter
from docx import Document
from docx.shared import Inches
import matplotlib.pyplot as plt

# --- Helper Functions ---
def mock_parse_cv_and_jd():
    return {
        "educationScore": random.choice([10, 7, 4, 2]),
        "experienceScore": random.choice([10, 7, 5, 3])
    }

def mock_parse_interview_sheet():
    return {
        "performanceScore": random.choice([10, 7, 5, 2])
    }

def get_step_interval(score):
    if score >= 25:
        return list(range(12, 16)), "Top Range"
    elif score >= 20:
        return list(range(9, 12)), "Mid-Upper Range"
    elif score >= 15:
        return list(range(6, 9)), "Mid Range"
    elif score >= 10:
        return list(range(3, 6)), "Lower-Mid Range"
    else:
        return list(range(1, 3)), "Bottom Range"

def convert_df_to_excel(df):
    output = BytesIO()
    with ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="EquityAnalysis", index=False)
    return output.getvalue()

def load_filtered_equity_data(uploaded_file, position_title_input):
    df = pd.read_excel(uploaded_file)
    df.columns = [col.strip().lower() for col in df.columns]
    required_cols = {'id', 'position title', 'hire date', 'comp rate'}
    if not required_cols.issubset(set(df.columns)):
        return None, "❌ Excel must include columns: ID, Position Title, Hire Date, Comp Rate."
    df_filtered = df[[c for c in df.columns if c in required_cols]]
    df_filtered.columns = ['id', 'positionTitle', 'hireDate', 'compRate']
    df_filtered = df_filtered[df_filtered['positionTitle'].str.lower() == position_title_input.lower()]
    return df_filtered, None

def generate_word_report(name, title, grade, education_score, experience_score, performance_score,
                          total_score, interval_options, placement, selected_step, recommended_salary,
                          final_salary, budget_threshold, budget_status, hr_comments, df_peers):
    doc = Document()
    doc.add_heading('Salary Recommendation Report', 0)

    doc.add_heading('Candidate Information', level=1)
    table = doc.add_table(rows=3, cols=2)
    table.style = 'Table Grid'
    table.cell(0, 0).text = 'Name:'
    table.cell(0, 1).text = name
    table.cell(1, 0).text = 'Position Title:'
    table.cell(1, 1).text = title
    table.cell(2, 0).text = 'Grade:'
    table.cell(2, 1).text = grade

    doc.add_heading('Scoring Summary', level=1)
    table = doc.add_table(rows=6, cols=2)
    table.style = 'Table Grid'
    table.cell(0, 0).text = 'Education Score'
    table.cell(0, 1).text = f"{education_score}/10"
    table.cell(1, 0).text = 'Experience Score'
    table.cell(1, 1).text = f"{experience_score}/10"
    table.cell(2, 0).text = 'Performance Score'
    table.cell(2, 1).text = f"{performance_score}/10"
    table.cell(3, 0).text = 'Total Score'
    table.cell(3, 1).text = f"{total_score}/30"
    table.cell(4, 0).text = 'Suggested Step Interval'
    table.cell(4, 1).text = f"{interval_options} → {placement}"
    table.cell(5, 0).text = 'Selected Step'
    table.cell(5, 1).text = str(selected_step)

    doc.add_heading('Salary Recommendation', level=1)
    table = doc.add_table(rows=4, cols=2)
    table.style = 'Table Grid'
    table.cell(0, 0).text = 'AI-Recommended Salary'
    table.cell(0, 1).text = f"AED {recommended_salary:,}"
    table.cell(1, 0).text = 'Final Recommended Salary'
    table.cell(1, 1).text = f"AED {final_salary:,}"
    table.cell(2, 0).text = 'Budget Threshold'
    table.cell(2, 1).text = f"AED {budget_threshold:,}"
    table.cell(3, 0).text = 'Budget Status'
    table.cell(3, 1).text = f"{budget_status} Budget"

    doc.add_heading('HR Comments', level=1)
    doc.add_paragraph(hr_comments)

    df_peers = pd.concat([
        df_peers,
        pd.DataFrame([{
            "id": "Final Reco.",
            "positionTitle": title,
            "hireDate": "N/A",
            "compRate": final_salary
        }])
    ], ignore_index=True)

    plt.figure(figsize=(6, 4))
    bar_colors = ['#2a5c88' if x not in ["Candidate", "Final Reco."] else '#FF8C00' for x in df_peers["id"]]
    plt.bar(df_peers["id"], df_peers["compRate"], color=bar_colors)
    plt.title("Internal Equity Compensation Comparison")
    plt.xlabel("ID")
    plt.ylabel("Compensation (AED)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    chart_path = "/mnt/data/peer_chart_final.png"
    plt.savefig(chart_path)
    plt.close()

    doc.add_heading('Internal Equity Chart', level=1)
    doc.add_picture(chart_path, width=Inches(5.5))

    doc_path = "/mnt/data/Salary_Recommendation_Report_Formatted.docx"
    doc.save(doc_path)

    return doc_path
