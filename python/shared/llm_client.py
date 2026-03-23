import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def call_llm(system_prompt: str, user_input: str) -> str:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.responses.create(
        model=llm_name,
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
    )

    return response.output[0].content[0].text