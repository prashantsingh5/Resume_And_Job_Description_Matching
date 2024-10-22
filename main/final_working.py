from langchain_community.llms import Ollama
MODEL = "llama3"
model = Ollama(model=MODEL)
import re
from PyPDF2 import PdfReader
import gradio as gr

# Step 1: Extract text from PDF using PyPDF2
def read_pdf(file):
    """Reads the PDF and extracts text from it."""
    try:
        reader = PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ''

# Step 2: Function to extract information from resumes using LLaMA
def extract_resume_info(resume_text):
    """Extracts specific details from resume text using LLaMA."""
    prompt = f"""
    Extract the following information from this resume:
    - Name
    - Email
    - Phone Number
    - List of Job Titles (in a comma-separated format)
    - List of Skills (in a comma-separated format)
    - Years of Experience (in numbers, no text, just the number of years)
    - List of Companies worked with (in a comma-separated format)

    Please ensure that the 'Years of Experience' includes only professional job or internship experience, not education experience.

    Here is the resume:
    {resume_text}
    """
    try:
        # Get the response from the LLaMA model
        response = model.invoke(prompt)
        return response.strip()  # Returning raw string response
    except Exception as e:
        print(f"Error in extracting resume info: {e}")
        return ''


# Step 3: Extract job description info using LLaMA
def extract_jd_info(jd_text):
    """Extracts specific details from a job description using LLaMA."""
    prompt = f"""
    Extract the following information from this job description:
    - Company Name
    - Email
    - Phone Number
    - Job Title (in a comma-separated format)
    - List of Required Skills (in a comma-separated format)
    - Years of Experience required (in numbers, no text, just the number of years)

    Here is the job description:
    {jd_text}
    """
    try:
        # Get the response from the LLaMA model
        response = model.invoke(prompt)
        return response.strip()  # Returning raw string response
    except Exception as e:
        print(f"Error in extracting JD info: {e}")
        return ''


# Step 4: Function to save extracted information to a .txt file
def save_extracted_info(info_text, output_file):
    """Saves the extracted information to a text file."""
    try:
        with open(output_file, 'w') as f:
            f.write(info_text)  # Save raw string info directly
        print(f"Information saved to {output_file}")
    except Exception as e:
        print(f"Error saving info: {e}")


# Step 5: Helper function to parse the extracted information from text to dictionary
def parse_extracted_info(text):
    """Parses the extracted information into a dictionary."""
    info = {}
    try:
        # Simple parsing by splitting lines and using key-value pairs
        lines = text.split('\n')
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                info[key.strip()] = value.strip()
    except Exception as e:
        print(f"Error parsing extracted info: {e}")
    return info


import pymysql
import re
from difflib import SequenceMatcher
from PyPDF2 import PdfReader

# MySQL connection (without specifying a database)
def get_server_connection():
    connection = pymysql.connect(
        host="localhost",
        user="root",
        password="root",
        cursorclass=pymysql.cursors.DictCursor  # DictCursor to get results as dictionaries
    )
    return connection

