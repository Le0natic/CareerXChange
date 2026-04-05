import random

from shared.llm_client import call_llm
from agents.base.agent import Agent
from agents.prompts import mbti_system_prompt
from agents.schemas import mbti_schema
import json

class MBTIAgent(Agent):
    def __init__(self):
        super().__init__(
            name = "MBTI Agent",
            system_prompt = mbti_system_prompt,
            schema = mbti_schema
        )

    # Step 1: Start interactive run.
    def run_interactive(self, initial_output, question_count = 20):
        context = initial_output
        answers = []
        count = 1

        # Step 1: Select questions from bank.
        questions = self.select_questions(self.question_bank, total_questions=20)

        print(f"\n[{self.name}] Got it! Please answer the following {len(questions)} questions.")

        for qs in questions:
            while True:  # Loop until valid answer is provided
                print(f"\n[{self.name}] {count}. {qs}")
                user_answer = input("Your answer (A or B): ").strip().upper()

                if user_answer not in {"A", "B"}:
                    print(f"\n[{self.name}] Invalid input. Please answer only with A or B. Let's try again...")
                    continue  # Ask the same question again
                else:
                    print(f"\n[{self.name}] Valid answer! Recording your answer...")
                    answers.append({
                        "question": qs,
                        "answer": user_answer
                    })
                    print(f"\n[{self.name}] Answer recorded. Moving to next question...")
                    break  # Move to the next question

            count += 1
            if count > question_count:
                print(f"\n[{self.name}] No more questions left. Concluding...")
                break
        
        # Step 2: Final classification.
        if len(answers) == len(questions):
            return self.finalize_questionnaire(context, answers)
        else:
            # Return a standard dict instead of print
            return {
                "mbti": None,
                "personality_type": None,
                "confidence": 0,
                "traits": [],
                "message": f"Only {len(answers)} out of {len(questions)} questions answered. Cannot determine MBTI type."
            }
    
    question_bank = {
        "Dichotomical": [
            # ENERGY — E/I
            "After a busy week, which feels more refreshing? \nA. Alone with one person \nB. Going out socially",
            "When solving a problem, what do you naturally do first? \nA. Think privately \nB. Talk it out",
            "In a group discussion, you usually: \nA. Observe and speak when meaningful \nB. Jump in easily",
            "After social interaction you usually feel: \nA. Drained \nB. Energized",

            # INFORMATION — S/N
            "When learning something new, which helps more? \nA. Concrete examples \nB. Big-picture concepts",
            "Which do you notice more naturally? \nA. Details now \nB. Patterns/possibilities",
            "When approaching a new idea, you tend to: \nA. Ask 'How does this work?' \nB. Ask 'What could this lead to?'",
            "When reading a story or film, you focus more on: \nA. Events/details \nB. Themes/symbolism",

            # DECISION STYLE — T/F
            "When making an important decision, you prioritize: \nA. Logic \nB. Impact on people",
            "When giving feedback, your instinct is: \nA. Be direct \nB. Phrase carefully",
            "In disagreements, you focus first on: \nA. What is logically correct \nB. Maintaining understanding",
            "Fairness usually means: \nA. Same rules for all \nB. Considering circumstances",

            # STRUCTURE — J/P
            "When planning a trip you prefer to: \nA. Organize itinerary \nB. Decide spontaneously",
            "How do deadlines affect you? \nA. Finish early \nB. Work best near deadline",
            "Your workspace or schedule is usually: \nA. Organized \nB. Flexible",
            "When starting a project you prefer: \nA. Define plan first \nB. Experiment along the way"
        ],
        "Targeted Cluster": [
            # Ni vs Ne
            "When thinking about the future, do you: \nA. Focus on one vision \nB. Generate many possibilities",
            "When brainstorming ideas you prefer: \nA. Develop one deeply \nB. Explore many rapidly",

            # Si vs Se
            "When solving problems, you rely more on: \nA. Past experience \nB. Immediate observation",
            "Your attention naturally goes to: \nA. What worked before \nB. What is happening now",

            # Ti vs Te
            "When analyzing something you prefer: \nA. Understand internal logic \nB. Make system efficient",
            "When something is inefficient you: \nA. Reevaluate logic \nB. Reorganize processes",

            # Fi vs Fe
            "When making moral decisions you rely more on: \nA. Personal values \nB. Group harmony",
            "When someone is upset you usually: \nA. Respect their emotions \nB. Restore harmony"
        ],
        "Pair Differentiation": [
            # INTJ vs INTP
            "Do you prefer: \nA. Structured long-term strategies \nB. Exploring theories without plan",

            # INFJ vs INFP
            "When your values are challenged you: \nA. Guide others \nB. Reflect internally",

            # ENTJ vs ESTJ
            "In leadership you focus more on: \nA. Strategic transformation \nB. Enforcing systems",

            # ISTJ vs ISFJ
            "When rules conflict with someone's situation you: \nA. Maintain rules \nB. Protect people",

            # ENFP vs ENTP
            "When exploring ideas you focus more on: \nA. Meaning/values \nB. Logical possibilities",

            # ISFP vs ISTP
            "When approaching a problem you rely more on: \nA. Personal values \nB. Technical logic"
        ]
    }

    def select_questions(self, question_bank, total_questions=20):
        """
        Returns a Python list of selected questions (ready to loop over),
        balanced across categories.
        """
        categories = list(question_bank.keys())
        selected_questions = []

        # Determine number of questions per category
        base_count = total_questions // len(categories)
        remainder = total_questions % len(categories)
        category_counts = {cat: base_count + (1 if i < remainder else 0) for i, cat in enumerate(categories)}

        # Pick questions
        for cat, count in category_counts.items():
            if count > len(question_bank[cat]):
                raise ValueError(f"Not enough questions in category {cat} to pick {count}")
            selected_questions.extend(random.sample(question_bank[cat], count))

        random.shuffle(selected_questions)
        return selected_questions

    # Step 3: Final classification.
    def finalize_questionnaire(self, context, answers):
        prompt = f"""
        Determine MBTI type based on:

        Initial context:
        {context}

        Q&A:
        {answers}

        Return JSON in following format:
        {{
          "mbti": "...",
          "personality_type": "..."
          "confidence": 0-1,
          "traits": [
            "...",
            "..."
          ]
        }}

        End off with:
        Handing off to Skills Agent for skills identifying.

        Important Note While Returning JSON:
        1. Return ONLY valid JSON, and must be constructed with double-quotes; Double quotes within strings must be escaped with a backslash.
        2. No explanation.
        3. Follow schema strictly.
        4. In the traits, provide a brief description of the personality_type with two key points
        """
        raw = call_llm(self.system_prompt, prompt, "json_object")
        parsed = json.loads(raw)
        self._validate(parsed)
        return parsed
        