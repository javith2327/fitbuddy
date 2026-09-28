from app.ai.gemini_client import get_gemini_service
from app.config import settings

def generate_workout_gemini(username: str, age: int, weight: float, goal: str, intensity: str) -> str:
    prompt = f"""
You are FitBuddy, a careful fitness-programming assistant.

Create a personalized 7-day beginner/intermediate fitness plan.
User:
- Name: {username}
- Age: {age}
- Weight: {weight} kg
- Goal: {goal}
- Preferred intensity: {intensity}

Return exactly seven labeled days. For each day include:
1. Focus
2. Warm-up (5–10 minutes)
3. Main workout with exercise names, sets, reps or duration, and rest
4. Cool-down/recovery

Rules:
- Keep the plan realistic and progressive.
- Include at least one recovery/rest-oriented day.
- Do not prescribe dangerous extremes, dehydration, starvation, or unsafe supplement use.
- Mention that the plan is general educational guidance and should be adjusted with a qualified professional when needed.
- Do not diagnose medical conditions.
- Use clear plain text headings, not JSON.
"""
    return get_gemini_service().generate(
        settings.workout_model, prompt, temperature=0.65, max_tokens=5000
    )
