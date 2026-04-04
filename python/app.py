from agents.mbti import MBTIAgent
from agents.skills import SkillsAgent
from agents.coach import CoachAgent
import re
import json

# Step 1: Initiate agents.
mbti_agent = MBTIAgent()
skills_agent = SkillsAgent()
coach_agent = CoachAgent()

# Step 2: Run the MBTI agent.
mbti_result = mbti_agent.run_interactive(None)

# Step 3: Print MBTI result.
print("\nFinal MBTI Result:")
print(json.dumps(mbti_result, ensure_ascii=False, indent=2))
#if result is not None:
#    json_string = json.dumps(result) # Convert dict to JSON string.
#    cleaned_result = re.sub(r"'", '"', json_string)  # Remove any single quote present.
#    print(cleaned_result)
#else:
#    print("Cannot determine final result.")

# Step 4: Run Skills agent next
#skills_result = skills_agent.run_interactive(None)
skills_result = skills_agent.run_interactive(initial_output=mbti_result)

# Step 5: Print Skills result
print("\nFinal Skills Result:")
print(json.dumps(skills_result, ensure_ascii=False, indent=2))
#if skills_result is not None:
#    skills_json_string = json.dumps(skills_result, ensure_ascii=False)
#    cleaned_skills = re.sub(r"'", '"', skills_json_string)
#    print(cleaned_skills)
#else:
#    print("Cannot determine skills result.")

# Step 6: Run Coach agent
coach_result = coach_agent.run_interactive(
    initial_output={
        "mbti": mbti_result,
        "skills": skills_result
    }
)

# Step 6: Print Coach result
print("\nFinal Coaching Result:")
print(json.dumps(coach_result, ensure_ascii=False, indent=2))
#if coach_result is not None:
#    coach_json_string = json.dumps(coach_result, ensure_ascii=False)
#    cleaned_coaching = re.sub(r"'", '"', coach_json_string)
#    print(cleaned_coaching)
#else:
#    print("Cannot determine coaching result.")