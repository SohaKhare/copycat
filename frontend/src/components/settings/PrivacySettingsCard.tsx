"use client";

import { useEffect, useState } from "react";
import { Card } from "@/components/ui/Card";
import {
  getHidePersonalDetails,
  PRIVACY_SETTING_DESCRIPTION,
  PRIVACY_SETTING_LABEL,
  setHidePersonalDetails,
} from "@/lib/privacy-settings";
import { cn } from "@/lib/utils";

function PrivacyToggle({
  enabled,
  onChange,
}: {
  enabled: boolean;
  onChange: (next: boolean) => void;
}) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={enabled}
      aria-label={PRIVACY_SETTING_LABEL}
      onClick={() => onChange(!enabled)}
      className={cn(
        "relative inline-flex h-7 w-12 shrink-0 rounded-full border transition-colors duration-200",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-soft",
        enabled
          ? "border-accent bg-accent"
          : "border-line bg-surface",
      )}
    >
      <span
        className={cn(
          "pointer-events-none absolute top-0.5 h-5 w-5 rounded-full bg-surface shadow-soft transition-transform duration-200",
          enabled ? "translate-x-5" : "translate-x-1",
        )}
      />
    </button>
  );
}

export function PrivacySettingsCard() {
  const [enabled, setEnabled] = useState(true);
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    setEnabled(getHidePersonalDetails());
    setHydrated(true);
  }, []);

  function handleChange(next: boolean) {
    setEnabled(next);
    setHidePersonalDetails(next);
  }

  return (
    <Card className="p-6">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0 flex-1">
          <h2 className="font-heading text-h3 font-bold text-ink">
            Recording privacy
          </h2>
          <p className="mt-2 max-w-2xl text-small text-ink-secondary">
            {PRIVACY_SETTING_DESCRIPTION}
          </p>
          <p className="mt-3 text-caption text-ink-muted">
            Original frames stay on your machine. Only redacted copies are sent
            for AI analysis.
          </p>
        </div>
        {hydrated ? (
          <PrivacyToggle enabled={enabled} onChange={handleChange} />
        ) : (
          <span
            className="inline-flex h-7 w-12 shrink-0 rounded-full border border-line bg-surface"
            aria-hidden
          />
        )}
      </div>
      <p className="mt-4 text-caption text-ink-secondary">
        <span className="font-medium text-ink">{PRIVACY_SETTING_LABEL}</span>
        {" — "}
        {hydrated
          ? enabled
            ? "On by default. Sensitive details are hidden before analysis."
            : "Off. Recordings are sent to AI without local redaction."
          : "Loading preference…"}
      </p>
    </Card>
  );
}
