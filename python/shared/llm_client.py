import os
from openai import OpenAI
from dotenv import load_dotenv
from shared.logger import setup_logger

load_dotenv()
logger = setup_logger("llm_client")
llm_name = "gpt-4.1-mini"

def call_llm(system_prompt: str, user_input: str, response_type: str) -> str:
    client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))
    logger.info("Calling LLM")
    response = client.chat.completions.create(
        model=llm_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ],
        response_format = {"type": response_type}
    )
    logger.info("LLM call completed")
    return response.choices[0].message.content
