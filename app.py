import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
import openai

api_key = st.secrets.get("OPENAI_API_KEY")

# Debugging: Check if API key is retrieved (Remove this after testing)
st.write(f"🔍 Debug: API Key Found? {bool(api_key)}")
st.write(f"🔍 Debug: API Key Value: {api_key}")  # 🔴 Remove this after confirming!

if not api_key:
    st.error("❌ API key not found. Please add it to Streamlit Cloud secrets.")

# Initialize OpenAI client
client = openai.OpenAI(api_key=api_key)
col1, col2, col3 = st.columns([1, 3, 1])  # Middle column is twice as big
with col2:
    st.image("logo.jpg", width=350)  # Centered Image
    st.title("MYP Data Analysis")


# File uploader
option_grade = st.selectbox("Select the Grade Level",("Grade 6","Grade 7","Grade 8","Grade 9","Grade 10"))
option = st.selectbox(
    "Select the subject from the list",
    ("English L&L", "German L&L", "English LA", "German LA",
     "French LA","Spanish LA","Individuals and Societies",
     "Science","Math","Visual Arts","PHE",
     "Performing Arts","Design","Music")
)
if option == "English L&L" or option == "German L&L":
    criteria = ["A: Analysing", "B: Organizing", "C: Producing text", "D: Using language","final"]
elif option == "German LA" or option == "English LA" or option == "French LA" or option == "Spanish LA":
    criteria = ["A: Listening", "B: Reading", "C: Speaking", "D: Writing","final"]
elif option == "Math":
    criteria = ["A: Knowing and understanding", "B: Investigating patterns", "C: Communicating", "D: Applying mathematics in real-life contexts","final"]
elif option == "Individuals and Societies":
    criteria = ["A: Knowing and understanding", "B: Investigating", "C: Communicating", "D: Thinking critically","final"]
elif option == "Science":
    criteria = ["A: Knowing and understanding", "B: Inquiring and designing", "C: Processing and evaluating", "D: Reflecting on the impacts of science","final"]
elif option == "Design":
    criteria = ["A: Inquiring and analysing", "B: Developing ideas", "C: Creating the solution", "D: Evaluating","final"]
elif option == "PHE":
    criteria = ["A: Knowing and understanding", "B: Planning for performance", "C: Applying and performing", "D: Reflecting and improving performance","final"]
else:
    criteria = ["A: Investigating", "B: Developing", "C: Creating or performing", "D: Evaluating","final"]

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])
summary = ""
if uploaded_file:
    df = pd.read_excel(uploaded_file)   
    for criterion in criteria:
        if criterion in df.columns:
            grade_counts = df[criterion].value_counts()

            fig, ax = plt.subplots(figsize=(5, 5))
            ax.pie(grade_counts, labels=grade_counts.index, autopct='%1.1f%%', startangle=140)
            if criterion == "final":
                ax.set_title(f"{option_grade} Distribution for Final Level of achievement")
            else:
                ax.set_title(f"{option_grade} Distribution for {criterion}")
            
            buf = io.BytesIO()
            fig.savefig(buf, format="png",bbox_inches="tight", pad_inches=0.5)
            buf.seek(0)
            
            st.pyplot(fig)
            st.download_button(
            label="Download Chart as Image",
            data=buf,
            file_name=f"{option_grade}_{criterion}.png",
            mime="image/png"
        )
            summary = f"Grade distribution: {grade_counts.to_dict()}"
   
        else:
            st.warning(f"Column '{criterion}' not found in the uploaded file.")
    
if st.button("Generate Action Plan"):
    if summary:  # Ensure summary is available
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert math educator. Your task is to analyze student performance and generate a detailed, targeted action plan for improving Grade 7 Math."},
                {"role": "user", "content": f"""
Here is the grade distribution for Grade 7 Math:
{summary}

Please provide a **specific and data-driven action plan**, including:
1. **Compare Criteria:** Identify which criteria students struggle with the most. Use the names of the exact criterion. 
2. **Highlight Trends:** Identify whether foundational skills (e.g., 'Knowing and Understanding') are weaker than applied skills (e.g., 'Investigating Patterns').
3. **Actionable Strategies:** Give specific strategies per weak area. Give specific examples that teachers could implement. 
4. **Final Summary:** Provide a holistic analysis of whether overall trends align with individual criteria challenges.
"""}
            ],
            max_tokens=350,
            temperature=0.5
        )
        st.subheader("Action Plan")
        st.write(response.choices[0].message.content)
    else:
        st.warning("Please upload a file first before generating the action plan.")


