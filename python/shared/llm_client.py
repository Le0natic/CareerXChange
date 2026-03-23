import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))
llm_name = "gpt-4.1-mini"

def call_llm(system_prompt: str, user_input: str) -> str:
    response = client.responses.create(
        model = llm_name,
        input = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
    )
    return response.output[0].content[0].text