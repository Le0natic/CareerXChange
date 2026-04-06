mbti_schema = {
    "mbti": str,
    "personality_type": str,
    "confidence": float,
    "traits": list
}
cover_letter_schema = {
    "cover_letter": str
}
skills_schema = {
    "experiences": list,
    "education": list,
    "inferred_skills": list,
    "existing_resume": str
}
coach_schema = {
    "career_summary": str,
    "career_paths": list,
    "strengths_identified": list,
    "development_areas": list,
    "additional_guidance": str
}
resume_schema = {
    "header": object,
    "professional_summary": str,
    "skills": str,
    "work_experience": list,
    "projects": str,
    "education": list,
    "additional_sections": object
}
