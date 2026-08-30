"use client";

import { useEffect, useState } from "react";
import { PageHeader } from "@/components/app/PageHeader";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { IconActivity } from "@/components/ui/Icons";
import { ApiError, getExecutionHistory, type ExecutionHistoryItem } from "@/lib/api";

export default function ActivityPage() {
  const [history, setHistory] = useState<ExecutionHistoryItem[] | null>(null);
  const [error, setError] = useState<string | null>(null);

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
          {history.map((item) => (
            <li key={item.id} className="flex items-start gap-3 py-4">
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
                  {item.created_at ? ` · ${new Date(item.created_at).toLocaleString()}` : ""}
                </p>
              </div>
            </li>
          ))}
        </ul>
      )}
    </>
  );
}
