import requests
import json
import os
import logging
import re
from django.conf import settings

# For reading PDF files
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

# For reading DOCX files
try:
    import docx
except ImportError:
    docx = None

logger = logging.getLogger(__name__)

def read_resume_file(file_path):
    """
    Read the content of a resume file (PDF or DOCX) and return it as a string.

    Args:
        file_path (str): Path to the resume file

    Returns:
        str: Content of the resume file as a string
    """
    file_ext = os.path.splitext(file_path)[1].lower()

    try:
        if file_ext == '.pdf':
            if PyPDF2 is None:
                logger.error("PyPDF2 is not installed. Cannot read PDF files.")
                return "Error: PyPDF2 is not installed. Cannot read PDF files."

            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text()
            return text

        elif file_ext in ['.doc', '.docx']:
            if docx is None:
                logger.error("python-docx is not installed. Cannot read DOCX files.")
                return "Error: python-docx is not installed. Cannot read DOCX files."

            doc = docx.Document(file_path)
            text = [paragraph.text for paragraph in doc.paragraphs]
            return '\n'.join(text)

        else:
            logger.error(f"Unsupported file format: {file_ext}")
            return f"Error: Unsupported file format: {file_ext}"

    except Exception as e:
        logger.error(f"Error reading resume file: {str(e)}")
        return f"Error: {str(e)}"

