/**
 * Backend API client — FRONTEND_SPEC.md Phase 6 (Backend Integration).
 *
 * Types mirror the existing FastAPI implementation exactly; nothing here is
 * invented. See backend/src/backend/main.py:
 *
 *   POST /upload-video   multipart field "file" (must be a video/* file)
 *     200 -> { message, video_id, original_filename, frames_extracted,
 *              analysis: { goal, observations, candidate_skills },
 *              saved_skills: [...skill rows...] }
 *     400 -> { detail }   (non-video content type, or processing ValueError)
 *     503 -> { detail }   (Gemini temporarily unavailable)
 *
 * Requests go through the same-origin `/api-backend` proxy (next.config.ts)
 * unless NEXT_PUBLIC_API_URL points directly at a CORS-enabled backend.
 */

const API_PROXY_PREFIX = "/api-backend";
const DIRECT_API_URL = process.env.NEXT_PUBLIC_API_URL ?? "";

function apiUrl(path: string): string {
  return DIRECT_API_URL
    ? `${DIRECT_API_URL}${path}`
    : `${API_PROXY_PREFIX}${path}`;
}

/** Mirrors backend.models.learning.CandidateSkillStep. */
export type CandidateSkillStep = {
  step_number: number;
  action: string;
  description: string;
  observed_data?: Record<string, unknown> | null;
};

/** Mirrors backend.models.learning.CandidateSkill. */
export type CandidateSkill = {
  id?: string | null;
  name: string;
  description: string;
  environment: string;
  steps: CandidateSkillStep[];
  confidence: string;
  requires_user_validation?: boolean;
  status?: string;
};

/** Mirrors backend.models.learning.LearningResult. */
export type LearningAnalysis = {
  goal: string;
  observations: unknown[];
  candidate_skills: CandidateSkill[];
};

/** A row created by backend.storage.skills.create_skill (Supabase insert). */
export type SavedSkill = {
  id: string;
  name: string;
  description: string;
  steps: Record<string, unknown>[];
  environment: string;
  confidence: string;
  status: string;
  tested: boolean;
  created_at?: string;
};

/** Exact 200 response of POST /upload-video. */
export type UploadVideoResponse = {
  message: string;
  video_id: string;
  original_filename: string | null;
  frames_extracted: number;
  analysis: LearningAnalysis;
  saved_skills: SavedSkill[];
};

/** Mirrors backend.models.execution.SkillParameter. */
export type SkillParameter = {
  name: string;
  value: unknown;
};

/** Mirrors backend.models.execution.ResolvedSkill. */
export type ResolvedSkill = {
  skill_id: string;
  skill_name: string;
  environment: string;
  parameters: SkillParameter[];
  match_confidence: string;
  reasoning: string;
};

/** One skill in a multi-skill resolution. */
export type ResolvedSkillItem = {
  skill_id: string;
  skill_name: string;
  environment: string;
  parameters: SkillParameter[];
  order: number;
  match_confidence: string;
};

/** Result of running one skill in a composition. */
export type SkillRunResult = {
  order: number;
  skill_id: string;
  skill_name: string;
  environment: string;
  success: boolean;
  message: string;
  execution_plan: ExecutionPlan;
  execution_result: ExecutionResult;
  execution_history?: Record<string, unknown> | null;
};

/** Mirrors backend.models.execution.ExecutionResult. */
export type ExecutionResult = {
  success: boolean;
  message: string;
  skill_id: string;
  details?: Record<string, unknown>;
};

/** Mirrors backend.models.execution.ExecutionPlanStep. */
export type ExecutionPlanStep = {
  step_number: number;
  action: string;
  description: string;
  parameters?: Record<string, unknown>;
};

/** Mirrors backend.models.execution.ExecutionPlan. */
export type ExecutionPlan = {
  skill_id: string;
  skill_name: string;
  environment: string;
  goal: string;
  parameters: SkillParameter[];
  steps: ExecutionPlanStep[];
};

