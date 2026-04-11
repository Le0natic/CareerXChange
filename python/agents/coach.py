from shared.llm_client import call_llm
from agents.base.agent import Agent
from agents.prompts import coach_system_prompt
from agents.schemas import coach_schema
import json
import requests
from dotenv import load_dotenv

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

Available Tools:
1. search_ssg_courses(query)
Purpose: Retrieves a list of courses from MySkillsFuture directory, a one-stop online portal designed by the Singapore government to support lifelong learning and career development. 
When to use: Use this when you want to check available courses for upskilling.
Parameter usage: 
- query=input keywords
Output: You will receive the course details.

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
Each recommended_next_steps must contain at least 2 items and should include recommended courses from MySkillsFuture. 
You have access to a tool called search_ssg_courses(query) to retrieve course information to recommend.
When recommending a course, extract and respond with the full course names of relevant courses. Do not hallucinate the course names.

Important Note While Returning JSON:
1. Return ONLY valid JSON, and must be constructed with double-quotes; Double quotes within strings must be escaped with a backslash.
2. No explanation.
3. Follow schema strictly.
        """
        raw = call_llm(self.system_prompt, prompt, "json_object")
        parsed = json.loads(raw)
        self._validate(parsed)
        return parsed

    def search_ssg_courses(query):
        load_dotenv()
        # Production Token URL for "Open" apps
        token_url = "https://public-api.ssg-wsg.sg/dp-oauth/oauth/token"
        
        # Base64 encode the credentials for the Authorization header
        auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
        encoded_auth = base64.b64encode(auth_str.encode()).decode()
        
        headers = {
            "Authorization": f"Basic {encoded_auth}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
            
        # Use client_credentials grant type
        data = {"grant_type": "client_credentials"}
        
        response = requests.post(token_url, headers=headers, data=data)
        
        if response.status_code == 200:
            token = response.json().get("access_token")
        else:
            raise Exception(f"Failed to get token: {response.text}")

        api_url = "https://ssg-wsg.sg/courses/directory"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Parameters for the search
        params = {
            "keyword": query,
            "pageSize": 5
        }
        
        response = requests.get(api_url, headers=headers, params=params)
        return response.json()
