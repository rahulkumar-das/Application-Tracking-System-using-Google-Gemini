import base64
import io
from dotenv import load_dotenv
import streamlit as st
import os
import pdf2image
import google.generativeai as genai

load_dotenv()


def get_api_key():
    try:
        if "GOOGLE_API_KEY" in st.secrets:
            return st.secrets["GOOGLE_API_KEY"]
    except Exception:
        pass
    return os.getenv("GOOGLE_API_KEY")


api_key = get_api_key()
if not api_key:
    st.error(
        "Google API key not found. Configure GOOGLE_API_KEY in Streamlit secrets or environment variables."
    )
    st.stop()

genai.configure(api_key=api_key)


def get_gemini_response(system_prompt, pdf_content, job_description):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content([system_prompt, pdf_content[0], job_description])
    return response.text


def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        ## Convert the pdf to image
        images = pdf2image.convert_from_bytes(uploaded_file.read())

        first_page = images[0]

        ## Convert to bytes
        img_byte_arr = io.BytesIO()
        first_page.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()

        pdf_parts = [
            {
               "mime_type": "image/jpeg",
               "data": base64.b64encode(img_byte_arr).decode() # encode to base64 

            }
        ]
        return pdf_parts
    else:
       raise FileNotFoundError("No File uploaded")
   

## Streamlit App
st.set_page_config(page_title="Resume Matcher")
st.header("ATS Tracking System")
input_text=st.text_area("Job Description:", key="input")
uploaded_file=st.file_uploader("Upload your resume(PDF)", type=["pdf"])

if uploaded_file is not None:
    st.write("PDF Uploaded Successfully")

submit1 = st.button("Tell me about the Resume")
submit2 = st.button("How can I Improve the resume")
submit3 = st.button("What are the keywords that are missing")
submit4 = st.button("Percentage match")

input_prompt1 = """
You are an experienced Technical Human Resource Manager,your task is to review the provided resume against the job description in the
field of Data Science, Full Stack, Web Development, Data Engineer, Data Analyst. Please share your professional evaluation on whether the candidate's profile aligns with the role. 
Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
"""

input_prompt2 = """
You are an experienced Technical Human Resource Manager,your role is to scrutinize the resume in light of the job description provided. 
Please share your insights on the candidate's suitability for the role from HR's perspective. Additionally offer advice on enhancing
the candidate's skills and identify areas where it can be improved.
"""

input_prompt3 = """
You are an experienced Technical Human Resource Manager,your role is to scrutinize the resume in light of the job description provided. 
Your task is to share the keywords that are missing. Additionally offer advice on the areas where the keywords can be included.
"""

input_prompt4 = """
You are an skilled ATS (Applicant Tracking System) scanner with a deep understanding of Data Science, Full Stack, Web Development, Data Engineer, Data Analyst
and deep ATS functionality, your task is to evaluate the resume against the provided job description. give me the percentage of match if the resume matches
the job description. First the output should come as percentage and then keywords missing and last final thoughts.
"""

selected_prompt = None
if submit1:
    selected_prompt = input_prompt1
elif submit2:
    selected_prompt = input_prompt2
elif submit3:
    selected_prompt = input_prompt3
elif submit4:
    selected_prompt = input_prompt4

if selected_prompt:
    if not input_text.strip():
        st.warning("Please enter Job Description")
    elif uploaded_file is None:
        st.warning("Please upload a PDF")
    else:
        pdf_content = input_pdf_setup(uploaded_file)
        response = get_gemini_response(selected_prompt, pdf_content, input_text)
        st.subheader("The response is")
        st.write(response)
