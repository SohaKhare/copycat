"use client";

import { useEffect, useState, type ReactNode } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { IconMenu, IconX } from "@/components/ui/Icons";
import { SidebarNav } from "./SidebarNav";

/**
 * Application shell — FRONTEND_SPEC.md Phase 5.
 *
 * Desktop (lg+): fixed-width warm beige sidebar (DESIGN.md §2) beside a
 * scrolling main content area. Below lg: a compact top bar opens a
 * slide-over navigation drawer, dismissed by the close button, overlay
 * click, or Escape. The drawer closes automatically on navigation.
 */
export function AppShell({ children }: { children: ReactNode }) {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const pathname = usePathname();
  const [prevPathname, setPrevPathname] = useState(pathname);

  // Close the drawer whenever navigation happens (including back/forward).
  // Adjusting state during render is the React-recommended alternative to
  // synchronizing an effect on every pathname change.
  if (pathname !== prevPathname) {
    setPrevPathname(pathname);
    setDrawerOpen(false);
  }

  // Dismiss the drawer with Escape.
  useEffect(() => {
    if (!drawerOpen) return;
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") setDrawerOpen(false);
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [drawerOpen]);

  // Prevent background scrolling while the drawer is open.
  useEffect(() => {
    document.body.style.overflow = drawerOpen ? "hidden" : "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [drawerOpen]);

  return (
    <div className="flex w-full flex-1 flex-col lg:flex-row">
      {/* Mobile top bar */}
      <header className="sticky top-0 z-40 flex items-center justify-between border-b border-line bg-cream/90 px-4 py-3 backdrop-blur-md lg:hidden">
        <Link
          href="/app"
          className="font-heading text-lg font-bold tracking-tight text-ink"
        >
          CopyCat
        </Link>
        <button
          type="button"
          onClick={() => setDrawerOpen(true)}
          aria-label="Open navigation"
          aria-expanded={drawerOpen}
          className="rounded-md p-2 text-ink transition-colors duration-200 hover:bg-beige"
        >
          <IconMenu className="h-6 w-6" />
        </button>
      </header>

      {/* Desktop sidebar */}
      <aside className="sticky top-0 hidden h-dvh w-64 shrink-0 flex-col border-r border-line bg-beige lg:flex">
        <Link
          href="/app"
          className="border-b border-line px-6 py-5 font-heading text-xl font-bold tracking-tight text-ink transition-colors duration-200 hover:text-accent"
        >
          CopyCat
        </Link>
        <SidebarNav className="flex flex-1 flex-col" />
      </aside>

      {/* Mobile navigation drawer */}
      {drawerOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div
            className="absolute inset-0 bg-ink/40"
            aria-hidden="true"
            onClick={() => setDrawerOpen(false)}
          />
          <div
            role="dialog"
            aria-modal="true"
            aria-label="Application navigation"
            className="absolute inset-y-0 left-0 flex w-72 max-w-[85vw] flex-col border-r border-line bg-beige shadow-soft"
          >
            <div className="flex items-center justify-between border-b border-line px-5 py-4">
              <span className="font-heading text-lg font-bold tracking-tight text-ink">
                CopyCat
              </span>
              <button
                type="button"
                onClick={() => setDrawerOpen(false)}
                aria-label="Close navigation"
                className="rounded-md p-2 text-ink transition-colors duration-200 hover:bg-surface"
              >
                <IconX className="h-5 w-5" />
              </button>
            </div>
            <SidebarNav
              className="flex flex-1 flex-col"
              onNavigate={() => setDrawerOpen(false)}
            />
          </div>
        </div>
      )}

      {/* Main content area */}
      <main className="min-w-0 flex-1">
        <div className="mx-auto w-full max-w-5xl px-6 py-10 md:px-8 md:py-14">
          {children}
        </div>
      </main>
    </div>
  );
}
