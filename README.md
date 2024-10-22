# Resume_And_Job_Description_Matching

## Overview

The Resume Analyzer is a machine learning-based tool that evaluates resumes against job descriptions (JDs). By comparing skills, experience, and job titles, it provides a score that reflects how well a resume matches a given job description. The project is integrated with a database to store relevant candidate details, making it easy to track and analyze applicant data.

## Features

- **Resume Evaluation**: Compares resumes with job descriptions to calculate a matching score based on extracted skills, experience, and job titles.
- **Database Integration**: Stores candidate details, including name, mobile number, email, extracted skills, and score.
- **Interactive Interface**: Built using Gradio for a user-friendly experience.

## Technologies Used

- Python
- Gradio
- PyMysql
- Large Language Model - llama3
- PyPDF2 - to read pdfs

## Installation

To set up the project on your local machine, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/resume-analyzer.git
   ```

2. Navigate to the project directory:
   ```bash
   cd resume-analyzer
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Pull the LLaMA model:
   ```bash
   ollama pull llama
   ```

## Usage

1. **Start the Gradio Interface**:
   Run the main script to start the Gradio interface:
   ```bash
   python main.py
   ```

2. **Upload Resumes**: 
   Use the interface to upload a resume and a job description.

3. **View Results**: 
   The analyzer will calculate the matching score and display extracted skills and details in the interface.

## Database Setup

Make sure to change them :

1. host = <Your host>
  
2. user = <Your Username>
   
3. password = <Your Password>


## Contact

For any inquiries or feedback, please reach out to Prashant Singh at prashantsingha96@gmail.com.
