from shared.llm_client import call_llm
from agents.base.agent import Agent
from agents.prompts import skills_system_prompt
from agents.schemas import skills_schema

import json
import re
import spacy
import pdfplumber
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

#spaCy is the NLP used 
#please download if got error python -m spacy download en_core_web_sm
#pdfplumber is to extract structured text like pdf
nlp = spacy.load("en_core_web_sm")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Skill database used only to standardise skills in embedding
SKILL_DB = [
    # Technology / IT
    "Python", "Java", "C++", "JavaScript", "SQL",
    "Machine Learning", "Deep Learning", "Data Analysis",
    "Natural Language Processing", "Computer Vision",
    "Software Development", "Web Development",
    "Mobile App Development", "Cloud Computing",
    "DevOps", "Cybersecurity", "Database Management",
    "API Development", "System Design",

    # Data / Analytics
    "Data Visualization", "Statistical Analysis",
    "Business Intelligence", "Data Engineering",
    "Excel", "Dashboarding", "Predictive Modeling",

    # Business / Finance
    "Financial Analysis", "Accounting", "Auditing",
    "Investment Analysis", "Risk Management",
    "Budgeting", "Business Strategy", "Market Research",
    "Project Management", "Operations Management",

    # Engineering (General)
    "Mechanical Engineering", "Electrical Engineering",
    "Civil Engineering", "Chemical Engineering",
    "Structural Design", "CAD Design", "Manufacturing",
    "Quality Control", "Systems Engineering",

    # Medical / Healthcare
    "Patient Care", "Clinical Research",
    "Medical Diagnostics", "Nursing",
    "Pharmacology", "Public Health",
    "Laboratory Testing", "Healthcare Management",

    # Food and Beverage 
    "Food Preparation", "Cooking", "Culinary Arts",
    "Menu Planning", "Food Safety", "Hygiene Management",
    "Restaurant Operations", "Barista Skills",
    "Hospitality Service", "Customer Service",

    # Creative / Media
    "Graphic Design", "UI/UX Design",
    "Video Editing", "Content Creation",
    "Photography", "Copywriting", "Digital Marketing",
    "Branding", "Animation",

    # Soft Skills (Universal)
    "Communication", "Leadership", "Teamwork",
    "Problem Solving", "Critical Thinking",
    "Adaptability", "Time Management",
    "Collaboration", "Decision Making",

    # Education / Research
    "Teaching", "Curriculum Development",
    "Academic Research", "Tutoring",
    "Technical Writing", "Data Interpretation"
]

SKILL_KEYWORDS = [s.lower() for s in SKILL_DB]

def sanitize_input(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"(ignore previous instructions|system prompt)", "", text, flags=re.I)
    return text.strip()


def normalize_to_strings(items):
    """
    Forces any LLM/NLP output into clean string list.
    Prevents dict/unhashable crashes.
    """
    cleaned = []

    for x in items:
        if isinstance(x, str):
            cleaned.append(x)

        elif isinstance(x, dict):
            cleaned.append(next(iter(x.values())))

        elif isinstance(x, list):
            cleaned.extend(normalize_to_strings(x))

        else:
            cleaned.append(str(x))

    return cleaned


def parse_resume_file(file_path: str) -> str:
    text = ""
    try:
        if file_path.endswith(".pdf"):
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
        else:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
    except Exception:
        return ""

    return text


def extract_keywords_spacy(text: str):
    doc = nlp(text)
    return list(set([chunk.text.strip() for chunk in doc.noun_chunks]))


def extract_skills_rule_based(text: str):
    text_lower = text.lower()
    found = []

    for skill in SKILL_KEYWORDS:
        if skill in text_lower:
            found.append(skill.title())

    return list(set(found))


def normalize_skills(skills: list):
    if not skills:
        return []

    skill_embeddings = embedding_model.encode(SKILL_DB)
    input_embeddings = embedding_model.encode(skills)

    normalized = []

    for i, emb in enumerate(input_embeddings):
        sims = cosine_similarity([emb], skill_embeddings)[0]
        best_idx = sims.argmax()

        if sims[best_idx] > 0.6:
            normalized.append(SKILL_DB[best_idx])
        else:
            normalized.append(skills[i])

    return list(set(normalized))


