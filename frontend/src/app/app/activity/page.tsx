"use client";

import { useEffect, useState } from "react";
import { PageHeader } from "@/components/app/PageHeader";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { IconActivity, IconArrowRight } from "@/components/ui/Icons";
import { Markdown } from "@/components/ui/Markdown";
import { cn } from "@/lib/utils";
import { ApiError, getExecutionHistory, type ExecutionHistoryItem } from "@/lib/api";

function resultMessage(item: ExecutionHistoryItem): string {
  const result = item.execution_result;
  if (
    result &&
    typeof result === "object" &&
    typeof (result as { message?: unknown }).message === "string"
  ) {
    return (result as { message: string }).message;
  }
  return "No response was recorded for this run.";
}

export default function ActivityPage() {
  const [history, setHistory] = useState<ExecutionHistoryItem[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [openIds, setOpenIds] = useState<Set<string>>(new Set());

  const toggle = (id: string) =>
    setOpenIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });

  useEffect(() => {
    getExecutionHistory()
      .then(setHistory)
      .catch((err) =>
        setError(err instanceof ApiError ? err.message : "Failed to load activity."),
      );
  }, []);

  return (
    <>
      <PageHeader
        title="Activity"
        description="Review learning and execution activity."
      />

      {error && (
        <Card className="mb-6 border-error/30 bg-error/10 p-4 text-small text-error">
          {error}
        </Card>
      )}

      {history === null && !error && (
        <p className="text-small text-ink-secondary">Loading activity…</p>
      )}

      {history !== null && history.length === 0 && (
        <Card className="flex flex-col items-center gap-4 p-10 text-center">
          <span className="flex h-12 w-12 items-center justify-center rounded-full bg-accent-soft text-accent">
            <IconActivity className="h-6 w-6" />
          </span>
          <h2 className="font-heading text-h3 font-bold text-ink">
            No activity yet
          </h2>
          <p className="max-w-md text-small text-ink-secondary">
            Once CopyCat learns a workflow or runs one for you, every event
            shows up here so you can review what happened.
          </p>
          <Button variant="secondary" size="sm" href="/app/teach">
            Teach CopyCat your first workflow
          </Button>
        </Card>
      )}

      {history !== null && history.length > 0 && (
        <ul className="flex flex-col divide-y divide-line">
          {history.map((item) => {
            const open = openIds.has(item.id);
            return (
              <li key={item.id} className="py-2">
                <button
                  type="button"
                  onClick={() => toggle(item.id)}
                  aria-expanded={open}
                  className="flex w-full items-start gap-3 py-2 text-left"
                >
                  <Badge tone={item.success ? "success" : "error"}>
                    {item.success ? "Success" : "Failed"}
                  </Badge>
                  <div className="min-w-0 flex-1">
                    <p className="text-small text-ink">
                      Ran <span className="font-medium">{item.skill_name}</span>{" "}
                      for &ldquo;{item.command}&rdquo;
                    </p>
                    <p className="mt-1 text-caption text-ink-muted">
                      {item.environment}
                      {item.created_at
                        ? ` · ${new Date(item.created_at).toLocaleString()}`
                        : ""}
                    </p>
                  </div>
                  <IconArrowRight
                    className={cn(
                      "mt-1 h-4 w-4 shrink-0 text-ink-muted transition-transform duration-200",
                      open && "rotate-90",
                    )}
                  />
                </button>

                {open && (
                  <div className="mb-3 ml-[4.75rem] rounded-md border border-line bg-surface p-4">
                    <Markdown className="text-small text-ink-secondary">
                      {resultMessage(item)}
                    </Markdown>
                  </div>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </>
  );
}