def call_api_with_prompt(resume_text, prompt_template):
    """
    Call the API with a specific prompt template.

    Args:
        resume_text (str): The resume text content
        prompt_template (str): The prompt template to use

    Returns:
        dict or None: The parsed API response or None if failed
    """
    try:
        # Prepare the API request
        api_endpoint = "http://localhost:11345/api/generate/"

        # Create the prompt with the resume text
        prompt = prompt_template.format(resume_text=resume_text)

        # Prepare the request payload
        payload = {
            "model": "deepseek-r1:1.5b",
            "prompt": prompt,
            "stream": False
        }

        # Make the API call
        response = requests.post(api_endpoint, json=payload)

        if response.status_code != 200:
            logger.error(f"API call failed with status code {response.status_code}: {response.text}")
            return None

        # Parse the API response
        api_response = response.json()

        # Extract the JSON from the response
        # The response contains a field 'response' which has the JSON string embedded in it
        json_str = None

        # First try to find JSON in code blocks
        json_match = re.search(r'```json\n(.+?)\n```', api_response['response'], re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find JSON object without code blocks
            json_match = re.search(r'\{.+\}', api_response['response'], re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                # Try to find JSON array without code blocks
                json_match = re.search(r'\[.+\]', api_response['response'], re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    logger.error("Could not find JSON in API response")
                    logger.error(f"API response: {api_response['response']}")
                    return None

        # Clean up the JSON string if needed
        if json_str:
            json_str = json_str.replace('```json', '').replace('```', '').strip()

        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON: {str(e)}")
            return None

    except Exception as e:
        logger.error(f"Error calling API: {str(e)}")
        return None

def extract_skills(resume_text):
    """
    Extract skills from the resume text.

    Args:
        resume_text (str): The resume text content

    Returns:
        str: Comma-separated list of skills
    """
    prompt_template = """Extract all professional skills from the resume below. Return ONLY a JSON array of strings, with each string being a single skill. Do not include any explanations or other text.

Resume:
{resume_text}

Output format example:
```json
["Python", "JavaScript", "Project Management"]
```"""

    result = call_api_with_prompt(resume_text, prompt_template)
    if not result or not isinstance(result, list):
        return ""

    # Join the skills into a comma-separated string
    return ", ".join([str(skill).strip() for skill in result if skill])

def extract_education(resume_text):
    """
    Extract education information from the resume text.

    Args:
        resume_text (str): The resume text content

    Returns:
        str: Newline-separated list of education entries
    """
    prompt_template = """Extract all education information from the resume below. Return ONLY a JSON array of strings, with each string representing one education entry (degree, institution, year, etc.). Do not include any explanations or other text.

Resume:
{resume_text}

Output format example:
```json
["Bachelor of Science in Computer Science, Stanford University, 2018-2022", "High School Diploma, Lincoln High School, 2014-2018"]
```"""

    result = call_api_with_prompt(resume_text, prompt_template)
    if not result or not isinstance(result, list):
        return ""

    # Join the education entries into a newline-separated string
    return "\n".join([str(edu).strip() for edu in result if edu])

def extract_experience(resume_text):
    """
    Extract experience information from the resume text.

    Args:
        resume_text (str): The resume text content

    Returns:
        list: List of experience entries
    """
    prompt_template = """Extract all work experience information from the resume below. Return ONLY a JSON array of strings, with each string representing one job or role (title, company, dates, etc.). Include the start and end years for each position. Do not include any explanations or other text.

Resume:
{resume_text}

Output format example:
```json
["Software Engineer, Google, 2020-2022", "Intern, Microsoft, 2019-2020"]
```"""

    result = call_api_with_prompt(resume_text, prompt_template)
    if not result or not isinstance(result, list):
        return []

    # Return the list of experience entries
    return [str(exp).strip() for exp in result if exp]

def extract_location(resume_text):
    """
    Extract location information from the resume text.

    Args:
        resume_text (str): The resume text content

    Returns:
        str: Comma-separated list of locations
    """
    prompt_template = """Extract all location information (cities, states, countries) from the resume below. Return ONLY a JSON array of strings, with each string being a single location. Do not include any explanations or other text.

Resume:
{resume_text}

Output format example:
```json
["San Francisco, CA", "New York, NY"]
```"""

    result = call_api_with_prompt(resume_text, prompt_template)
    if not result or not isinstance(result, list):
        return ""

    # Join the locations into a comma-separated string
    return ", ".join([str(loc).strip() for loc in result if loc])

def extract_resume_data_from_api(resume_file_path):
    """
    Call an external API to extract data from a resume file.

    Args:
        resume_file_path (str): Path to the resume file

    Returns:
        dict: Extracted data with keys 'skills', 'education', 'experience_years', 'location'
        or None if extraction failed
    """
    try:
        # Get the absolute file path
        abs_file_path = os.path.join(settings.MEDIA_ROOT, resume_file_path)

        # Check if file exists
        if not os.path.exists(abs_file_path):
            logger.error(f"Resume file not found at {abs_file_path}")
            return None

        # Read the resume file content
        resume_text = read_resume_file(abs_file_path)
        if resume_text.startswith("Error:"):
            logger.error(resume_text)
            return None

        # Extract each field separately
        skills = extract_skills(resume_text)
        education = extract_education(resume_text)
        experience_entries = extract_experience(resume_text)
        location = extract_location(resume_text)

        # Calculate experience years
        experience_years = estimate_experience_years(experience_entries)

        # Combine the results
        processed_data = {
            'skills': skills,
            'education': education,
            'experience_years': experience_years,
            'location': location
        }

        return processed_data

    except Exception as e:
        logger.error(f"Error extracting resume data: {str(e)}")
        return None

def estimate_experience_years(experience_entries):
    """
    Estimate the total years of experience from the experience entries.
    This is a simple implementation that looks for year ranges in the experience entries.

    Args:
        experience_entries (list): List of experience entries

    Returns:
        float: Estimated years of experience
    """
    try:
        total_years = 0.0

        for entry in experience_entries:
            # Look for year ranges like "2018 - 2020" or "2018–2020"
            year_matches = re.findall(r'(\d{4})\s*[–-]\s*(\d{4}|present|current|now)', entry.lower())

            for start_year, end_year in year_matches:
                start = int(start_year)

                if end_year in ['present', 'current', 'now']:
                    # Use current year for 'present'
                    from datetime import datetime
                    end = datetime.now().year
                else:
                    end = int(end_year)

                # Add the duration to the total
                total_years += (end - start)

        # If we couldn't extract any years, return a default value
        if total_years == 0:
            return 2.0  # Default value

        return total_years

    except Exception as e:
        logger.error(f"Error estimating experience years: {str(e)}")
        return 2.0  # Default value

def analyze_resume_job_match(resume_text, job_description):
    """
    Analyze the match between a resume and a job description using AI.

    Args:
        resume_text (str): The resume text content
        job_description (str): The job description text

    Returns:
        dict: Analysis results with match score and insights
    """
    try:
        # Prepare the API request
        api_endpoint = "http://localhost:11345/api/generate/"

        # Create the prompt for the analysis
        prompt = f"""Analyze the match between the candidate's resume and the job description below.
        Return a JSON object with the following fields:
        1. match_score: A number between 0 and 100 representing how well the candidate matches the job requirements
        2. matching_skills: An array of skills from the resume that match the job requirements
        3. missing_skills: An array of important skills from the job description that are not found in the resume
        4. experience_match: A brief analysis of how well the candidate's experience matches the job requirements
        5. education_match: A brief analysis of how well the candidate's education matches the job requirements
        6. overall_assessment: A brief overall assessment of the candidate's fit for the position
        7. improvement_suggestions: Suggestions for how the candidate could improve their match for this position

Resume:
{resume_text}

Job Description:
{job_description}

Return the entire output as a valid JSON object."""

        # Prepare the request payload
        payload = {
            "model": "deepseek-r1:1.5b",
            "prompt": prompt,
            "stream": False
        }

        # Make the API call
        response = requests.post(api_endpoint, json=payload)

        if response.status_code != 200:
            logger.error(f"API call failed with status code {response.status_code}: {response.text}")
            return None

        # Parse the API response
        api_response = response.json()

        # Extract the JSON from the response
        json_match = re.search(r'```json\n(.+?)\n```', api_response['response'], re.DOTALL)
        if not json_match:
            # Try to find JSON object without code blocks
            json_match = re.search(r'\{.+\}', api_response['response'], re.DOTALL)
            if not json_match:
                logger.error("Could not find JSON in API response")
                logger.error(f"API response: {api_response['response']}")
                return None

        json_str = json_match.group(0).replace('```json', '').replace('```', '').strip()

        try:
            analysis_result = json.loads(json_str)
            return analysis_result
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON: {str(e)}")
            logger.error(f"Problematic JSON string: {json_str}")

            # Try to clean up the string and parse it again
            try:
                # Replace single quotes with double quotes
                cleaned_str = json_str.replace("'", '"')
                # Remove newline characters and extra spaces
                cleaned_str = re.sub(r'\s*\n\s*', '', cleaned_str)
                # Fix common JSON formatting issues
                cleaned_str = cleaned_str.replace('\\n', '')

                logger.info(f"Attempting to parse cleaned JSON string: {cleaned_str}")
                return json.loads(cleaned_str)
            except json.JSONDecodeError as e2:
                logger.error(f"Error parsing cleaned JSON: {str(e2)}")
                return None

    except Exception as e:
        logger.error(f"Error analyzing resume-job match: {str(e)}")
        return None
