import type { ComponentProps } from "react";
import { cn } from "@/lib/utils";

/**
 * Shared badge — CopyCat DESIGN.md §12.
 *
 * One of the few sanctioned pill shapes (tags, status indicators, filters,
 * small badges). Tones use the muted functional colors from DESIGN.md §6.
 */

type BadgeTone = "neutral" | "accent" | "success" | "warning" | "error" | "info";

const toneStyles: Record<BadgeTone, string> = {
  neutral: "border-line bg-surface text-ink-secondary",
  accent: "border-accent-soft bg-accent-soft text-accent",
  success: "border-success/30 bg-success/10 text-success",
  warning: "border-warning/30 bg-warning/10 text-warning",
  error: "border-error/30 bg-error/10 text-error",
  info: "border-info/30 bg-info/10 text-info",
};

type BadgeProps = ComponentProps<"span"> & {
  tone?: BadgeTone;
};

export function Badge({ tone = "neutral", className, ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full border px-3 py-1 text-caption font-medium",
        toneStyles[tone],
        className,
      )}
      {...props}
    />
  );
}
