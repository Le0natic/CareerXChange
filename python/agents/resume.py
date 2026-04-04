from shared.llm_client import call_llm
from agents.base.agent import Agent
from agents.prompts import resume_system_prompt
from agents.schemas import resume_schema
import json

class ResumeAgent(Agent):
    def __init__(self):
        super().__init__(
            name = "Resume Agent",
            system_prompt = resume_system_prompt,
            schema = resume_schema
        )

    def run_interactive(self, initial_output):
        context = initial_output
        print(f"\n[{self.name}] Generating resume...")
        return self.generate_resume(context)
    
    def generate_resume(self, context):
        prompt = f"""
Generate a resume based on:

Initial context:
{context}

Instructions:
Return results in JSON.
If there is insufficient information, return:
{{
    "header": {{}},
    "professional_summary": "Insufficient information to generate resume",
    "skills": "",
    "work_experience": [],
    "projects": "",
    "education": [],
    "additional_sections": {{}}
}}

Return JSON in following format:
{{
    "header": {{
        "name": "...",
        "contact_info": {{
            "email": "...",
            "phone": "...
        }}
    }}
    "professional_summary": "...",
    "skills": "...",
    "work_experience": [
        {{
            "job_title": "...",
            "company": "...",
            "start_employment_date": "...",
            "end_employment_date": "..."
        }},
        {{
            "job_title": "...",
            "company": "...",
            "start_employment_date": "...",
            "end_employment_date": "..."
        }}
    ],
    "projects": "...",
    "education": [
        {{
            "qualification": "...",
            "institution": "...",
            "graduation_date": "...",
            "gpa": "..."
        }},
        {{
            "qualification": "...",
            "institution": "...",
            "graduation_date": "...",
            "gpa": "..."
        }}
    ],
    "additional_sections": {{
        "certifications": "...",
        "awards": "...",
        "publications": "..."
    }}
}}

IMPORTANT:
- Return ONLY valid JSON (no single quotes, strictly double quotes for keys and values).
- No explanation.
- Follow schema strictly.
"""
        result_str = call_llm(resume_system_prompt, prompt, "text")
        try:
            return json.loads(result_str)
        except json.JSONDecodeError:
            return {"header": {}, "professional_summary": "JSONDecodeError", "skills": "", "work_experience": [], "projects": "", "education": [], "additional_sections": {}}
