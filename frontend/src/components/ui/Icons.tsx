import type { ComponentProps } from "react";
import { cn } from "@/lib/utils";

/**
 * Inline SVG icon set — CopyCat DESIGN.md §24–25.
 *
 * Deliberately dependency-free (no icon library). All icons share one
 * visual style: 24×24 viewBox, 1.5px strokes, round caps/joins,
 * currentColor, fill="none". Size via className (defaults to 20px).
 */

type IconProps = Omit<ComponentProps<"svg">, "children">;

function IconBase({ className, ...props }: IconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.5}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      className={cn("h-5 w-5 shrink-0", className)}
      {...props}
    />
  );
}

export function IconDashboard(props: IconProps) {
  return (
    <IconBase {...props}>
      <rect x="3" y="3" width="7" height="9" rx="1" />
      <rect x="14" y="3" width="7" height="5" rx="1" />
      <rect x="14" y="12" width="7" height="9" rx="1" />
      <rect x="3" y="16" width="7" height="5" rx="1" />
    </IconBase>
  );
}

export function IconUpload(props: IconProps) {
  return (
    <IconBase {...props}>
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
      <path d="m17 8-5-5-5 5" />
      <path d="M12 3v12" />
    </IconBase>
  );
}

export function IconSparkles(props: IconProps) {
  return (
    <IconBase {...props}>
      <path d="M12 3l2.1 5.4 5.4 2.1-5.4 2.1L12 18l-2.1-5.4-5.4-2.1 5.4-2.1L12 3Z" />
    </IconBase>
  );
}

export function IconActivity(props: IconProps) {
  return (
    <IconBase {...props}>
      <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
    </IconBase>
  );
}

export function IconSliders(props: IconProps) {
  return (
    <IconBase {...props}>
      <path d="M21 4h-7" />
      <path d="M10 4H3" />
      <path d="M21 12h-9" />
      <path d="M8 12H3" />
      <path d="M21 20h-5" />
      <path d="M12 20H3" />
      <path d="M14 2v4" />
      <path d="M8 10v4" />
      <path d="M16 18v4" />
    </IconBase>
  );
}

export function IconMic(props: IconProps) {
  return (
    <IconBase {...props}>
      <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z" />
      <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
      <path d="M12 19v3" />
    </IconBase>
  );
}

export function IconArrowRight(props: IconProps) {
  return (
    <IconBase {...props}>
      <path d="M5 12h14" />
      <path d="m13 6 6 6-6 6" />
    </IconBase>
  );
}

export function IconCheck(props: IconProps) {
  return (
    <IconBase {...props}>
      <path d="m5 12 5 5L20 7" />
    </IconBase>
  );
}

export function IconMenu(props: IconProps) {
  return (
    <IconBase {...props}>
      <path d="M4 7h16" />
      <path d="M4 12h16" />
      <path d="M4 17h16" />
    </IconBase>
  );
}

export function IconX(props: IconProps) {
  return (
    <IconBase {...props}>
      <path d="m6 6 12 12" />
      <path d="M18 6 6 18" />
    </IconBase>
  );
}

export function IconVideo(props: IconProps) {
  return (
    <IconBase {...props}>
      <rect x="2.5" y="6" width="14" height="12" rx="2" />
      <path d="m16.5 10.5 5-3v9l-5-3" />
    </IconBase>
  );
}

export function IconFile(props: IconProps) {
  return (
    <IconBase {...props}>
      <path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z" />
      <path d="M14 3v5h5" />
    </IconBase>
  );
}