# Helper function for fuzzy matching
def fuzzy_match(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

# Helper function to clean and normalize extracted text
def clean_text(text):
    text = re.sub(r'[\\]+', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# Step 1: Extract text from PDF using PyPDF2
def read_pdf(file):
    """Reads the PDF and extracts text from it."""
    try:
        reader = PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ''

# Step 2: Enhanced extraction using multiple regex patterns
def extract_info_from_text(text, info_type="resume"):
    """Extracts specific details from the given text using multiple regex patterns."""

    # Helper function for extracting and cleaning text based on patterns
    def extract_field(text, patterns):
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return clean_text(match.group(1))
        return None

    # Defining patterns for each field based on the type (resume or job description)
    if info_type == "resume":
        name_patterns = [
            r'Name:\s*(.+)',  # New pattern for "Name:"
            r'\\*Name\\:\s*(.+)',
            r'Full Name:\s*(.+)',
            r'\*\*Name:\*\*\s*(.+)',  # Pattern for **Name:** format
            r'\bName\b\s*:\s*(.+)'  
        ]
        email_patterns = [
            r'Email:\s*([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)',
            r'\*\*Email:\*\*\s*([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)',  # New pattern for **Email:** format
            r'\b(?:E-mail|Email)\b\s*:\s*([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)'
        ]
        phone_patterns = [
            r'Phone Number:\s*(\+?\d[\d\s-]+)',
            r'\*\*Phone Number:\*\*\s*(\+?\d[\d\s-]+)',  # New pattern for **Phone Number:** format
            r'Contact Number:\s*(\+?\d[\d\s-]+)',
            r'\b(?:Phone|Telephone|Contact)\b\s*:\s*(\+?\d[\d\s-]+)'
        ]
        company_patterns = [
            r'Companies worked with:\s*(.+)',  # Pattern for "Companies worked with:"
            r'\*\*Companies worked with:\*\*\s*(.+)'  # Pattern for **Companies worked with:** format
        ]

    elif info_type == "jd":
        name_patterns = [
            r'Company Name:\s*(.+)',
            r'\b(?:Organization|Employer)\b\s*:\s*(.+)'
        ]
        email_patterns = [
            r'Email:\s*([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)',
            r'\b(?:E-mail|Email)\b\s*:\s*([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)'
        ]
        phone_patterns = [
            r'Phone Number:\s*(\+?\d[\d\s-]+)',
            r'Contact Number:\s*(\+?\d[\d\s-]+)',
            r'\b(?:Phone|Telephone|Contact)\b\s*:\s*(\+?\d[\d\s-]+)'
        ]

    # Extract the relevant fields using the patterns
    extracted_info = {
        'Name': extract_field(text, name_patterns),
        'Email': extract_field(text, email_patterns),
        'Phone Number': extract_field(text, phone_patterns),
        'Job Titles': ', '.join(extract_job_titles(text)),  # Use updated extract_job_titles function
        'Skills': ', '.join(extract_skills(text)),  # Use updated extract_skills function
        'Years of Experience': extract_experience(text),  # Use updated extract_experience function
    }

    return extracted_info

# Enhanced pattern-matching functions

def extract_skills(text):
    patterns = [
        r'Skills\s*\(comma-separated\):\s*(.+)',
        r'\*\*Skills:\*\*\s*(.+)',  # Pattern for **Skills:** format
        r'\\*Skills\\:\s(.+)',
        r'\* Skills:\s*(.+)',
        r'Skills:\s*(.+)',
        r'\\*Required Skills\\:\s(.+)',
        r'Required Skills:\s*(.+)',
        r'List of Skills:\s*(.+)',
        r'\bSkills\b\s*:\s*(.+)'
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return [clean_text(skill.strip().lower()) for skill in match.group(1).split(',')]
    return []

def extract_job_titles(text):
    patterns = [
        r'Job Titles\s*\(comma-separated\):\s*(.+)',
        r'\*\*Job Titles:\*\*\s*(.+)',  # Pattern for **Job Titles:** format
        r'\\*Job Titles\\:\s(.+)',
        r'\* Job Titles:\s*(.+)',
        r'Job Titles:\s*(.+)',
        r'\\*Job Title\\:\s(.+)',
        r'Job Title:\s*(.+)',
        r'List of Job Titles:\s*(.+)',
        r'\b(?:Positions|Roles)\b\s*:\s*(.+)'
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return [clean_text(title.strip().lower()) for title in match.group(1).split(',')]
    return []

def extract_experience(text):
    patterns = [
        r'Years of Experience:\s*(\d+)',
        r'\*\*Years of Experience:\*\*\s*(\d+)',  # Pattern for **Years of Experience:** format
        r'Experience required:\s*(\d+)',
        r'\* Years of Experience:\s*(\d+)',
        r'\d+\s*years? experience(?: required)?',
        r'\b(?:Experience|Professional Experience)\b\s*:\s*(\d+)'
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return int(match.group(1))
    return 0

# Step 3: Function to create a database and information table
def create_company_db(company_name):
    conn = get_server_connection()
    cursor = conn.cursor()
    try:
        # Create the database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{company_name}`")
        conn.commit()

        # Select the created database
        conn.select_db(company_name)

        # Create the information table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS information (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255),
                phone_number VARCHAR(20),
                email VARCHAR(255),
                skills TEXT,
                score FLOAT
            )
        """)
        conn.commit()
    except Exception as e:
        print(f"Error creating database/table: {e}")
    finally:
        cursor.close()
        conn.close()

# Step 4: Function to insert extracted resume info into the table
def insert_resume_info(company_name, resume_info, score):
    conn = get_server_connection()
    cursor = conn.cursor()
    try:
        # Select the database
        conn.select_db(company_name)

        # Insert into the database
        query = "INSERT INTO information (name, phone_number, email, skills, score) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (resume_info.get('Name'), resume_info.get('Phone Number'), resume_info.get('Email'), resume_info.get('Skills'), score))
        conn.commit()

    except Exception as e:
        print(f"Error inserting resume info into the database: {e}")
    finally:
        cursor.close()
        conn.close()

# Step 5: Function to calculate the resume score based on matching criteria
def calculate_resume_score(resume_info, jd_info):
    """Calculate the resume score based on skills, experience, and job title matches."""
    score = 0
    max_score = 100
    weights = {
        "skills": 0.6,
        "experience": 0.2,
        "job_title": 0.2
    }

    # Extracted details from the resume and job description
    resume_skills = set(resume_info.get('Skills', '').split(', '))
    jd_skills = set(jd_info.get('Required Skills', '').split(', '))

    # Skill matching (exact and partial match)
    exact_skill_matches = resume_skills.intersection(jd_skills)
    partial_skill_matches = set()

    # Fuzzy matching for partial skill matches
    for resume_skill in resume_skills:
        for jd_skill in jd_skills:
            if fuzzy_match(resume_skill, jd_skill) > 0.55:  # Fuzzy match threshold
                partial_skill_matches.add(resume_skill)

    # Combine exact and partial matches
    total_skill_matches = exact_skill_matches.union(partial_skill_matches)
    skill_match_ratio = len(total_skill_matches) / len(jd_skills) if jd_skills else 0
    skill_score = skill_match_ratio * weights['skills'] * max_score
    score += skill_score

    # Experience matching
    resume_experience = int(resume_info.get('Years of Experience', 0))
    jd_experience_required = int(jd_info.get('Years of Experience', 0))
    experience_match_ratio = resume_experience / jd_experience_required if jd_experience_required else 0
    experience_score = experience_match_ratio * weights['experience'] * max_score
    score += experience_score

    # Job title matching
    resume_job_titles = set(resume_info.get('Job Titles', '').split(', '))
    jd_job_titles = set(jd_info.get('Job Titles', '').split(', '))
    best_title_match = max([fuzzy_match(rjt, jjt) for rjt in resume_job_titles for jjt in jd_job_titles], default=0)
    job_title_score = best_title_match * weights['job_title'] * max_score if best_title_match > 0.7 else 0
    score += job_title_score

    return round(score, 2)

# Step 6: Example usage of the functions
def process_resume(resume_pdf, jd_pdf):
# Define the PDF file paths
    resume_pdf_path = resume_pdf
    jd_pdf_path = jd_pdf

    # Extract text from the resume and job description PDFs
    resume_text = read_pdf(resume_pdf_path)
    jd_text = read_pdf(jd_pdf_path)

    resume_info_raw = extract_resume_info(resume_text)
    jd_info_raw = extract_jd_info(jd_text)

    # Parse the raw extracted information into dictionaries (optional for verification)
    resume_info = parse_extracted_info(resume_info_raw)
    jd_info = parse_extracted_info(jd_info_raw)

    # Step 7: Save extracted resume and JD information to .txt files
    save_extracted_info(resume_info_raw, 'extracted_resume_info.txt')
    save_extracted_info(jd_info_raw, 'extracted_jd_info.txt')

    # Define the file paths
    resume_info_file = 'extracted_resume_info.txt'
    jd_info_file = 'extracted_jd_info.txt'

    # Read the extracted text from the files
    resume_info_text = read_file(resume_info_file)
    jd_info_text = read_file(jd_info_file)

    if resume_info_text and jd_info_text:
        # Extract structured information from both the resume and the job description
        resume_info = extract_info_from_text(resume_info_text, info_type="resume")
        jd_info = extract_info_from_text(jd_info_text, info_type="jd")

        # Debugging output
        print("Extracted Resume Info:", resume_info)
        print("Extracted JD Info:", jd_info)

        # Create a database based on the company name
        company_name = jd_info.get('Company Name', 'default_company').replace(' ', '_')
        create_company_db(company_name)

        # Calculate resume score
        score = calculate_resume_score(resume_info, jd_info)

        # Insert resume info into the database
        insert_resume_info(company_name, resume_info, score)

        return f"Resume processed and stored in database '{company_name}' with score {score}"
    else:
        print("Error: Failed to process resume or job description.")

# Function to read the contents of a file
def read_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

# Gradio interface
gr.Interface(
    fn=process_resume,
    inputs=["file", "file"],
    outputs="text",
    title="Resume Scoring",
    description="Upload a resume and a job description to calculate the resume score."
).launch()
