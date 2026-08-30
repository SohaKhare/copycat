import { AppShell } from "@/components/app/AppShell";

/**
 * Application layout — FRONTEND_SPEC.md Phase 5.
 *
 * Wraps every /app/* route in the application shell (sidebar navigation,
 * responsive drawer, main content area). The landing page keeps the root
 * layout untouched.
 */
export default function AppLayout({ children }: LayoutProps<"/app">) {
  return <AppShell>{children}</AppShell>;
}
