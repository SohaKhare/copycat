"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ComponentType } from "react";
import {
  IconActivity,
  IconDashboard,
  IconSliders,
  IconSparkles,
  IconUpload,
} from "@/components/ui/Icons";
import { cn } from "@/lib/utils";

/**
 * Application sidebar navigation — FRONTEND_SPEC.md Phase 5.
 *
 * Primary outcomes only (Dashboard, Teach CopyCat, My Skills, Activity),
 * with Settings separated below a divider. Atomic actions deliberately
 * stay out of navigation — CopyCat is centered on workflows and outcomes.
 *
 * Active state uses the accent-soft selected background from
 * DESIGN.md §5: clearly visible without being overly bright.
 */

type NavItem = {
  href: string;
  label: string;
  icon: ComponentType<{ className?: string }>;
};

const PRIMARY_ITEMS: NavItem[] = [
  { href: "/app", label: "Dashboard", icon: IconDashboard },
  { href: "/app/teach", label: "Teach CopyCat", icon: IconUpload },
  { href: "/app/skills", label: "My Skills", icon: IconSparkles },
  { href: "/app/activity", label: "Activity", icon: IconActivity },
];

const SETTINGS_ITEM: NavItem = {
  href: "/app/settings",
  label: "Settings",
  icon: IconSliders,
};

function NavLink({
  item,
  active,
  onNavigate,
}: {
  item: NavItem;
  active: boolean;
  onNavigate?: () => void;
}) {
  const Icon = item.icon;
  return (
    <Link
      href={item.href}
      onClick={onNavigate}
      aria-current={active ? "page" : undefined}
      className={cn(
        "flex items-center gap-3 rounded-md px-3 py-2 text-small font-medium transition-colors duration-200",
        active
          ? "bg-accent-soft text-accent"
          : "text-ink-secondary hover:bg-surface hover:text-ink",
      )}
    >
      <Icon className="h-[18px] w-[18px]" />
      {item.label}
    </Link>
  );
}

export function SidebarNav({
  onNavigate,
  className,
}: {
  /** Called after a link is clicked — closes the mobile drawer. */
  onNavigate?: () => void;
  className?: string;
}) {
  const pathname = usePathname();

  // Exact match for /app so it isn't active on /app/teach etc.
  const isActive = (href: string) =>
    href === "/app" ? pathname === "/app" : pathname.startsWith(href);

  return (
    <nav aria-label="Application" className={cn("flex flex-col", className)}>
      <ul className="flex flex-col gap-1 p-4">
        {PRIMARY_ITEMS.map((item) => (
          <li key={item.href}>
            <NavLink
              item={item}
              active={isActive(item.href)}
              onNavigate={onNavigate}
            />
          </li>
        ))}
      </ul>
      <div className="mt-auto border-t border-line p-4">
        <ul className="flex flex-col gap-1">
          <li>
            <NavLink
              item={SETTINGS_ITEM}
              active={isActive(SETTINGS_ITEM.href)}
              onNavigate={onNavigate}
            />
          </li>
        </ul>
      </div>
    </nav>
  );
}
