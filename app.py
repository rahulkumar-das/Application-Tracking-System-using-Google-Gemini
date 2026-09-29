import io
import streamlit as st
import os
import pdf2image
from google import genai
from google.genai import types


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


client = genai.Client(api_key=api_key)


def get_gemini_response(system_prompt, image_bytes, job_description):
    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=[
            system_prompt,
            types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
            job_description,
        ],
    )
    return response.text


def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        if not file_bytes:
            raise ValueError("The uploaded PDF is empty.")
        try:
            images = pdf2image.convert_from_bytes(file_bytes)
        except Exception as exc:
            raise RuntimeError("Unable to convert the uploaded PDF to image.") from exc
        if not images:
            raise ValueError("No pages were found in the uploaded PDF.")

        first_page = images[0]

        img_byte_arr = io.BytesIO()
        first_page.save(img_byte_arr, format="JPEG")
        return img_byte_arr.getvalue()
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
        try:
            pdf_content = input_pdf_setup(uploaded_file)
            response = get_gemini_response(selected_prompt, pdf_content, input_text)
        except Exception as exc:
            st.error(f"Failed to process resume with Gemini: {exc}")
        else:
            st.subheader("The response is")
            st.write(response)
