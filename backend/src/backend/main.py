import asyncio
from asyncio import to_thread
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, UploadFile
from google.genai.errors import ServerError

from backend.voice.live_agent import VoiceSession

from backend.ai.gemini import analyze_frames, test_gemini
from backend.ai.skill_resolver import resolve_skill

from backend.models.execution import ExecuteRequest
from backend.models.skill import EditSkillRequest, Skill

from backend.storage.skills import (
    create_skill,
    delete_skill,
    get_accepted_skills,
    get_skill,
    get_skills,
    update_skill,
)

from backend.video.processor import extract_frames
from backend.ai.planner import create_execution_plan

from backend.executors.router import (
    execute_plan,
)

from backend.storage.execution_history import (
    get_execution,
    get_execution_history,
    save_execution,
)


app = FastAPI(
    title="CopyCat API",
    description="Teach AI by showing.",
    version="0.3.0",
)


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

FRAMES_DIR = Path("frames")
FRAMES_DIR.mkdir(exist_ok=True)

_voice_session: VoiceSession | None = None
_voice_task: asyncio.Task | None = None


@app.get("/")
def root():
    return {
        "message": "CopyCat backend is running!"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.post("/upload-video")
async def upload_video(file: UploadFile = File(...)):

    if not file.content_type or not file.content_type.startswith("video/"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a valid video file.",
        )

    file_extension = Path(file.filename).suffix

    video_id = str(uuid4())

    unique_filename = f"{video_id}{file_extension}"

    file_path = UPLOAD_DIR / unique_filename

    with file_path.open("wb") as buffer:
        contents = await file.read()
        buffer.write(contents)

    video_frames_dir = FRAMES_DIR / video_id

    try:
        # extract_frames decodes every frame and analyze_frames calls the
        # Gemini API (with SDK retries), which can take minutes on a long
        # recording. Running them on threads keeps the event loop responsive
        # so concurrent requests (health checks, retries) are still served.
        frames = await to_thread(
            extract_frames,
            video_path=file_path,
            output_dir=video_frames_dir,
            interval_seconds=1.0,
        )

        analysis = await to_thread(analyze_frames, frames)

        saved_skills = []

        for candidate_skill in analysis.candidate_skills:

            steps = [
                step.model_dump()
                for step in candidate_skill.steps
            ]

            skill = Skill(
                name=candidate_skill.name,
                description=candidate_skill.description,
                steps=steps,
                environment=candidate_skill.environment,
                confidence=candidate_skill.confidence,
                status="pending",
                tested=False,
            )

            created_skill = create_skill(skill)

            saved_skills.append(created_skill)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except ServerError:
        raise HTTPException(
            status_code=503,
            detail=(
                "Gemini is temporarily unavailable. "
                "Please try again later."
            ),
        )

    return {
        "message": "Video analyzed and candidate skill saved successfully!",
        "video_id": video_id,
        "original_filename": file.filename,
        "frames_extracted": len(frames),
        "analysis": analysis,
        "saved_skills": saved_skills,
    }


@app.get("/skills")
def get_all_skills():
    return get_skills()


@app.get("/skills/{skill_id}")
def get_skill_by_id(skill_id: str):

    skill = get_skill(skill_id)

    if skill is None:
        raise HTTPException(
            status_code=404,
            detail="Skill not found",
        )

    return skill


@app.post("/skills/{skill_id}/accept")
def accept_skill(skill_id: str):

    skill = update_skill(
        skill_id,
        {
            "status": "accepted"
        }
    )

    if skill is None:
        raise HTTPException(
            status_code=404,
            detail="Skill not found",
        )

    return {
        "message": "Skill accepted successfully",
        "skill": skill,
    }


@app.post("/skills/{skill_id}/reject")
def reject_skill(skill_id: str):

    skill = update_skill(
        skill_id,
        {
            "status": "rejected"
        }
    )

    if skill is None:
        raise HTTPException(
            status_code=404,
            detail="Skill not found",
        )

    return {
        "message": "Skill rejected successfully",
        "skill": skill,
    }


@app.put("/skills/{skill_id}")
def edit_skill(
    skill_id: str,
    updated_data: EditSkillRequest,
):

    existing_skill = get_skill(skill_id)

    if existing_skill is None:
        raise HTTPException(
            status_code=404,
            detail="Skill not found",
        )

    update_data = updated_data.model_dump(
        exclude_none=True
    )

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="No update data provided",
        )

    skill = update_skill(
        skill_id,
        update_data
    )

    return {
        "message": "Skill updated successfully",
        "skill": skill,
    }


