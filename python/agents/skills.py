from shared.llm_client import call_llm
from agents.base.agent import Agent
from agents.prompts import skills_system_prompt
from agents.schemas import skills_schema
import json

class SkillsAgent(Agent):
    def __init__(self):
        super().__init__(
            name = "Skills Agent",
            system_prompt = skills_system_prompt,
            schema = skills_schema
        )

    # Step 1: Start interactive run.
    def run_interactive(self, initial_output, max_experiences = 3,max_education=3):
        context = initial_output
        experiences = []
        education = []

        #Job experience
        print(f"\n[{self.name}] Now, please describe maximum 3 main job experiences you have had that you think is most impactful or memorable.")
        print(f"[{self.name}] (Press Enter to skip if you have no more job experience to share.)")

        for i in range(1, max_experiences + 1):
            print(f"\n[{self.name}] Experience {i}:")
            user_input = input("Your answer (press Enter to skip): ").strip()

            if not user_input:
                print(f"\n[{self.name}] No input provided. Skipping...")
                continue

            print(f"\n[{self.name}] Noted. Recording your experience...")
            experiences.append(user_input)

        if len(experiences) == 0:
            print(f"\n[{self.name}] No job experience detected. Proceeding with this information...")
        else:
            print(f"\n[{self.name}] {len(experiences)} experience(s) recorded. Processing...")

        #Education History
        print(f"\n[{self.name}] Now, please describe your top 3 educational experience (e.g., degree, diploma, certifications). Provide at least 1 educational experience.")
        print(f"[{self.name}] (Example: Bachelor's in Computer Science, NUS, 2020–2024)")

        edu_count = 0
        while edu_count < 1 or edu_count < max_education:
            print(f"\n[{self.name}] Education {edu_count + 1}:")
            user_input = input("Your answer: ").strip()

            if not user_input:
                if edu_count < 1:
                    print(f"[{self.name}] You must provide at least 1 education record.")
                    continue
                else:
                    print(f"[{self.name}] Skipped remaining entries.")
                    break

            print(f"[{self.name}] Noted. Recording your education...")
            education.append(user_input)
            edu_count += 1

            if edu_count >= max_education:
                break

        print(f"\n[{self.name}] {len(education)} education record(s) recorded. Processing all inputs...")

        #Resume
        resume_text = input(f"\n[{self.name}] Do you have an existing resume you want to provide for our analysis? (Press Enter to skip): ").strip()
        if resume_text:
            print(f"\n[{self.name}] Resume detected. Extracting additional information...")
            resume_data = self.process_resume(resume_text)
            experiences.extend(resume_data.get("experiences", []))
            education.extend(resume_data.get("education", []))
        else:
            print(f"\n[{self.name}] No resume provided. Proceeding with current data...")

        return self.process_profile(context, experiences, education)
     
        
    # Step 2: Generating user profile.
    def process_profile(self, context, experiences, education):
        """
        Step 3: Extract soft skills based on user input using the imported skills_system_prompt.
        Returns JSON in the required format.
        """
        # Combine all user input into a single context
        input_text = ""
        if experiences:
            input_text += "Work Experiences:\n" + "\n".join(experiences) + "\n"
        if education:
            input_text += "Education History:\n" + "\n".join(education) + "\n"

        # If there is no input at all, return insufficient evidence
        # if not input_text.strip():
        #     return {
        #         "identified_soft_skills": [],
        #         "message": "Insufficient evidence to infer soft skills"
        #     }

        # --- Call the LLM ---
        prompt = f"""
System Prompt:
{skills_system_prompt}

User Input:
{input_text}

Instructions:
Return results in JSON. Limit results to the most relevant 5 to 12 skills.
If there is insufficient information, leave inferred_skills blank.
Return JSON with the following format:
{{
    "experiences": [ "...", "..."],
    "education": [ "...", "..."],
    "inferred_skills":[ "...", "..."]
}}
"""
        result_json_str = call_llm(
            skills_system_prompt,  # system prompt
            prompt,                # user input
            "text"                 # response type
        )

        try:
            result_json = json.loads(result_json_str)
        except json.JSONDecodeError:
            result_json = {
                "experiences": ["JSONDecodeError"],
                "education": [],
                "inferred_skills":[]
            }

        # Limit to 12 skills max
        if "inferred_skills" in result_json:
            result_json["inferred_skills"] = result_json["inferred_skills"][:12]
        return result_json
    
    def process_resume(self, resume_text):
            """
            Process resume to extract key experiences and education points.
            Returns a dictionary with 'experiences' and 'education'.
            """
            prompt = f"""
System Prompt:
{skills_system_prompt}

User Input:
Here is a resume text:
{resume_text}

Instructions:
1. Extract the main work experiences (projects, job roles, responsibilities) in bullet form.
2. Extract education history (degrees, institutions, certifications) in bullet form.
3. Extract inferred skills with evidence provided in bullet form.
4. Return JSON with keys:
{{
    "experiences": [ "...", "..."],
    "education": [ "...", "..."],
    "inferred_skills":[ "...", "..."]
}}
5. Only include relevant items. Avoid explanations. Strictly follow the schema.
"""
            result_str = call_llm(skills_system_prompt, prompt, "text")
            try:
                result_json = json.loads(result_str)
            except json.JSONDecodeError:
                result_json = {"experiences": [], "education": []}
            return result_json