/** Response of POST /skills/{id}/accept | reject and PUT /skills/{id}. */
export type SkillMutationResponse = {
  message: string;
  skill: SavedSkill;
};

/** Body for PUT /skills/{id} — mirrors backend.models.skill.EditSkillRequest. */
export type EditSkillPayload = {
  name?: string;
  description?: string;
  steps?: Record<string, unknown>[];
  environment?: string;
};

/** Response of POST /resolve-skill. */
export type ResolveSkillResponse = {
  message: string;
  command: string;
  resolved_skill: ResolvedSkill | null;
  resolved_skills: ResolvedSkillItem[];
  reasoning: string;
};

/** User-facing reply from POST /execute (Phase 1). */
export type UserReply = {
  text: string;
  speakable: string;
  modality: "text" | "voice";
};

/** Response of POST /execute. */
export type ExecuteResponse = {
  message: string;
  command: string;
  resolved_skill: ResolvedSkill | null;
  resolved_skills: ResolvedSkillItem[];
  reasoning: string;
  skill_runs: SkillRunResult[];
  execution_plan: ExecutionPlan | null;
  execution_result: ExecutionResult | null;
  execution_history?: Record<string, unknown> | null;
  /** Full UI message (mirrors execution_result.message on a normal run). */
  text: string;
  /** Short spoken sentence — null on text turns. */
  speakable: string | null;
  modality: "text" | "voice";
  /** base64 WAV of `speakable` — null on text turns or if TTS failed. */
  audio_b64: string | null;
  audio_mime: string | null;
};

/** Input to executeCommand — a bare string is the typed-command shorthand. */
export type ExecuteInput =
  | string
  | {
      command?: string;
      audio_b64?: string;
      audio_format?: string;
      modality?: "text" | "voice";
    };

/** Row from Supabase execution_history. */
export type ExecutionHistoryRecord = {
  id: string;
  command: string;
  skill_id: string;
  skill_name: string;
  environment: string;
  success: boolean;
  execution_plan: Record<string, unknown>;
  execution_result: Record<string, unknown>;
  created_at?: string;
};

/** HTTPException body from FastAPI: { detail: string }. */
export class ApiError extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

function messageFromErrorBody(body: unknown, status: number): string {
  if (body && typeof body === "object" && "detail" in body) {
    const detail = (body as { detail: unknown }).detail;
    if (typeof detail === "string") return detail;
    // FastAPI validation errors: detail is an array of { loc, msg, ... }.
    if (Array.isArray(detail)) {
      const parts = detail
        .map((item) =>
          item && typeof item === "object" && "msg" in item
            ? String((item as { msg: unknown }).msg)
            : null,
        )
        .filter(Boolean);
      if (parts.length) return parts.join("; ");
    }
  }
  return `The request failed with status ${status}.`;
}

async function requestJson<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  let response: Response;
  try {
    response = await fetch(apiUrl(path), {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    });
  } catch {
    throw new ApiError(
      0,
      "CopyCat couldn't reach the server. Make sure the backend is running, then try again.",
    );
  }

  let body: unknown = null;
  try {
    body = await response.json();
  } catch {
    body = null;
  }

  if (!response.ok) {
    if (response.status === 503) {
      throw new ApiError(
        503,
        messageFromErrorBody(body, response.status) ||
          "CopyCat's analysis engine is temporarily unavailable. Please try again shortly.",
      );
    }
    throw new ApiError(
      response.status,
      messageFromErrorBody(body, response.status),
    );
  }

  return body as T;
}

export function getSkills(): Promise<SavedSkill[]> {
  return requestJson<SavedSkill[]>("/skills");
}

export function getSkill(skillId: string): Promise<SavedSkill> {
  return requestJson<SavedSkill>(`/skills/${skillId}`);
}

