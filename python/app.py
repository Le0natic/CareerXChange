from agents.mbti import MBTIAgent

# Step 1: Initiate MBTI Agent.
agent = MBTIAgent()

# Step 2: Run the MBTI Agent.
result = agent.run_interactive(None)

# Step 3: Print MBTI result.
print("\nFinal MBTI Result:")
print(result if result is not None else "Cannot determine final result.")