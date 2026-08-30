import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

/**
 * Shared section heading — eyebrow label + display title.
 *
 * Used by landing page sections for a consistent editorial hierarchy.
 * `dark` switches the palette for sections on the ink background.
 */

type SectionHeadingProps = {
  eyebrow: string;
  title: ReactNode;
  dark?: boolean;
  className?: string;
};

export function SectionHeading({
  eyebrow,
  title,
  dark,
  className,
}: SectionHeadingProps) {
  return (
    <div className={cn("flex flex-col gap-4", className)}>
      <p
        className={cn(
          "font-mono text-small font-medium uppercase tracking-[0.3em]",
          dark ? "text-cream/60" : "text-ink-muted",
        )}
      >
        {eyebrow}
      </p>
      <h2
        className={cn(
          "font-heading text-h2 font-bold",
          dark ? "text-cream" : "text-ink",
        )}
      >
        {title}
      </h2>
    </div>
  );
}
