"use client";

import { useState } from "react";
import {
  acceptSkill,
  editSkill,
  rejectSkill,
  ApiError,
  type SavedSkill,
  type UploadVideoResponse,
} from "@/lib/api";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { IconCheck } from "@/components/ui/Icons";
import { Input } from "@/components/ui/Input";
import { cn } from "@/lib/utils";
import { PRIVACY_STATUS_MESSAGE } from "@/lib/privacy-settings";

type SkillStep = {
  step_number: number;
  action: string;
  description: string;
  observed_data?: Record<string, unknown> | null;
};

function parseSteps(steps: Record<string, unknown>[]): SkillStep[] {
  return steps.map((step, index) => ({
    step_number:
      typeof step.step_number === "number" ? step.step_number : index + 1,
    action: typeof step.action === "string" ? step.action : "",
    description: typeof step.description === "string" ? step.description : "",
    observed_data:
      step.observed_data && typeof step.observed_data === "object"
        ? (step.observed_data as Record<string, unknown>)
        : null,
  }));
}

function statusTone(status: string): "warning" | "success" | "error" | "neutral" {
  if (status === "accepted") return "success";
  if (status === "rejected") return "error";
  if (status === "pending") return "warning";
  return "neutral";
}

function suggestedCommand(skill: SavedSkill): string {
  return skill.name;
}

type SkillReviewCardProps = {
  skill: SavedSkill;
  onUpdate: (skill: SavedSkill) => void;
};

function SkillReviewCard({ skill, onUpdate }: SkillReviewCardProps) {
  const [editing, setEditing] = useState(false);
  const [busy, setBusy] = useState<"accept" | "reject" | "save" | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [draftName, setDraftName] = useState(skill.name);
  const [draftDescription, setDraftDescription] = useState(skill.description);
  const [draftSteps, setDraftSteps] = useState<SkillStep[]>(() =>
    parseSteps(skill.steps),
  );

  const steps = parseSteps(skill.steps);
  const isPending = skill.status === "pending";
  const isAccepted = skill.status === "accepted";

  async function handleAccept() {
    setBusy("accept");
    setError(null);
    try {
      const response = await acceptSkill(skill.id);
      onUpdate(response.skill);
    } catch (actionError) {
      setError(
        actionError instanceof ApiError
          ? actionError.message
          : "Could not accept this skill. Please try again.",
      );
    } finally {
      setBusy(null);
    }
  }

  async function handleReject() {
    setBusy("reject");
    setError(null);
    try {
      const response = await rejectSkill(skill.id);
      onUpdate(response.skill);
    } catch (actionError) {
      setError(
        actionError instanceof ApiError
          ? actionError.message
          : "Could not reject this skill. Please try again.",
      );
    } finally {
      setBusy(null);
    }
  }

  async function handleSaveEdit() {
    setBusy("save");
    setError(null);
    try {
      const response = await editSkill(skill.id, {
        name: draftName.trim(),
        description: draftDescription.trim(),
        steps: draftSteps.map((step) => ({
          step_number: step.step_number,
          action: step.action,
          description: step.description,
          observed_data: step.observed_data ?? null,
        })),
      });
      onUpdate(response.skill);
      setEditing(false);
    } catch (actionError) {
      setError(
        actionError instanceof ApiError
          ? actionError.message
          : "Could not save your changes. Please try again.",
      );
    } finally {
      setBusy(null);
    }
  }

  function startEditing() {
    setDraftName(skill.name);
    setDraftDescription(skill.description);
    setDraftSteps(parseSteps(skill.steps));
    setEditing(true);
    setError(null);
  }

  function cancelEditing() {
    setEditing(false);
    setError(null);
  }

  return (
    <li className="rounded-md border border-line bg-surface p-4">
      <div className="flex flex-wrap items-start justify-between gap-x-4 gap-y-2">
        <div className="min-w-0 flex-1">
          {editing ? (
            <Input
              value={draftName}
              onChange={(event) => setDraftName(event.target.value)}
              aria-label="Workflow name"
              className="font-medium"
            />
          ) : (
            <p className="font-medium text-ink">{skill.name}</p>
          )}
          <p className="mt-1 text-caption text-ink-muted">
            {skill.environment} · {steps.length}{" "}
            {steps.length === 1 ? "step" : "steps"} · {skill.confidence}{" "}
            confidence
          </p>
        </div>
        <Badge tone={statusTone(skill.status)}>
          {skill.status === "pending"
            ? "Pending review"
            : skill.status.charAt(0).toUpperCase() + skill.status.slice(1)}
        </Badge>
      </div>

      {editing ? (
        <textarea
          value={draftDescription}
          onChange={(event) => setDraftDescription(event.target.value)}
          aria-label="Workflow description"
          rows={3}
          className={cn(
            "mt-3 w-full rounded-md border border-line bg-surface px-4 py-3 text-small text-ink",
            "placeholder:text-ink-muted transition-colors duration-200",
            "focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent-soft",
          )}
        />
      ) : (
        <p className="mt-2 text-small text-ink-secondary">{skill.description}</p>
      )}

      <div className="mt-4 flex flex-col gap-2">
        <p className="text-caption font-medium uppercase tracking-[0.18em] text-ink-muted">
          Workflow steps
        </p>
        <ol className="flex flex-col gap-2">
          {(editing ? draftSteps : steps).map((step, index) => (
            <li
              key={step.step_number}
              className="rounded-md border border-line bg-beige px-3 py-2"
            >
              <p className="text-caption text-ink-muted">
                Step {step.step_number}
              </p>
              {editing ? (
                <textarea
                  value={draftSteps[index]?.description ?? ""}
                  onChange={(event) => {
                    const next = [...draftSteps];
                    next[index] = {
                      ...next[index],
                      description: event.target.value,
                    };
                    setDraftSteps(next);
                  }}
                  aria-label={`Step ${step.step_number} description`}
                  rows={2}
                  className={cn(
                    "mt-1 w-full rounded-md border border-line bg-surface px-3 py-2 text-small text-ink",
                    "focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent-soft",
                  )}
                />
              ) : (
                <p className="mt-0.5 text-small text-ink">{step.description}</p>
              )}
            </li>
          ))}
        </ol>
      </div>

      {error && (
        <p className="mt-3 text-small text-error" role="alert">
          {error}
        </p>
      )}

      <div className="mt-4 flex flex-wrap gap-2">
        {editing ? (
          <>
            <Button
              size="sm"
              onClick={handleSaveEdit}
              disabled={busy !== null || !draftName.trim()}
            >
              {busy === "save" ? "Saving…" : "Save changes"}
            </Button>
            <Button
              variant="secondary"
              size="sm"
              onClick={cancelEditing}
              disabled={busy !== null}
            >
              Cancel
            </Button>
          </>
        ) : (
          <>
            {isPending && (
              <>
                <Button
                  size="sm"
                  onClick={handleAccept}
                  disabled={busy !== null}
                >
                  {busy === "accept" ? "Accepting…" : "Accept skill"}
                </Button>
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={handleReject}
                  disabled={busy !== null}
                >
                  {busy === "reject" ? "Rejecting…" : "Reject"}
                </Button>
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={startEditing}
                  disabled={busy !== null}
                >
                  Edit
                </Button>
              </>
            )}
            {isAccepted && (
              <Button
                size="sm"
                href={`/app?command=${encodeURIComponent(suggestedCommand(skill))}`}
              >
                Try this skill
              </Button>
            )}
          </>
        )}
      </div>
    </li>
  );
}

