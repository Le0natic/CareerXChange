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
    
    def _call(self, user_input):
        enforced_prompt = f"""
        {self.system_prompt}

        IMPORTANT:
        - Return ONLY valid JSON (no single quotes, strictly double quotes for keys and values).
        - No explanation.
        - Follow schema strictly.
        """
        return call_llm(enforced_prompt, user_input)

    def _parse(self, output):
        try:
            return json.loads(output)
        except json.JSONDecodeError:
            raise Exception(f"[{self.name}] Invalid JSON output:\n{output}")