@app.post("/skills/{skill_id}/tested")
def mark_skill_tested(skill_id: str):

    skill = update_skill(
        skill_id,
        {
            "tested": True
        }
    )

    if skill is None:
        raise HTTPException(
            status_code=404,
            detail="Skill not found",
        )

    return {
        "message": "Skill marked as tested",
        "skill": skill,
    }


@app.delete("/skills/{skill_id}")
def remove_skill(skill_id: str):

    deleted = delete_skill(skill_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Skill not found",
        )

    return {
        "message": "Skill deleted successfully",
        "skill_id": skill_id,
    }


@app.post("/resolve-skill")
def resolve_user_skill(
    request: ExecuteRequest,
):

    accepted_skills = get_accepted_skills()

    if not accepted_skills:
        raise HTTPException(
            status_code=404,
            detail="No accepted skills found.",
        )

    try:
        resolved_skill = resolve_skill(
            command=request.command,
            skills=accepted_skills,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except ServerError:
        raise HTTPException(
            status_code=503,
            detail=(
                "Gemini is temporarily unavailable. "
                "Please try again later."
            ),
        )

    if resolved_skill is None:
        return {
            "message": "No matching learned skill found.",
            "command": request.command,
            "resolved_skill": None,
        }

    return {
        "message": "Matching skill found successfully.",
        "command": request.command,
        "resolved_skill": resolved_skill,
    }

@app.post("/execute")
def execute_user_command(
    request: ExecuteRequest,
):
    accepted_skills = (
        get_accepted_skills()
    )

    if not accepted_skills:
        raise HTTPException(
            status_code=404,
            detail=(
                "No accepted skills found."
            ),
        )

    try:
        resolved_skill = resolve_skill(
            command=request.command,
            skills=accepted_skills,
        )

        if resolved_skill is None:
            return {
                "message": (
                    "No matching learned skill "
                    "found."
                ),
                "command": request.command,
                "resolved_skill": None,
                "execution_plan": None,
                "execution_result": None,
            }

        skill = get_skill(
            resolved_skill.skill_id
        )

        if skill is None:
            raise HTTPException(
                status_code=404,
                detail=(
                    "Resolved skill could not "
                    "be found."
                ),
            )

        execution_plan = (
            create_execution_plan(
                command=request.command,
                skill=skill,
                resolved_skill=resolved_skill,
            )
        )

        execution_result = execute_plan(
            execution_plan
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except ServerError:
        raise HTTPException(
            status_code=503,
            detail=(
                "Gemini is temporarily unavailable. "
                "Please try again later."
            ),
        )

    saved_execution = save_execution(
        command=request.command,
        skill_id=resolved_skill.skill_id,
        skill_name=resolved_skill.skill_name,
        environment=resolved_skill.environment,
        success=execution_result.success,
        execution_plan=execution_plan.model_dump(),
        execution_result=execution_result.model_dump(),
    )

    return {
        "message": "Command processed.",
        "command": request.command,
        "resolved_skill": resolved_skill,
        "execution_plan": execution_plan,
        "execution_result": execution_result,
        "execution_history": saved_execution,
    }

@app.get("/execution-history")
def get_all_execution_history():
    return get_execution_history()

@app.get("/execution-history/{execution_id}")
def get_execution_history_item(
    execution_id: str,
):
    execution = get_execution(
        execution_id
    )

    if execution is None:
        raise HTTPException(
            status_code=404,
            detail="Execution record not found.",
        )

    return execution

@app.get("/test-gemini")
def test_gemini_connection():

    response = test_gemini()

    return {
        "response": response
    }


@app.post("/voice/start")
def start_voice_session():
    global _voice_session, _voice_task

    if _voice_task and not _voice_task.done():
        raise HTTPException(
            status_code=409,
            detail="A voice session is already running.",
        )

    _voice_session = VoiceSession()
    _voice_task = asyncio.create_task(_voice_session.run())

    return {"message": "Voice session started. Talk to CopyCat."}


@app.post("/voice/stop")
def stop_voice_session():
    global _voice_session, _voice_task

    if not _voice_task or _voice_task.done():
        raise HTTPException(
            status_code=409,
            detail="No voice session is running.",
        )

    _voice_task.cancel()

    if _voice_session and _voice_session.audio_stream:
        _voice_session.audio_stream.close()

    _voice_task = None
    _voice_session = None

    return {"message": "Voice session stopped."}