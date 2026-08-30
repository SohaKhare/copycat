"use client";

import { useEffect, useState } from "react";
import { PageHeader } from "@/components/app/PageHeader";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { IconSparkles } from "@/components/ui/Icons";
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

export default function SkillsPage() {
  const [skills, setSkills] = useState<SavedSkill[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pendingActionId, setPendingActionId] = useState<string | null>(null);

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
          {skills.map((skill) => (
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
                  <p className="mt-2 text-caption text-ink-muted">
                    {skill.steps.length} steps · confidence: {skill.confidence}
                  </p>
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
            </Card>
          ))}
        </div>
      )}
    </>
  );
}
