from dotenv import load_dotenv
load_dotenv()
from flask import Flask, render_template, request, session
import os
import PyPDF2 as pdf
import google.generativeai as genai

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Required for session handling

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_response(input):
    model = genai.GenerativeModel('gemini-1.5-flash')  # Updated model name
    response = model.generate_content(input)
    return response.text

def input_pdf(uploaded_file):
    # Convert PDF to text
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text



@app.route("/", methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        if 'pdfInput' in request.files:
            uploaded_file = request.files['pdfInput']
            if uploaded_file.filename != '':
                text = input_pdf(uploaded_file)
                session['resume_text'] = text  # Store resume in session
                session['resume_filename'] = uploaded_file.filename  # Store filename for display

        if 'jobDescription' in request.form:
            session['job_description'] = request.form['jobDescription']  # Store JD in session

        if 'action' in request.form:
            action = request.form['action']
            text = session.get('resume_text', '')
            jd = session.get('job_description', '')
            
            if action == "percentage_match":
                prompt = f"Evaluate the resume and return the match percentage with 5-6 very small points (10 words max) on where it missed the match percentage. Resume: {text} | JD: {jd}"
            elif action == "profile_summary":
                prompt = f"Provide a detailed summary of the resume in  20 points of small sentences. Resume: {text} | JD: {jd}"
            elif action == "improve_skills":
                prompt = f"Suggest skill improvements based on the current skill and the given JD resume also provide some resources. Resume: {text} | JD: {jd}"
            elif action == "missing_keywords":
                prompt = f"Identify and return a numbered list of only the missing keywords in this resume nothing else. Resume: {text} | JD: {jd}"
            else:
                prompt = "Invalid action."

            response = get_response(prompt)
            cleaned_response = response.replace("*", "") 
            return render_template(
                "index.html",
                response=cleaned_response,
                job_description=jd,
                resume_filename=session.get('resume_filename', '')
            )

    return render_template(
        "index.html",
        job_description=session.get('job_description', ''),
        resume_filename=session.get('resume_filename', '')
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Default Render port is 10000
    app.run(host="0.0.0.0", port=port, debug=False)