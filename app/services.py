from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User, Plan


def get_user(db: Session, user_id: str):
    return db.scalar(
        select(User).where(User.user_id == user_id)
    )


def save_user(db: Session, data):
    user = get_user(
        db,
        data.user_id,
    )

    if user:
        user.username = data.username
        user.age = data.age
        user.weight = data.weight
        user.goal = data.goal
        user.intensity = data.intensity
    else:
        user = User(
            user_id=data.user_id,
            username=data.username,
            age=data.age,
            weight=data.weight,
            goal=data.goal,
            intensity=data.intensity,
        )

        db.add(user)

    # Commit user immediately so the connection
    # does not keep an unnecessary pending transaction.
    db.commit()
    db.refresh(user)

    return user


def save_plan(
    db: Session,
    user: User,
    workout_plan: str,
    tip: str,
):
    if user.plan:
        user.plan.original_plan = workout_plan
        user.plan.original_tip = tip
        user.plan.updated_plan = None
        user.plan.updated_tip = None
        user.plan.last_feedback = None
        user.plan.updated_at = None

        plan = user.plan

    else:
        plan = Plan(
            user_id=user.id,
            original_plan=workout_plan,
            original_tip=tip,
        )

        db.add(plan)

    db.commit()
    db.refresh(plan)

    return plan


def update_plan(
    db: Session,
    user: User,
    revised_plan: str,
    revised_tip: str,
    feedback: str,
):
    plan = user.plan

    if not plan:
        raise ValueError(
            "No plan exists for this user."
        )

    plan.updated_plan = revised_plan
    plan.updated_tip = revised_tip
    plan.last_feedback = feedback
    plan.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(plan)

    return plan


def get_all_users(db: Session):
    return db.scalars(
        select(User).order_by(
            User.created_at.desc()
        )
    ).all()


def delete_user(
    db: Session,
    user: User,
):
    db.delete(user)
    db.commit()