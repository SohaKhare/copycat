import type { ComponentProps } from "react";
import { cn } from "@/lib/utils";

/**
 * Shared text input — CopyCat DESIGN.md §15.
 *
 * Warm surface background, default border, 8px radius.
 * Focus uses a burgundy border plus a soft accent ring so the focus
 * state remains clearly visible (keyboard and pointer).
 */

const defaultStyles =
  "h-11 w-full rounded-md border border-line bg-surface px-4 text-base text-ink placeholder:text-ink-muted transition-colors duration-200 focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent-soft disabled:cursor-not-allowed disabled:opacity-50";

export function Input({ className, ...props }: ComponentProps<"input">) {
  return <input className={cn(defaultStyles, className)} {...props} />;
}
