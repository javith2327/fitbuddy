from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import FeedbackRequest, UserInput
from app.services import (
    delete_user,
    get_all_users,
    get_user,
    save_plan,
    save_user,
    update_plan,
)
from app.ai.workout_generator import generate_workout_gemini
from app.ai.nutrition import generate_nutrition_tip_with_flash
from app.ai.plan_updater import update_workout_plan


router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


def render_error(
    request: Request,
    message: str,
    status_code: int = 400,
):
    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={
            "request": request,
            "message": message,
        },
        status_code=status_code,
    )


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
        },
    )


# =========================================================
# HTML: GENERATE WORKOUT
# =========================================================

@router.post("/generate-workout", response_class=HTMLResponse)
def generate_workout(
    request: Request,
    username: str = Form(...),
    user_id: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        data = UserInput(
            username=username,
            user_id=user_id,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity,
        )

        # Save/update user in database
        user = save_user(db, data)

        # IMPORTANT:
        # user_id is used by FitBuddy/database,
        # but it is NOT a parameter of generate_workout_gemini().
        workout = generate_workout_gemini(
            username=data.username,
            age=data.age,
            weight=data.weight,
            goal=data.goal,
            intensity=data.intensity,
        )

        # Generate nutrition/recovery tip
        tip = generate_nutrition_tip_with_flash(
            data.goal
        )

        # Save generated plan
        plan = save_plan(
            db,
            user,
            workout,
            tip,
        )

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "request": request,
                "user": user,
                "plan": plan,
                "display_plan": plan.original_plan,
                "display_tip": plan.original_tip,
                "is_updated": False,
            },
        )

    except ValueError as exc:
        return render_error(
            request,
            str(exc),
            400,
        )

    except Exception as exc:
        return render_error(
            request,
            f"Generation failed: {exc}",
            502,
        )


# =========================================================
# HTML: SUBMIT FEEDBACK
# =========================================================

@router.post("/submit-feedback", response_class=HTMLResponse)
def submit_feedback(
    request: Request,
    user_id: str = Form(...),
    feedback: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        data = FeedbackRequest(
            user_id=user_id,
            feedback=feedback,
        )

        user = get_user(
            db,
            data.user_id,
        )

        if not user or not user.plan:
            return render_error(
                request,
                "User ID not found or no workout plan exists.",
                404,
            )

        # Update workout plan using feedback
        revised = update_workout_plan(
            user.plan.original_plan,
            data.feedback,
            user.goal,
            user.intensity,
        )

        # Generate new nutrition tip
        tip = generate_nutrition_tip_with_flash(
            user.goal
        )

        # Save updated plan
        plan = update_plan(
            db,
            user,
            revised,
            tip,
            data.feedback,
        )

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "request": request,
                "user": user,
                "plan": plan,
                "display_plan": plan.updated_plan,
                "display_tip": plan.updated_tip,
                "is_updated": True,
            },
        )

    except ValueError as exc:
        return render_error(
            request,
            str(exc),
            400,
        )

    except Exception as exc:
        return render_error(
            request,
            f"Plan update failed: {exc}",
            502,
        )


# =========================================================
# ADMIN / COACH
# =========================================================

@router.get("/view-all-users", response_class=HTMLResponse)
def view_all_users(
    request: Request,
    db: Session = Depends(get_db),
):
    users = get_all_users(db)

    return templates.TemplateResponse(
        request=request,
        name="all_users.html",
        context={
            "request": request,
            "users": users,
        },
    )


@router.post("/delete-user/{user_id}")
def remove_user(
    user_id: str,
    db: Session = Depends(get_db),
):
    user = get_user(
        db,
        user_id,
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    delete_user(
        db,
        user,
    )

    return RedirectResponse(
        "/view-all-users",
        status_code=303,
    )


# =========================================================
# JSON API
# =========================================================

@router.post("/api/generate-workout")
def api_generate(
    data: UserInput,
    db: Session = Depends(get_db),
):
    try:
        # Save/update user
        user = save_user(
            db,
            data,
        )

        # IMPORTANT:
        # Do NOT use **data.model_dump() here because
        # that also contains user_id.
        workout = generate_workout_gemini(
            username=data.username,
            age=data.age,
            weight=data.weight,
            goal=data.goal,
            intensity=data.intensity,
        )

        # Generate nutrition tip
        tip = generate_nutrition_tip_with_flash(
            data.goal
        )

        # Save plan
        plan = save_plan(
            db,
            user,
            workout,
            tip,
        )

        return {
            "user_id": user.user_id,
            "workout_plan": plan.original_plan,
            "nutrition_tip": plan.original_tip,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        )


# =========================================================
# JSON API: FEEDBACK
# =========================================================

@router.post("/api/submit-feedback")
def api_feedback(
    data: FeedbackRequest,
    db: Session = Depends(get_db),
):
    user = get_user(
        db,
        data.user_id,
    )

    if not user or not user.plan:
        raise HTTPException(
            status_code=404,
            detail="User or plan not found.",
        )

    try:
        # Generate revised plan
        revised = update_workout_plan(
            user.plan.original_plan,
            data.feedback,
            user.goal,
            user.intensity,
        )

        # Generate updated nutrition tip
        tip = generate_nutrition_tip_with_flash(
            user.goal
        )

        # Save update
        plan = update_plan(
            db,
            user,
            revised,
            tip,
            data.feedback,
        )

        return {
            "user_id": user.user_id,
            "updated_plan": plan.updated_plan,
            "nutrition_tip": plan.updated_tip,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        )


# =========================================================
# JSON API: ALL USERS
# =========================================================

@router.get("/api/users")
def api_users(
    db: Session = Depends(get_db),
):
    users = get_all_users(db)

    return [
        {
            "user_id": user.user_id,
            "username": user.username,
            "age": user.age,
            "weight": user.weight,
            "goal": user.goal,
            "intensity": user.intensity,
            "created_at": user.created_at.isoformat(),
            "has_updated_plan": bool(
                user.plan and user.plan.updated_plan
            ),
        }
        for user in users
    ]


# =========================================================
# HEALTH CHECK
# =========================================================

@router.get("/health")
def health():
    return {
        "status": "ok",
        "service": "FitBuddy",
    }