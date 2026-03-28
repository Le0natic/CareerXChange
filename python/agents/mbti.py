from shared.llm_client import call_llm
from agents.base.agent import Agent
from agents.prompts import mbti_system_prompt, mbti_questions
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

        # Step 1: Generate questions.
        questions = self.generate_questions(context, question_count)

        print(f"\n[{self.name}] Got it! Please answer the following {len(questions)} questions.")

        for qs in questions:
            print(f"\n[{self.name}] {count}. {qs}")
            while True:
                user_answer = input("Your answer (A or B): ").strip().upper()
                if user_answer not in {"A", "B"}:
                    print(f"\n[{self.name}] Please provide answer only in A or B. Please answer again...")
                else:
                    print(f"\n[{self.name}] Valid answer! Adding answer to questionnaire...")
                    answers.append({
                        "question": qs,
                        "answer": user_answer
                    })
                    print(f"\n[{self.name}] Record added successfully. To the next question...")
                    break
            count += 1
            if count > question_count:
                print(f"\n[{self.name}] No more question left. Concluding...")
                break
        
        # Step 2: Final classification.
        if len(answers) == len(questions):
            return self.finalize_questionnaire(context, answers)
        
        return print(f"\n[{self.name}] ({len(answers)} out of {len(questions)} valid answers)\nInsufficient questions answered to form a final decision.")

    # Step 2: Ask questions.
    def generate_questions(self, context, question_count):
        print(f"Requesting {question_count} questions from {self.name}...")
        prompt = f"""
        Based on your knowledge as an agent detailed in {self.system_prompt}:
        {context}

        Ask EXACTLY any {question_count} questions from the question list below:
        {mbti_questions}

        Important Note While Asking Questions:
        1. Only ask the questions provided, word-by-word: Do not deviate from these questions.
        2. Do not repeat questions already asked.
        3. Do not show any hint or information regarding what the question is asking about. E.g.: providing context of 'Si/Se' in the questions prompted to the user.
        4. There must be 2 choices (labelled with A and B arranged vertically) for each question.
        5. Must cover at least ONE question from each of 3 categories.

        Return JSON in following format:
        {{
            "questions": [
                "...", 
                "..."
            ]
        }}

        Important Note While Returning JSON:
        1. Return ONLY valid JSON, and must be constructed with double-quotes; Double quotes within strings must be escaped with a backslash.
        2. No explanation.
        3. Follow schema strictly.
        """
        raw = call_llm(self.system_prompt, prompt, "json_object")
        data = json.loads(raw)
        return data["questions"]
    
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
            "...",
            "...",
            "..."
          ]
        }}

        Important Note While Returning JSON:
        1. Return ONLY valid JSON, and must be constructed with double-quotes; Double quotes within strings must be escaped with a backslash.
        2. No explanation.
        3. Follow schema strictly.
        """
        raw = call_llm(self.system_prompt, prompt, "json_object")
        parsed = json.loads(raw)
        self._validate(parsed)
        return parsed