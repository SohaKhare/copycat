"use client";

import { useEffect, useState } from "react";
import { PageHeader } from "@/components/app/PageHeader";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { IconArrowRight, IconSparkles } from "@/components/ui/Icons";
import { cn } from "@/lib/utils";
import {
  acceptSkill,
  ApiError,
  getSkills,
  rejectSkill,
  type SavedSkill,
} from "@/lib/api";

const STATUS_TONE: Record<string, "success" | "warning" | "neutral"> = {
  accepted: "success",
  pending: "warning",
  rejected: "neutral",
};

type SkillStep = { step_number: number; action: string; description: string };

function parseSteps(raw: Record<string, unknown>[]): SkillStep[] {
  return raw.map((step, index) => ({
    step_number:
      typeof step.step_number === "number" ? step.step_number : index + 1,
    action: typeof step.action === "string" ? step.action : "",
    description: typeof step.description === "string" ? step.description : "",
  }));
}

export default function SkillsPage() {
  const [skills, setSkills] = useState<SavedSkill[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pendingActionId, setPendingActionId] = useState<string | null>(null);
  const [openIds, setOpenIds] = useState<Set<string>>(new Set());

  const toggle = (id: string) =>
    setOpenIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });

  useEffect(() => {
    getSkills()
      .then(setSkills)
      .catch((err) =>
        setError(err instanceof ApiError ? err.message : "Failed to load skills."),
      );
  }, []);

  async function handleAccept(id: string) {
    setPendingActionId(id);
    try {
      const { skill } = await acceptSkill(id);
      setSkills((prev) => prev?.map((s) => (s.id === id ? skill : s)) ?? null);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to accept skill.");
    } finally {
      setPendingActionId(null);
    }
  }

  async function handleReject(id: string) {
    setPendingActionId(id);
    try {
      const { skill } = await rejectSkill(id);
      setSkills((prev) => prev?.map((s) => (s.id === id ? skill : s)) ?? null);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to reject skill.");
    } finally {
      setPendingActionId(null);
    }
  }

  return (
    <>
      <PageHeader
        title="My Skills"
        description="Workflows CopyCat has learned from you."
      />

      {error && (
        <Card className="mb-6 border-error/30 bg-error/10 p-4 text-small text-error">
          {error}
        </Card>
      )}

      {skills === null && !error && (
        <p className="text-small text-ink-secondary">Loading skills…</p>
      )}

      {skills !== null && skills.length === 0 && (
        <Card className="flex flex-col items-center gap-4 p-10 text-center">
          <span className="flex h-12 w-12 items-center justify-center rounded-full bg-accent-soft text-accent">
            <IconSparkles className="h-6 w-6" />
          </span>
          <h2 className="font-heading text-h3 font-bold text-ink">No skills yet</h2>
          <p className="max-w-md text-small text-ink-secondary">
            Teach CopyCat a workflow by showing it a demonstration. Every skill
            you teach appears here, ready to run from a single command.
          </p>
          <Button size="sm" href="/app/teach">
            Teach CopyCat
          </Button>
        </Card>
      )}

      {skills !== null && skills.length > 0 && (
        <div className="flex flex-col gap-4">
          {skills.map((skill) => {
            const open = openIds.has(skill.id);
            const steps = parseSteps(skill.steps);
            return (
              <Card key={skill.id} className="p-6">
                <div className="flex flex-wrap items-start justify-between gap-4">
                  <div className="min-w-0">
                    <div className="flex flex-wrap items-center gap-2">
                      <h2 className="font-heading text-base font-bold text-ink">
                        {skill.name}
                      </h2>
                      <Badge tone={STATUS_TONE[skill.status] ?? "neutral"}>
                        {skill.status}
                      </Badge>
                      <Badge tone="accent">{skill.environment}</Badge>
                    </div>
                    <p className="mt-1 text-small text-ink-secondary">
                      {skill.description}
                    </p>
                    <button
                      type="button"
                      onClick={() => toggle(skill.id)}
                      aria-expanded={open}
                      className="mt-2 flex items-center gap-1.5 text-caption text-ink-muted transition-colors hover:text-ink"
                    >
                      <IconArrowRight
                        className={cn(
                          "h-3.5 w-3.5 transition-transform duration-200",
                          open && "rotate-90",
                        )}
                      />
                      {steps.length} steps · confidence: {skill.confidence}
                    </button>
                  </div>

                  {skill.status === "pending" && (
                    <div className="flex shrink-0 gap-2">
                      <Button
                        size="sm"
                        disabled={pendingActionId === skill.id}
                        onClick={() => handleAccept(skill.id)}
                      >
                        Accept
                      </Button>
                      <Button
                        size="sm"
                        variant="secondary"
                        disabled={pendingActionId === skill.id}
                        onClick={() => handleReject(skill.id)}
                      >
                        Reject
                      </Button>
                    </div>
                  )}
                </div>

                {open && (
                  <ol className="mt-4 flex flex-col gap-2 border-t border-line pt-4">
                    {steps.map((step) => (
                      <li
                        key={step.step_number}
                        className="flex gap-3 text-small"
                      >
                        <span className="shrink-0 tabular-nums text-caption text-ink-muted">
                          {step.step_number}.
                        </span>
                        <span className="text-ink-secondary">
                          <span className="font-medium text-ink">
                            {step.action || "step"}
                          </span>
                          {step.description ? ` — ${step.description}` : ""}
                        </span>
                      </li>
                    ))}
                    {steps.length === 0 && (
                      <li className="text-small text-ink-muted">
                        No steps recorded for this skill.
                      </li>
                    )}
                  </ol>
                )}
              </Card>
            );
          })}
        </div>
      )}
    </>
  );
}
