import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
import openai

api_key = st.secrets.get("OPENAI_API_KEY")

client = openai.OpenAI(api_key=api_key)
col1, col2, col3 = st.columns([1, 3, 1])  
with col2:
    st.image("logo.jpg", width=350)  
    st.title("MYP Data Analysis")

option_grade = st.selectbox("Select the Grade Level",("Grade 6","Grade 7","Grade 8","Grade 9","Grade 10"))
option = st.selectbox(
    "Select the subject from the list",
    ("English L&L", "German L&L", "English LA", "German LA",
     "French LA","Spanish LA","Individuals and Societies",
     "Science","Math","Visual Arts","PHE",
     "Performing Arts","Design","Music")
)
if option == "English L&L" or option == "German L&L":
    criteria = ["A: Analysing", "B: Organizing", "C: Producing text", "D: Using language"]
elif option == "German LA" or option == "English LA" or option == "French LA" or option == "Spanish LA":
    criteria = ["A: Listening", "B: Reading", "C: Speaking", "D: Writing"]
elif option == "Math":
    criteria = ["A: Knowing and understanding", "B: Investigating patterns", "C: Communicating", "D: Applying mathematics in real-life contexts"]
elif option == "Individuals and Societies":
    criteria = ["A: Knowing and understanding", "B: Investigating", "C: Communicating", "D: Thinking critically"]
elif option == "Science":
    criteria = ["A: Knowing and understanding", "B: Inquiring and designing", "C: Processing and evaluating", "D: Reflecting on the impacts of science"]
elif option == "Design":
    criteria = ["A: Inquiring and analysing", "B: Developing ideas", "C: Creating the solution", "D: Evaluating"]
elif option == "PHE":
    criteria = ["A: Knowing and understanding", "B: Planning for performance", "C: Applying and performing", "D: Reflecting and improving performance"]
else:
    criteria = ["A: Investigating", "B: Developing", "C: Creating or performing", "D: Evaluating"]

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, header=6) 
    summary = f"Subject: {option}, Grade Level: {option_grade}\n"
    grade_distribution = {}
    for criterion in criteria:
        if criterion in df.columns:
            grade_counts = df[criterion].value_counts()
            grade_distribution_str = ', '.join([f"{index}: {count}" for index, count in grade_counts.items()])
            summary += f"\n{criterion}: {grade_distribution_str}\n"
            grade_distribution[criterion] = grade_counts
            fig, ax = plt.subplots(figsize=(5, 5))
            ax.pie(grade_counts, labels=grade_counts.index, autopct='%1.1f%%', startangle=140)
            ax.set_title(f"{option_grade} Distribution for {criterion}")
            st.pyplot(fig)
        else:
            st.warning(f"Column '{criterion}' not found in the uploaded file.")
        buf = io.BytesIO()
        fig.savefig(buf, format="png",bbox_inches="tight", pad_inches=0.5)
        buf.seek(0)
            
    
        st.download_button(
        label="Download Chart as Image",
        data=buf,
        file_name=f"{option_grade}_{criterion}.png",
        mime="image/png",
        key=f"download_{criterion}")
      
    final_column = df.iloc[:, 10]
    final_grade_counts = final_column.value_counts()
    final_grade_distribution_str = ', '.join([f"{index}: {count}" for index, count in final_grade_counts.items()])
    summary += f"\nFinal Level of Achievement: {final_grade_distribution_str}\n"
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.pie(final_grade_counts, labels=final_grade_counts.index, autopct='%1.1f%%', startangle=140)
    ax.set_title(f"{option_grade} Distribution for Final Level of achievement")
    st.pyplot(fig)
    
    buf = io.BytesIO()
    fig.savefig(buf, format="png",bbox_inches="tight", pad_inches=0.5)
    buf.seek(0)
    st.download_button(
    label="Download Chart as Image",
    data=buf,
    file_name=f"{option_grade}_{criterion}.png",
    mime="image/png",
    key="download_final"
    )
    
    #summary = f"Subject: {option}, Grade Level: {option_grade}\nCriteria: {', '.join(criteria)}\nGrade distribution: {grade_counts.to_dict()}"
    st.write(summary)
    grade_distribution_str = ""
    for criterion, grade_counts in grade_distribution.items():
        grade_distribution_str += f"\n{criterion}:\n{grade_counts.to_dict()}"
    
    action_plan_input = f"""
    ### Student Performance Data:
    Subject: {option}, Grade Level: {option_grade}
    Criteria: {', '.join(criteria)}

    Grade Distribution:
    {grade_distribution_str}

    ### Instructions:
    1. **Look at the grade distribution for each criterion**: Focus on areas where there are students performing below Grade 5 or where the majority of students are clustered at Grade 5 or below.
    2. **Criterion-Specific Action Plan**: Provide a short, specific intervention for each of the four criterion.
    3. **Teaching Strategies**: Propose specific teaching strategies to improve performance in each criterion. Tailor these strategies to the subject ({option}).
    4. **Assessment & Monitoring**: Suggest methods for assessing and tracking student progress for each criterion.
    5. **Teacher Action Steps**: Provide 3-5 specific, concrete steps teachers can take immediately to address weaknesses.
    """
    
if st.button("Generate Action Plan"):
    if summary:  
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert educator. Your task is to analyze student performance and generate a detailed, targeted action plan for improving student learning in the given subject and grade level."},
               {"role": "user", "content": action_plan_input}
        
            ],
            max_tokens=550,
            temperature=0.5
        )
        st.subheader("Action Plan")
        st.write(response.choices[0].message.content)
    else:
        st.warning("Please upload a file first before generating the action plan.")
