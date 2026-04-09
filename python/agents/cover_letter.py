from shared.llm_client import call_llm
from agents.base.agent import Agent
from agents.prompts import cover_letter_system_prompt
from agents.schemas import cover_letter_schema
import json

class CoverLetterAgent(Agent):
    def __init__(self):
        super().__init__(
            name = "Cover Letter Agent",
            system_prompt = cover_letter_system_prompt,
            schema = cover_letter_schema
        )

    def run_interactive(self, initial_output):
        context = initial_output
        print(f"\n[{self.name}] Generating cover letter...")
        return self.write_cover_letter(context)
    
    def write_cover_letter(self, context):
        prompt = f"""
Write a cover letter based on:

Initial context:
{context}

Instructions:
Return results in JSON.
If there is insufficient information, return:
{{
    "cover_letter": "Insufficient input to generate cover letter"
}}

Return JSON in following format:
{{
    "cover_letter": "..."
}}

IMPORTANT:
- Return ONLY valid JSON (no single quotes, strictly double quotes for keys and values).
- No explanation.
- Follow schema strictly.
"""
        result_str = call_llm(cover_letter_system_prompt, prompt, "text")
        try:
            return json.loads(result_str)
        except json.JSONDecodeError:
            return {"cover_letter": "JSONDecodeError"}
