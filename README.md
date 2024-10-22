# Resume_And_Job_Description_Matching

## Overview

- The Resume Analyzer is an innovative application designed to streamline the hiring process by evaluating resumes against job descriptions. This project leverages the powerful **LLaMA3** model for advanced text extraction and analysis, enabling the identification of key skills, experience, and job titles from resumes. Additionally, regular expressions (regex) are utilized to enhance data parsing and extraction, ensuring accuracy and efficiency in capturing relevant information.

- The application provides a scoring mechanism that compares extracted resume data with the requirements specified in job descriptions, allowing recruiters to quickly assess candidate suitability. The results, including the candidate's name, mobile number, email, extracted skills, and calculated score, are stored in a database for easy retrieval and management.

- An interactive front-end powered by **Gradio** allows users to upload resumes and job descriptions, making it user-friendly and accessible for both job seekers and recruiters.

- Extracts key information from resumes using LLaMA3 and regex.
- Compares resumes against job descriptions to generate a suitability score.
- Stores candidate details in a database for effective management.
- User-friendly interface created with Gradio for seamless interaction.

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

1. host = "<Your_host>"
  
2. user = "<Your_Username>"
   
3. password = "<Your_Password>"


## Contact

For any inquiries or feedback, please reach out to Prashant Singh at prashantsingha96@gmail.com.
