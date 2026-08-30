import type { Metadata } from "next";
import { PageHeader } from "@/components/app/PageHeader";
import { Card } from "@/components/ui/Card";
import { IconSliders } from "@/components/ui/Icons";

export const metadata: Metadata = {
  title: "Settings",
};

/**
 * Settings — FRONTEND_SPEC.md Phase 5 (navigation destination only).
 *
 * Per FRONTEND_SPEC.md §47, user settings are a future feature and are
 * not implemented automatically; this page exists so the navigation item
 * has an honest destination.
 */
export default function SettingsPage() {
  return (
    <>
      <PageHeader title="Settings" />
      <Card className="flex flex-col items-center gap-4 p-10 text-center">
        <span className="flex h-12 w-12 items-center justify-center rounded-full bg-accent-soft text-accent">
          <IconSliders className="h-6 w-6" />
        </span>
        <h2 className="font-heading text-h3 font-bold text-ink">
          Settings are on the way
        </h2>
        <p className="max-w-md text-small text-ink-secondary">
          Account preferences and sign-out will arrive in a later phase.
        </p>
      </Card>
    </>
  );
}
