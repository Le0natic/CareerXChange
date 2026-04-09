# llm_secure.py
import re
from shared.llm_client import call_llm

BLOCKED_INPUT = [
    r"ignore previous instructions",
    r"reveal the system prompt",
    r"api[_ -]?key",
]

BLOCKED_OUTPUT = [
    r"sk-[A-Za-z0-9]+",
    r"api[_ -]?key",
    r"password",
]

def is_malicious_input(text: str) -> bool:
    text = text.lower()
    return any(re.search(p, text) for p in BLOCKED_INPUT)

def is_unsafe_output(text: str) -> bool:
    text = text.lower()
    return any(re.search(p, text) for p in BLOCKED_OUTPUT)

def call_llm_secure(system_prompt: str, user_input: str) -> str:
    if is_malicious_input(user_input):
        return "Blocked malicious input"

    response = call_llm(system_prompt, user_input,"text")

    if is_unsafe_output(response):
        return "Blocked unsafe output"

    return response