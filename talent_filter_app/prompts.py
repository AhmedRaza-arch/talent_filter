"""
This file contains all prompt templates used for AI interactions in the Talent Filter application.
"""

# Prompt for generating AI recommendations for recruiters
RECRUITER_RECOMMENDATIONS_PROMPT = """Generate AI recommendations for job candidates that match the given job description.
Analyze the job requirements and the candidate profiles to find the best matches.

Job Description:
{job_description}

Candidate Profiles:
{candidate_profiles}

Return a JSON object with the following fields:
1. recommendations: An array of candidate recommendations, each containing:
   a. candidate_id: The ID of the candidate
   b. match_score: A number between 0 and 100 representing how well the candidate matches the job
   c. matching_skills: An array of skills from the candidate that match the job requirements
   d. missing_skills: An array of important skills from the job that the candidate doesn't have
   e. experience_match: A brief analysis of how well the candidate's experience matches the job requirements
   f. education_match: A brief analysis of how well the candidate's education matches the job requirements
   g. overall_assessment: A brief overall assessment of why this candidate would be a good fit
   h. contact_recommendation: A brief suggestion on how to approach this candidate

Analyze each match carefully, considering both explicit skills and implicit qualifications.
Return the entire output as a valid JSON object."""

# Prompt for extracting skills from a resume
SKILLS_EXTRACTION_PROMPT = """Extract all professional skills from the resume below. Return ONLY a JSON array of strings, with each string being a single skill. Do not include any explanations or other text.

Resume:
{resume_text}

Output format example:
```json
["Python", "JavaScript", "Project Management"]
```"""

# Prompt for extracting education information from a resume
EDUCATION_EXTRACTION_PROMPT = """Extract all education information from the resume below. Return ONLY a JSON array of strings, with each string representing one education entry (degree, institution, year, etc.). Do not include any explanations or other text.

Resume:
{resume_text}

Output format example:
```json
["Bachelor of Science in Computer Science, Stanford University, 2018-2022", "High School Diploma, Lincoln High School, 2014-2018"]
```"""

# Prompt for extracting work experience information from a resume
EXPERIENCE_EXTRACTION_PROMPT = """Extract all work experience information from the resume below. Return ONLY a JSON array of strings, with each string representing one job or role (title, company, dates, etc.). Include the start and end years for each position. Do not include any explanations or other text.

Resume:
{resume_text}

Output format example:
```json
["Software Engineer, Google, 2020-2022", "Intern, Microsoft, 2019-2020"]
```"""

# Prompt for extracting location information from a resume
LOCATION_EXTRACTION_PROMPT = """Extract all location information (cities, states, countries) from the resume below. Return ONLY a JSON array of strings, with each string being a single location. Do not include any explanations or other text.

Resume:
{resume_text}

Output format example:
```json
["San Francisco, CA", "New York, NY"]
```"""

# Prompt for analyzing the match between a resume and a job description
RESUME_JOB_MATCH_PROMPT = """Analyze the match between the candidate's resume summary and the job description below.
The resume summary contains the key information extracted from the candidate's full resume.

Return a JSON object with the following fields:
1. match_score: A number between 0 and 100 representing how well the candidate matches the job requirements
2. matching_skills: An array of skills from the resume that match the job requirements
3. missing_skills: An array of important skills from the job description that are not found in the resume
4. experience_match: A brief analysis of how well the candidate's experience matches the job requirements
5. education_match: A brief analysis of how well the candidate's education matches the job requirements
6. overall_assessment: A brief overall assessment of the candidate's fit for the position
7. improvement_suggestions: Suggestions for how the candidate could improve their match for this position

Resume Summary:
{resume_text}

Job Description:
{job_description}

Analyze the match carefully, considering both the explicit skills and implicit qualifications.
Return the entire output as a valid JSON object."""