/**
 * Success state of the teaching flow — Phase A (skill review + accept).
 *
 * Renders what the backend returned and lets the user accept, reject, or
 * edit candidate skills before CopyCat can run them from the dashboard.
 */
export function TeachSuccess({ result }: { result: UploadVideoResponse }) {
  const {
    analysis,
    frames_extracted,
    saved_skills,
    privacy_filter_applied,
  } = result;
  const [skills, setSkills] = useState<SavedSkill[]>(saved_skills);

  function updateSkill(updated: SavedSkill) {
    setSkills((current) =>
      current.map((skill) => (skill.id === updated.id ? updated : skill)),
    );
  }

  const acceptedSkills = skills.filter((skill) => skill.status === "accepted");

  return (
    <Card elevated className="flex flex-col gap-6 p-8">
      <div className="flex flex-col items-center gap-4 text-center">
        <span className="flex h-12 w-12 items-center justify-center rounded-full bg-accent-soft text-accent">
          <IconCheck className="h-6 w-6" />
        </span>
        <p className="text-caption font-medium uppercase tracking-[0.18em] text-ink-muted">
          Demonstration learned
        </p>
        <h2 className="font-heading text-h3 font-bold text-ink">
          {analysis.goal || "CopyCat understood your workflow"}
        </h2>
        <p className="max-w-xl text-small text-ink-secondary">
          CopyCat watched your demonstration ({frames_extracted}{" "}
          {frames_extracted === 1 ? "moment" : "moments"} examined) and broke it
          down into the steps that make up the workflow. Review each skill below
          — CopyCat can only run skills you accept.
        </p>
        {privacy_filter_applied && (
          <p
            className="max-w-xl rounded-md border border-line bg-surface px-4 py-3 text-small text-ink-secondary"
            role="status"
          >
            🔒 {PRIVACY_STATUS_MESSAGE}
          </p>
        )}
      </div>

      {skills.length > 0 ? (
        <div className="flex flex-col gap-3">
          <h3 className="text-caption font-medium uppercase tracking-[0.18em] text-ink-muted">
            Candidate skills — review before use
          </h3>
          <ul className="flex flex-col gap-3">
            {skills.map((skill) => (
              <SkillReviewCard
                key={skill.id}
                skill={skill}
                onUpdate={updateSkill}
              />
            ))}
          </ul>
        </div>
      ) : (
        <p className="rounded-md border border-line bg-surface p-4 text-small text-ink-secondary">
          CopyCat couldn&rsquo;t identify a complete multi-step workflow in this
          recording. Try re-recording the full workflow — including the
          decisions in between — and teach it again.
        </p>
      )}

      <div className="flex flex-wrap items-center justify-center gap-3 border-t border-line pt-6">
        {acceptedSkills.length > 0 && (
          <Button
            size="sm"
            href={`/app?command=${encodeURIComponent(suggestedCommand(acceptedSkills[0]))}`}
          >
            Try accepted skill
          </Button>
        )}
        <Button variant="secondary" size="sm" href="/app/teach">
          Teach another workflow
        </Button>
        <Button variant="secondary" size="sm" href="/app">
          Go to dashboard
        </Button>
      </div>
    </Card>
  );
}
