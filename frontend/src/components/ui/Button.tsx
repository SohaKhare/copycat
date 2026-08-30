import Link from "next/link";
import type { ComponentProps } from "react";
import { cn } from "@/lib/utils";

/**
 * Shared button — CopyCat DESIGN.md §14.
 *
 * Only two variants by design ("Avoid excessive button styles"):
 *  - primary:   burgundy background, white text, darker hover
 *  - secondary: transparent, 1px ink border, warm beige hover
 */

type ButtonVariant = "primary" | "secondary" | "inverse";
type ButtonSize = "sm" | "md" | "lg";

const baseStyles =
  "inline-flex items-center justify-center gap-2 rounded-md font-medium whitespace-nowrap transition-colors duration-200 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent disabled:pointer-events-none disabled:opacity-50";

const variantStyles: Record<ButtonVariant, string> = {
  primary: "bg-accent text-white hover:bg-accent-hover active:bg-accent-hover",
  secondary: "border border-ink bg-transparent text-ink hover:bg-beige",
  /* Inversion of primary for use on accent/dark section backgrounds
     (e.g. the final CTA section). Kept to a single extra variant to
     honor DESIGN.md §14 "Avoid excessive button styles". */
  inverse: "bg-cream text-accent hover:bg-surface",
};

const sizeStyles: Record<ButtonSize, string> = {
  sm: "h-9 px-4 text-small",
  md: "h-11 px-6 text-base",
  lg: "h-12 px-8 text-base",
};

type ButtonProps = ComponentProps<"button"> & {
  variant?: ButtonVariant;
  size?: ButtonSize;
  /** Renders a next/link when the target is internal, an <a> when external. */
  href?: string;
  external?: boolean;
};

export function Button({
  variant = "primary",
  size = "md",
  href,
  external,
  className,
  children,
  type,
  ...props
}: ButtonProps) {
  const classes = cn(baseStyles, variantStyles[variant], sizeStyles[size], className);

  if (href) {
    if (external) {
      return (
        <a
          href={href}
          target="_blank"
          rel="noopener noreferrer"
          className={classes}
        >
          {children}
        </a>
      );
    }
    return (
      <Link href={href} className={classes}>
        {children}
      </Link>
    );
  }

  return (
    <button type={type ?? "button"} className={classes} {...props}>
      {children}
    </button>
  );
}
