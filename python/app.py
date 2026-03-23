from agents.mbti import MBTIAgent
import re
import json

# Step 1: Initiate MBTI agent.
mbti_agent = MBTIAgent()

# Step 2: Run the MBTI agent.
result = mbti_agent.run_interactive(None)

# Step 3: Print MBTI result.
print("\nFinal MBTI Result:")
if result is not None:
    json_string = json.dumps(result) # Convert dict to JSON string.
    cleaned_result = re.sub(r"'", '"', json_string)  # Remove any single quote present.
    print(cleaned_result)
else:
    print("Cannot determine final result.")