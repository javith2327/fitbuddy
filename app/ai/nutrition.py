from app.ai.gemini_client import get_gemini_service
from app.config import settings

def generate_nutrition_tip_with_flash(goal: str) -> str:
    prompt = f"""
Give one concise, practical nutrition or recovery tip for a person whose fitness goal is "{goal}".
Keep it to 3–5 sentences. Focus on sustainable habits, adequate protein/food quality,
hydration, sleep, and recovery as appropriate. Do not prescribe extreme diets or medical
treatment. End with a brief reminder that individual nutrition needs vary.
"""
    return get_gemini_service().generate(
        settings.tip_model, prompt, temperature=0.5, max_tokens=500
    )
