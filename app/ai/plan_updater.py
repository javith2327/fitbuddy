from app.ai.gemini_client import get_gemini_service
from app.config import settings

def update_workout_plan(original_plan: str, feedback: str, goal: str, intensity: str) -> str:
    prompt = f"""
You are updating an existing FitBuddy 7-day workout plan.

Fitness goal: {goal}
Preferred intensity: {intensity}

ORIGINAL PLAN:
{original_plan}

USER FEEDBACK:
{feedback}

Create a revised seven-day plan that addresses the feedback while preserving useful
parts of the original plan. Keep the same day-by-day structure:
Day, Focus, Warm-up, Main workout (sets/reps/duration/rest), Cool-down/recovery.

Do not use unsafe training, extreme calorie restriction, dehydration, or medical treatment.
Include a sensible recovery day. Add a short safety note at the end.
"""
    return get_gemini_service().generate(
        settings.workout_model, prompt, temperature=0.65, max_tokens=5000
    )
