from shared.llm_client import call_llm
from agents.base.agent import Agent
from agents.prompts import coach_system_prompt
from agents.schemas import coach_schema
import json

class CoachAgent(Agent):
    def __init__(self):
        super().__init__(
            name = "Coach Agent",
            system_prompt = coach_system_prompt,
            schema = coach_schema
        )

    # Step 1: Start interactive run.
    def run_interactive(self, initial_output):
        context = initial_output
        print(f"\n[{self.name}] Putting together your personalised career advice...")
        return self.start_coaching(context)

    # Step 3: Final classification.
    def start_coaching(self, context):
        prompt = f"""
Forumulate career advice based on:

Initial context:
{context}

Instructions:
Return results in JSON. Limit results to the most relevant 2 to 5 career paths.
If there is insufficient information, return:
{{
"career_summary": "Insufficient input to give career advice",
"career_paths": [],
"strengths_identified": [],
"development_areas": [],
"additional_guidance": ""
}}

Return JSON in following format:
{{
"career_summary": "...",

"career_paths": [
    {{
    "career_title": "...",
    "description": "...",
    "why_it_fits": [
        "...",
        "..."
    ],
    "recommended_next_steps": [
        "...",
        "..."
    ]
    }},
    {{
    "career_title": "...",
    "description": "...",
    "why_it_fits": [
        "...",
        "..."
    ],
    "recommended_next_steps": [
        "...",
        "..."
    ]
    }}
],

"strengths_identified": [
    "...",
    "..."
],

"development_areas": [
    "...",
    "..."
],

"additional_guidance": "..."
}}

Return at least 2 career_paths.
Each why_it_fits must contain at least 2 items.
Each recommended_next_steps must contain at least 2 items.

End off with:
Handing off to Resume Agent for creating resume.

Important Note While Returning JSON:
1. Return ONLY valid JSON, and must be constructed with double-quotes; Double quotes within strings must be escaped with a backslash.
2. No explanation.
3. Follow schema strictly.
        """
        # raw = call_llm(self.system_prompt, prompt, "json_object")
        # parsed = json.loads(raw)
        # self._validate(parsed)
        # return parsed
        result_str = call_llm(coach_system_prompt, prompt, "text")
        try:
            result_json = json.loads(result_str)
        except json.JSONDecodeError:
            result_json = {"career_summary": "JSONDecodeError", "career_paths": [], "strengths_identified": [], "development_areas": [], "additional_guidance": ""}
        return result_json
        