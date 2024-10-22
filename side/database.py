import mysql.connector
import re
from difflib import SequenceMatcher
from PyPDF2 import PdfReader

def get_server_connection():
    """Establishes a connection to the MySQL server."""
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root"
    )
    return connection

def fuzzy_match(a, b):
    """Calculates the fuzzy match ratio between two strings."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def clean_text(text):
    """Cleans and normalizes extracted text."""
    text = re.sub(r'[\*\*]+', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

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

def save_extracted_info(info_text, output_file):
    """Saves the extracted information to a text file."""
    try:
        with open(output_file, 'w') as f:
            f.write(info_text)  # Save raw string info directly
        print(f"Information saved to {output_file}")
    except Exception as e:
        print(f"Error saving info: {e}")

def parse_extracted_info(text):
    """Parses the extracted information into a dictionary."""
    info = {}
    try:
        lines = text.split('\n')
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                # Clean up the key by removing leading asterisks and whitespace
                clean_key = key.strip().lstrip('*').strip()
                info[clean_key] = value.strip()
        
        print("Parsed Information:", info)  # Debugging output
        
    except Exception as e:
        print(f"Error parsing extracted info: {e}")
    return info

def create_company_db(company_name):
    """Creates a database and information table for the company."""
    sanitized_company_name = company_name.replace(" ", "_").replace("'", "''")
    
    try:
        with get_server_connection() as conn:
            conn.database = sanitized_company_name
            with conn.cursor() as cursor:
                # Use backticks to safely create the database
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{sanitized_company_name}`")
                conn.database = sanitized_company_name

                # Create the information table if it doesn't exist
                cursor.execute("""CREATE TABLE IF NOT EXISTS information (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255),
                    phone_number VARCHAR(50),
                    email VARCHAR(255),
                    skills TEXT,
                    score FLOAT
                )""")
                print(f"Database '{sanitized_company_name}' and table 'information' created or already exists.")

    except mysql.connector.Error as e:
        print(f"Error creating database or table: {e}")

def insert_resume_info(company_name, resume_info, score):
    """Inserts extracted resume info into the database."""
    sanitized_company_name = company_name.replace(" ", "_"). replace("'", "''")
    
    try:
        with get_server_connection() as conn:
            conn.database = sanitized_company_name
            with conn.cursor() as cursor:
                name = resume_info.get('Name')
                phone_number = resume_info.get('Phone Number')
                email = resume_info.get('Email')
                skills = resume_info.get('List of Skills (comma-separated)')

                if not all([name, phone_number, email, skills]):
                    print("Error: Missing required fields. Insertion aborted.")
                    return

                query = "INSERT INTO information (name, phone_number, email, skills, score) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(query, (name, phone_number, email, skills, score))
                conn.commit()
                print("Resume information inserted successfully.")

    except mysql.connector.Error as e:
        print(f"Error inserting resume info: {e}")

def extract_skills(text, type="resume"):
    """Extracts skills from text using multiple regex patterns."""
    patterns = [
        r'Skills\s*\(comma-separated\):\s*(.+)',  
        r'\*\*Skills:\*\*\s*(.+)',                
        r'\* Skills:\s*(.+)',                    
        r'Skills:\s*(.+)',                       
        r'\*\*Required Skills\*\*:\s*(.+)',       
        r'Required Skills:\s*(.+)',              
        r'\*\*Skills\*\*:\s*(.+)',               
        r'List of Skills:\s*(.+)',               
        r'List of Skills: (.+)',                  
        r'Skills:\s*(.*)\n',                      
        r'\* Skills\s*:\s*(.+)',                  
        r'Skills\s*(?:\(.+?\):)?\s*(.+)',       
        r'\*\*Skills:\*\*\s*(.+)',               
        r'\* Skills:\s*(.+)',                    
        r'Skills:\s*(.+)',                       
        r'Required Skills?:\s*(.+)',            
        r'\*\*Skills\*\*:\s*(.+)',               
        r'List of Skills:\s*(.+)',               
        r'Skills\s*(?:\(.+?\):)?\s*(.+)',       
        r'\*\*Skills:\*\*\s*(.+)',               
        r'\* Skills:\s*(.+)',                    
        r'Skills:\s*(.+)',                       
        r'Required Skills?:\s*(.+)',            
        r'\*\*Skills\*\*:\s*(.+)',               
        r'Position Titles?:\s*(.+)',           
        r'\*\*Job Title\*\*:\s*(.+)',          
        r'Position\s*(?:Held|Held\s*:\s*|Titles?)\s*:\s*(.+)', 
        r'\b(?:Work Experience|Employment History)\b\s*:\s*(.+)',  
    ]
    
    for pattern in patterns:
        skills_regex = re.search(pattern, text)
        if skills_regex:
            return [clean_text(skill.strip().lower()) for skill in skills_regex.group(1).split(',')]
    
    return []

def extract_job_titles(text, type="resume"):
    """Extracts job titles from text using multiple regex patterns."""
    patterns = [
        r'Job Titles\s*\(comma-separated\):\s*(.+)',  
        r'\*\*Job Titles:\*\*\s*(.+)',               
        r'\* Job Titles:\s*(.+)',                    
        r'Job Titles:\s*(.+)',                       
        r'\*\*Job Title\*\*:\s*(.+)',              
        r'Job Title:\s*(.+)',                        
        r'\*\*Job Titles\*\*:\s*(.+)',              
        r'List of Job Titles:\s*(.+)',              
        r'List of Job Titles\s*:\s*(.+)',           
        r'Job Titles?\s*(?:\(.+?\):)?\s*(.+)',       
        r'\*\*Job Titles:\*\*\s*(.+)',              
        r'\* Job Titles?:\s*(.+)',                  
        r'Job Titles?:\s*(.+)',                     
        r'Position Titles?:\s*(.+)',               
        r'\*\*Job Title\*\*:\s*(.+)',              
        r'Position\s*(?:Held|Held\s*:\s*|Titles?)\s*:\s*(.+)', 
        r'\b(?:Work Experience|Employment History)\b\s*:\s*(.+)',  
    ]
    
    for pattern in patterns:
        job_titles_regex = re.search(pattern, text)
        if job_titles_regex:
            return [clean_text(title.strip().lower()) for title in job_titles_regex.group(1).split(',')]
    
    return []

def extract_experience(text, type="resume"):
    """Extracts years of experience from text using multiple regex patterns."""
    patterns = [
        r'Years of Experience:\s*(\d+)',               
        r'\*\* Years of Experience:\*\*\s*(\d+)',       
        r'\* Years of Experience:\s*(\d+)',            
        r'Experience:\s*(\d+)',                        
        r'Years of Experience Required:\s*(\d+)',      
        r'\*\*Experience Required\*\*:\s*(\d+)',        
    ]
    
    for pattern in patterns:
        experience_regex = re.search(pattern, text)
        if experience_regex:
            return int(experience_regex.group(1).strip())
    
    return 0

def main():
    resume_pdf_path = "resume.pdf"  # Update with actual path
    jd_pdf_path = "jd2.pdf"  # Update with actual path

    # Extract text from PDF resumes and job descriptions
    resume_text = read_pdf(resume_pdf_path)
    jd_text = read_pdf(jd_pdf_path)

    # Extract information from resume and job description
    resume_info = extract_resume_info(resume_text)
    jd_info = extract_jd_info(jd_text)

    # Parse the extracted information into dictionaries
    resume_data = parse_extracted_info(resume_info)
    jd_data = parse_extracted_info(jd_info)

    # Create database for the company from job description
    company_name = jd_data.get('Company Name', 'DefaultCompany')
    create_company_db(company_name)

    # Extract skills and job titles
    resume_skills = extract_skills(resume_text)
    resume_job_titles = extract_job_titles(resume_text)
    jd_skills = extract_skills(jd_text, type="jd")
    jd_job_titles = extract_job_titles(jd_text, type="jd")

    # Extract years of experience
    resume_experience = extract_experience(resume_text)
    jd_experience_required = extract_experience(jd_text)

    # Calculate scores
    max_score = 1.0
    weights = {
        "skills": 0.6,
        "experience": 0.3,
        "job_title": 0.1
    }

    # Skill Matching
    total_skill_matches = set(resume_skills) & set(jd_skills)
    skill_match_ratio = len(total_skill_matches) / len(set(jd_skills)) if len(set(jd_skills)) > 0 else 0

    # Experience Matching
    experience_score = 0
    if resume_experience >= jd_experience_required:
        experience_score = 1
    elif resume_experience > 0:
        experience_score = resume_experience / jd_experience_required if jd_experience_required > 0 else 0

    # Job Title Matching
    job_title_score = 0
    for resume_title in resume_job_titles:
        for jd_title in jd_job_titles:
            if fuzzy_match(resume_title, jd_title) > 0.7:
                job_title_score = 1
                break

    # Combine scores based on weights
    final_score = (weights["skills"] * skill_match_ratio +
                   weights["experience"] * experience_score +
                   weights["job_title"] * job_title_score) * max_score

    # Insert extracted resume info into the database
    insert_resume_info(company_name, resume_data, final_score)

    print(f"Final Score for the resume: {final_score:.2f}")

if __name__ == "__main__":
    main()