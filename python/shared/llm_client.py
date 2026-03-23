import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))
llm_name = "gpt-4.1-mini"

def call_llm(system_prompt: str, user_input: str, response_type: str) -> str:
    response = client.chat.completions.create(
        model=llm_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ],
        response_format = {"type": response_type}
    )
    return response.choices[0].message.content
