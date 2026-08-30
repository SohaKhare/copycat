import asyncio
import base64
import os
from asyncio import to_thread
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from google.genai.errors import ClientError, ServerError

from backend.logging_setup import log
from backend.voice.command_bridge import run_command
from backend.voice.live_agent import VoiceSession

from backend.ai.gemini import analyze_frames, test_gemini
from backend.ai.skill_resolver import resolve_skills
from backend.ai.voice import (
    summarize_for_speech,
    synthesize_speech,
    transcribe_command,
)

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
from backend.video.privacy import apply_privacy_filter

from backend.storage.execution_history import (
    get_execution,
    get_execution_history,
)
from backend.executors.browser import prewarm_browser_session
from backend.env_config import get_cors_allowed_origins


app = FastAPI(
    title="CopyCat API",
    description="Teach AI by showing.",
    version="0.3.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

FRAMES_DIR = Path("frames")
FRAMES_DIR.mkdir(exist_ok=True)

_voice_session: VoiceSession | None = None
_voice_task: asyncio.Task | None = None

log.info("CopyCat API starting up")


@app.exception_handler(HTTPException)
async def _log_http_exception(request: Request, exc: HTTPException):
    level = log.warning if exc.status_code < 500 else log.error
    level(
        "%s %s -> %s: %s",
        request.method,
        request.url.path,
        exc.status_code,
        exc.detail,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=getattr(exc, "headers", None),
    )


@app.exception_handler(Exception)
async def _log_unhandled_exception(request: Request, exc: Exception):
    log.exception(
        "UNHANDLED exception on %s %s",
        request.method,
        request.url.path,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error - see log.txt."},
    )


@app.on_event("startup")
async def startup_prewarm_browser() -> None:
    if os.getenv("BROWSER_PREWARM", "").lower() == "true":
        await to_thread(prewarm_browser_session)


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


def _parse_privacy_filter_flag(value: str) -> bool:
    return value.strip().lower() not in ("false", "0", "no", "off")


@app.post("/upload-video")
async def upload_video(
    file: UploadFile = File(...),
    privacy_filter: str = Form(default="true"),
):

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

    privacy_filter_enabled = _parse_privacy_filter_flag(privacy_filter)

    log.info(
        "/upload-video %s (%s bytes, privacy_filter=%s)",
        file.filename,
        len(contents),
        privacy_filter_enabled,
    )

    try:
        frames = await to_thread(
            extract_frames,
            video_path=file_path,
            output_dir=video_frames_dir,
            interval_seconds=1.0,
        )

        frames, privacy_result = await to_thread(
            apply_privacy_filter,
            frames,
            enabled=privacy_filter_enabled,
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
        log.warning("/upload-video rejected %s: %s", file.filename, error)
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except ServerError:
        log.error("/upload-video: Gemini unavailable", exc_info=True)
        raise HTTPException(
            status_code=503,
            detail=(
                "Gemini is temporarily unavailable. "
                "Please try again later."
            ),
        )

    except Exception:
        log.exception("/upload-video crashed for %s", file.filename)
        raise HTTPException(
            status_code=500,
            detail="Video processing failed unexpectedly - see log.txt.",
        )

    log.info(
        "/upload-video OK %s -> %d frame(s), %d candidate skill(s)",
        file.filename,
        len(frames),
        len(saved_skills),
    )

    return {
        "message": "Video analyzed and candidate skill saved successfully!",
        "video_id": video_id,
        "original_filename": file.filename,
        "frames_extracted": len(frames),
        "privacy_filter_applied": privacy_result.applied,
        "privacy_regions_redacted": privacy_result.regions_redacted,
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

    if not request.command:
        raise HTTPException(
            status_code=400,
            detail="Provide a text command for skill resolution.",
        )

    try:
        resolution = resolve_skills(
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

    if resolution is None or not resolution.skills:
        return {
            "message": "No matching learned skill found.",
            "command": request.command,
            "resolved_skill": None,
            "resolved_skills": [],
            "reasoning": "",
        }

    first_skill = resolution.skills[0].to_resolved_skill(
        reasoning=resolution.reasoning
    )

    return {
        "message": "Matching skill found successfully.",
        "command": request.command,
        "resolved_skill": first_skill,
        "resolved_skills": resolution.skills,
        "reasoning": resolution.reasoning,
    }


_QUOTA_MESSAGE = (
    "Gemini's rate limit / free-tier quota is exhausted right now. "
    "Wait ~30 seconds and try again, or add a second GEMINI_API_KEY_2 in .env."
)


def _voice_fields(
    text: str,
    modality: str,
    speakable: str | None = None,
) -> dict:
    """
    Build the text/speakable/audio part of an /execute reply.

    Only voice turns get a spoken reply ("speak only on voice turns"). A TTS
    failure degrades to text - it never fails the command.
    """

    if modality != "voice":
        return {
            "text": text,
            "speakable": None,
            "modality": modality,
            "audio_b64": None,
            "audio_mime": None,
        }

    try:
        speakable_text = speakable or summarize_for_speech(text)
        wav_bytes, audio_mime = synthesize_speech(speakable_text)

        return {
            "text": text,
            "speakable": speakable_text,
            "modality": modality,
            "audio_b64": base64.b64encode(wav_bytes).decode(),
            "audio_mime": audio_mime,
        }

    except Exception:
        log.exception("voice reply (speakable/TTS) failed; returning text only")
        return {
            "text": text,
            "speakable": (speakable or text)[:200],
            "modality": modality,
            "audio_b64": None,
            "audio_mime": None,
        }


@app.post("/execute")
def execute_user_command(
    request: ExecuteRequest,
):
    if request.audio_b64:
        try:
            audio = base64.b64decode(request.audio_b64)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=400,
                detail="audio_b64 is not valid base64.",
            )

        try:
            command = transcribe_command(
                audio,
                f"audio/{request.audio_format}",
            )
        except ClientError as error:
            if error.code == 429:
                log.warning("/execute transcription: quota/rate limit hit")
                raise HTTPException(
                    status_code=429,
                    detail=_QUOTA_MESSAGE,
                )
            log.exception("/execute transcription: client error")
            raise HTTPException(
                status_code=400,
                detail="Could not transcribe the audio.",
            )
        except ServerError:
            log.error("/execute transcription: Gemini unavailable", exc_info=True)
            raise HTTPException(
                status_code=503,
                detail=(
                    "Gemini is temporarily unavailable. "
                    "Please try again later."
                ),
            )
        except Exception:
            log.exception(
                "/execute transcription failed (audio_format=%s)",
                request.audio_format,
            )
            raise HTTPException(
                status_code=400,
                detail="Could not transcribe the audio.",
            )
    else:
        command = request.command

    if not command:
        raise HTTPException(
            status_code=400,
            detail="Could not make out a command.",
        )

    log.info("/execute [%s] command=%r", request.modality, command)

    accepted_skills = get_accepted_skills()

    if not accepted_skills:
        raise HTTPException(
            status_code=404,
            detail="No accepted skills found.",
        )

    try:
        pipeline_result = run_command(
            command=command,
            modality=request.modality,
        )

    except HTTPException:
        raise

    except ClientError as error:
        if getattr(error, "code", None) == 429:
            log.warning("/execute: quota/rate limit hit (command=%r)", command)
            raise HTTPException(status_code=429, detail=_QUOTA_MESSAGE)
        log.exception("/execute: Gemini client error (command=%r)", command)
        raise HTTPException(status_code=400, detail=str(error))

    except ValueError as error:
        log.warning(
            "/execute plan/exec ValueError for command=%r: %s", command, error
        )
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except ServerError:
        log.error(
            "/execute plan/exec: Gemini unavailable (command=%r)",
            command,
            exc_info=True,
        )
        raise HTTPException(
            status_code=503,
            detail=(
                "Gemini is temporarily unavailable. "
                "Please try again later."
            ),
        )

    except Exception:
        log.exception("/execute plan/exec crashed for command=%r", command)
        raise HTTPException(
            status_code=500,
            detail="Execution failed unexpectedly - see log.txt.",
        )

    reply = pipeline_result.reply
    voice_payload = _voice_fields(
        reply.text,
        request.modality,
        speakable=reply.speakable,
    )

    if pipeline_result.resolved_skill is None:
        log.warning("/execute NO MATCH for command=%r", command)
    elif pipeline_result.execution_result and pipeline_result.execution_result.success:
        log.info(
            "/execute PASS skill=%r command=%r",
            pipeline_result.resolved_skill.skill_name,
            command,
        )
    elif pipeline_result.resolved_skill is not None:
        log.warning(
            "/execute FAIL skill=%r command=%r",
            pipeline_result.resolved_skill.skill_name,
            command,
        )

    return {
        "message": "Command processed.",
        "command": command,
        "resolved_skill": pipeline_result.resolved_skill,
        "resolved_skills": pipeline_result.resolved_skills,
        "reasoning": pipeline_result.reasoning,
        "skill_runs": pipeline_result.skill_runs,
        "execution_plan": pipeline_result.execution_plan,
        "execution_result": pipeline_result.execution_result,
        "execution_history": pipeline_result.execution_history,
        "reply": reply,
        "stopped_at_order": pipeline_result.stopped_at_order,
        **voice_payload,
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
