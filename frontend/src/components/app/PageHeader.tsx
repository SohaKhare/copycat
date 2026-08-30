import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

/**
 * Page header — FRONTEND_SPEC.md Phase 5.
 *
 * Every major application page opens with a title, a short supporting
 * description when useful, and an optional contextual action.
 */

type PageHeaderProps = {
  title: string;
  description?: string;
  action?: ReactNode;
  className?: string;
};

export function PageHeader({
  title,
  description,
  action,
  className,
}: PageHeaderProps) {
  return (
    <header
      className={cn(
        "mb-10 flex flex-wrap items-end justify-between gap-x-8 gap-y-4",
        className,
      )}
    >
      <div className="max-w-2xl">
        <h1 className="font-heading text-h3 font-bold tracking-tight text-ink">
          {title}
        </h1>
        {description && (
          <p className="mt-2 text-base text-ink-secondary">{description}</p>
        )}
      </div>
      {action && (
        <div className="flex shrink-0 items-center gap-3">{action}</div>
      )}
    </header>
  );
}
