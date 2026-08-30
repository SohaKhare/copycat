import type { ComponentProps } from "react";
import { cn } from "@/lib/utils";

/**
 * Shared card — CopyCat DESIGN.md §16.
 *
 * Warm surface, thin border, 12px radius, generous padding, minimal shadow.
 * Cards must not be overused — only when grouping adds clarity.
 * Use `elevated` for elements that float above the page (modals, popovers).
 */

type CardProps = ComponentProps<"div"> & {
  elevated?: boolean;
};

export function Card({ elevated, className, ...props }: CardProps) {
  return (
    <div
      className={cn(
        "rounded-lg border border-line bg-surface",
        elevated && "shadow-soft",
        className,
      )}
      {...props}
    />
  );
}
