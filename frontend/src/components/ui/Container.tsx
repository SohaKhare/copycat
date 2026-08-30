import type { ComponentProps } from "react";
import { cn } from "@/lib/utils";

/**
 * Page-width wrapper — CopyCat DESIGN.md §1–2.
 *
 * Centralizes horizontal rhythm so sections stay consistent.
 * Pass a className to extend or override (e.g. narrower measures).
 */

const defaultStyles = "mx-auto w-full max-w-6xl px-6 md:px-8";

export function Container({ className, ...props }: ComponentProps<"div">) {
  return <div className={cn(defaultStyles, className)} {...props} />;
}