class SkillsAgent(Agent):
    def __init__(self):
        super().__init__(
            name="Skills Agent",
            system_prompt=skills_system_prompt,
            schema=skills_schema
        )

    def run_interactive(self, initial_output, max_experiences=3, max_education=3):

        experiences = []
        education = []

        print(f"\n[{self.name}] Enter up to 3 key job experiences.")
        for i in range(max_experiences):
            exp = input(f"Experience {i+1}: ").strip()
            if exp:
                experiences.append(sanitize_input(exp))

        print(f"\n[{self.name}] Enter your education (at least 1).")
        while len(education) < 1:
            edu = input("Education: ").strip()
            if edu:
                education.append(sanitize_input(edu))

        resume_text = input("\nPaste resume (optional): ").strip()
        resume_text = sanitize_input(resume_text)

        if resume_text:
            parsed = self.process_resume(resume_text)
            experiences.extend(parsed.get("experiences", []))
            education.extend(parsed.get("education", []))

        return self.process_profile(experiences, education, resume_text)

    # RESUME PROCESSING
    def process_resume(self, resume_text: str):

        resume_text = sanitize_input(resume_text)
        keywords = extract_keywords_spacy(resume_text)

        prompt = f"""
Extract structured information from the resume.

Rules:
- Return JSON only
- experiences must be list of STRINGS
- education must be list of STRINGS
- inferred_skills must be list of STRINGS only

Resume:
{resume_text}

Keywords:
{keywords}

Return format:
{{
  "experiences": ["string"],
  "education": ["string"],
  "inferred_skills": ["Python"]
}}
"""

        try:
            result = call_llm(self.system_prompt, prompt, "text")
            parsed = json.loads(result)
        except Exception:
            parsed = {
                "experiences": [],
                "education": [],
                "inferred_skills": []
            }

        parsed["experiences"] = normalize_to_strings(parsed.get("experiences", []))
        parsed["education"] = normalize_to_strings(parsed.get("education", []))
        parsed["inferred_skills"] = normalize_to_strings(parsed.get("inferred_skills", []))

        return parsed

    def process_profile(self, experiences, education, resume_text):

        def safe_join(data):
            return "\n".join([str(x) for x in data if x])

        input_text = ""

        if experiences:
            input_text += "Experiences:\n" + safe_join(experiences)

        if education:
            input_text += "\nEducation:\n" + safe_join(education)

        # 1. NLP
        nlp_skills = extract_skills_rule_based(input_text + resume_text)
        nlp_skills = normalize_to_strings(nlp_skills)

        # 2. LLM
        prompt = f"""
Extract professional skills.

Rules:
- Return JSON only
- inferred_skills must be list of STRINGS only
- Each string must follow format:
  "Skill - evidence from input text"
- Evidence must be copied or closely derived from user input
- No objects or dictionaries allowed
- If there is insufficient information to extract inferred_skills, leave inferred_skills blank, just explicit skills is sufficient.
- 5-12 skills max

Input:
{input_text}

Resume:
{resume_text}

Format:
{{"inferred_skills": ["Python", "Leadership"]}}
"""

        try:
            result = call_llm(self.system_prompt, prompt, "text")
            result_json = json.loads(result)

            llm_skills = result_json.get("inferred_skills", [])
            llm_skills = normalize_to_strings(llm_skills)

        except Exception:
            llm_skills = []

        # 3. Merge
        combined = normalize_to_strings(nlp_skills + llm_skills)

        # 4. deduplicate
        seen = set()
        unique = []
        for s in combined:
            if s not in seen:
                seen.add(s)
                unique.append(s)

        # 5. Normalize embeddings
        final_skills = normalize_skills(unique)

        return {
            "experiences": experiences,
            "education": education,
            "inferred_skills": final_skills[:12],
            "existing_resume": resume_text
        }


# PROMPTFOO TEST CONFIG

PROMPTFOO_TEST_CONFIG = """
prompts:
  - "{{input}}"

providers:
  - openai:gpt-4.1-mini

tests:
  - description: Extract ML skill
    input: "Built machine learning models using Python"
    assertions:
      - type: contains
        value: "Machine Learning"

  - description: Extract leadership skill
    input: "Led a team of developers"
    assertions:
      - type: contains
        value: "Leadership"

  - description: Normalize deep learning
    input: "Worked with PyTorch and neural networks"
    assertions:
      - type: contains
        value: "Deep Learning"
"""


def save_promptfoo_config(filename="skills_promptfoo.yaml"):
    with open(filename, "w") as f:
        f.write(PROMPTFOO_TEST_CONFIG)