export function acceptSkill(skillId: string): Promise<SkillMutationResponse> {
  return requestJson<SkillMutationResponse>(`/skills/${skillId}/accept`, {
    method: "POST",
  });
}

export function rejectSkill(skillId: string): Promise<SkillMutationResponse> {
  return requestJson<SkillMutationResponse>(`/skills/${skillId}/reject`, {
    method: "POST",
  });
}

export function editSkill(
  skillId: string,
  payload: EditSkillPayload,
): Promise<SkillMutationResponse> {
  return requestJson<SkillMutationResponse>(`/skills/${skillId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function resolveSkill(command: string): Promise<ResolveSkillResponse> {
  return requestJson<ResolveSkillResponse>("/resolve-skill", {
    method: "POST",
    body: JSON.stringify({ command }),
  });
}

export function executeCommand(input: ExecuteInput): Promise<ExecuteResponse> {
  const body =
    typeof input === "string"
      ? { command: input, modality: "text" as const }
      : { modality: "text" as const, ...input };

  return requestJson<ExecuteResponse>("/execute", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function getExecutionHistory(): Promise<ExecutionHistoryRecord[]> {
  return requestJson<ExecutionHistoryRecord[]>("/execution-history");
}

/**
 * Upload a demonstration video with real progress reporting.
 *
 * XMLHttpRequest is used (instead of fetch) because it exposes upload
 * progress events, which the spec asks to surface when real progress data
 * is available. `onProgress` receives 0–100 when the total size is known;
 * when it is not, progress stays null and the UI shows an indeterminate
 * state instead of a fake percentage.
 */
export function uploadVideo(
  file: File,
  options: {
    onProgress?: (percent: number | null) => void;
    signal?: AbortSignal;
  } = {},
): Promise<UploadVideoResponse> {
  const { onProgress, signal } = options;

  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open("POST", apiUrl("/upload-video"));

    const onAbort = () => xhr.abort();
    signal?.addEventListener("abort", onAbort);

    function cleanup() {
      signal?.removeEventListener("abort", onAbort);
    }

    xhr.upload.onprogress = (event) => {
      if (!onProgress) return;
      if (event.lengthComputable && event.total > 0) {
        onProgress(Math.round((event.loaded / event.total) * 100));
      } else {
        onProgress(null);
      }
    };

    xhr.onload = () => {
      cleanup();

      let body: unknown = null;
      try {
        body = JSON.parse(xhr.responseText) as unknown;
      } catch {
        body = null;
      }

      if (xhr.status >= 200 && xhr.status < 300) {
        if (
          body &&
          typeof body === "object" &&
          "video_id" in body &&
          "analysis" in body
        ) {
          resolve(body as UploadVideoResponse);
        } else {
          reject(
            new ApiError(
              xhr.status,
              "The server responded with an unexpected format. Please try again.",
            ),
          );
        }
        return;
      }

      if (xhr.status === 503) {
        reject(
          new ApiError(
            503,
            messageFromErrorBody(body, xhr.status) ||
              "CopyCat's analysis engine is temporarily unavailable. Please try again shortly.",
          ),
        );
        return;
      }

      reject(new ApiError(xhr.status, messageFromErrorBody(body, xhr.status)));
    };

    xhr.onerror = () => {
      cleanup();
      reject(
        new ApiError(
          0,
          "CopyCat couldn't reach the server. Make sure the backend is running, then try again.",
        ),
      );
    };

    xhr.onabort = () => {
      cleanup();
      reject(new DOMException("Upload cancelled.", "AbortError"));
    };

    const formData = new FormData();
    formData.append("file", file, file.name);
    xhr.send(formData);
  });
}

/**
 * Back-compat alias: an earlier revision of this file exported a second,
 * duplicate client where the execution-history row type was named
 * `ExecutionHistoryItem`. Kept as an alias so existing imports keep working.
 */
export type ExecutionHistoryItem = ExecutionHistoryRecord;
