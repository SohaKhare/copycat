from backend.database.supabase import supabase
from backend.models.skill import Skill


def create_skill(skill: Skill):
    data = {
        "name": skill.name,
        "description": skill.description,
        "steps": skill.steps,
        "environment": skill.environment,
        "confidence": skill.confidence,
        "status": skill.status,
        "tested": skill.tested,
    }

    response = (
        supabase
        .table("skills")
        .insert(data)
        .execute()
    )

    return response.data[0]


def get_skills():
    response = (
        supabase
        .table("skills")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )

    return response.data


def get_accepted_skills():
    response = (
        supabase
        .table("skills")
        .select("*")
        .eq("status", "accepted")
        .execute()
    )

    return response.data


def get_skill(skill_id: str):
    response = (
        supabase
        .table("skills")
        .select("*")
        .eq("id", skill_id)
        .execute()
    )

    if not response.data:
        return None

    return response.data[0]


def update_skill(skill_id: str, data: dict):
    response = (
        supabase
        .table("skills")
        .update(data)
        .eq("id", skill_id)
        .execute()
    )

    if not response.data:
        return None

    return response.data[0]


def delete_skill(skill_id: str):
    response = (
        supabase
        .table("skills")
        .delete()
        .eq("id", skill_id)
        .execute()
    )

    return len(response.data) > 0