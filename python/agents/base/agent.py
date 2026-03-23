import json
from shared.llm_client import call_llm

class Agent:
    def __init__(self, name, system_prompt, schema):
        self.name = name
        self.system_prompt = system_prompt
        self.schema = schema

    def run(self, user_input, retries = 2):
        for attempt in range(retries + 1):
            raw_output = self._call(user_input)
            try:
                parsed_output = self._parse(raw_output)
                self._validate(parsed_output)
                return parsed_output
            except Exception as e:
                if attempt == retries:
                    raise e
    
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

    def _validate(self, data):
        for key, value_type in self.schema.items():
            if key not in data:
                raise Exception(f"[{self.name}] Missing key: {key}")
            if not isinstance(data[key], value_type):
                raise Exception(
                    f"[{self.name}] Wrong type for {key}, expected {value_type}"
                )