import type { Metadata } from "next";
import Link from "next/link";
import { Suspense } from "react";
import { VoiceCommand } from "@/components/app/VoiceCommand";
import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import {
  IconActivity,
  IconArrowRight,
  IconSparkles,
  IconUpload,
} from "@/components/ui/Icons";

export const metadata: Metadata = {
  title: "Dashboard",
};

/**
 * Dashboard — Phase A.
 *
 * The voice-first command box runs accepted skills via POST /execute.
 * Activity and skills previews remain sample data until Phase B.
 */

const QUICK_ACTIONS = [
  {
    href: "/app/teach",
    label: "Teach CopyCat",
    description: "Show CopyCat a new workflow.",
    icon: IconUpload,
  },
  {
    href: "/app/skills",
    label: "View Skills",
    description: "See what CopyCat has learned.",
    icon: IconSparkles,
  },
  {
    href: "/app/activity",
    label: "Recent Activity",
    description: "Review what CopyCat has done.",
    icon: IconActivity,
  },
] as const;

const SAMPLE_ACTIVITY = [
  {
    type: "Learned",
    tone: "success" as const,
    text: "CopyCat learned \u201COrganize Semester Files\u201D",
    time: "2 hours ago",
  },
  {
    type: "Executed",
    tone: "info" as const,
    text: "CopyCat ran \u201CPrepare Project Workspace\u201D",
    time: "Yesterday",
  },
  {
    type: "Learned",
    tone: "success" as const,
    text: "CopyCat learned \u201CProcess Important Emails\u201D",
    time: "Monday",
  },
];

const SAMPLE_SKILLS = [
  { name: "Organize Semester Files", steps: 14 },
  { name: "Prepare Project Workspace", steps: 9 },
  { name: "Process Important Emails", steps: 12 },
];

export default function DashboardPage() {
  return (
    <div className="flex flex-col gap-14">
      {/* Voice-first hero — the primary product interaction */}
      <section className="flex flex-col items-center pt-2 text-center md:pt-6">
        <p className="text-caption font-medium uppercase tracking-[0.2em] text-ink-muted">
          Dashboard
        </p>
        <h1 className="mt-4 max-w-2xl font-heading text-h3 font-extrabold text-ink md:text-h2">
          What would you like CopyCat to do?
        </h1>
        <div className="mt-10 w-full max-w-xl">
          <Suspense
            fallback={
              <div className="rounded-md border border-line bg-surface p-8 text-center text-small text-ink-secondary">
                Loading command input…
              </div>
            }
          >
            <VoiceCommand />
          </Suspense>
        </div>
      </section>

      {/* Quick actions */}
      <section>
        <h2 className="text-caption font-medium uppercase tracking-[0.18em] text-ink-muted">
          Quick actions
        </h2>
        <div className="mt-4 grid gap-4 sm:grid-cols-3">
          {QUICK_ACTIONS.map((action) => {
            const Icon = action.icon;
            return (
              <Link key={action.href} href={action.href} className="group">
                <Card className="h-full p-5 transition-colors duration-200 group-hover:border-accent">
                  <div className="flex items-start justify-between">
                    <span className="flex h-10 w-10 items-center justify-center rounded-md bg-accent-soft text-accent">
                      <Icon />
                    </span>
                    <IconArrowRight className="h-4 w-4 text-ink-muted transition-all duration-200 group-hover:translate-x-0.5 group-hover:text-accent" />
                  </div>
                  <p className="mt-4 font-medium text-ink">{action.label}</p>
                  <p className="mt-1 text-small text-ink-secondary">
                    {action.description}
                  </p>
                </Card>
              </Link>
            );
          })}
        </div>
      </section>

      {/* Recent activity + skills overview */}
      <section className="grid gap-6 lg:grid-cols-2">
        <Card className="p-6">
          <div className="flex items-center justify-between gap-4">
            <h2 className="font-heading text-base font-bold text-ink">
              Recent activity
            </h2>
            <Link
              href="/app/activity"
              className="inline-flex items-center gap-1 text-small text-ink-secondary transition-colors duration-200 hover:text-accent"
            >
              View all
              <IconArrowRight className="h-3.5 w-3.5" />
            </Link>
          </div>
          <ul className="mt-4 divide-y divide-line">
            {SAMPLE_ACTIVITY.map((item) => (
              <li key={item.text} className="flex items-center gap-3 py-3">
                <Badge tone={item.tone}>{item.type}</Badge>
                <div className="min-w-0 flex-1">
                  <p className="truncate text-small text-ink">{item.text}</p>
                  <p className="text-caption text-ink-muted">{item.time}</p>
                </div>
              </li>
            ))}
          </ul>
          <p className="mt-4 text-caption text-ink-muted">
            Sample preview — live activity appears once CopyCat is connected.
          </p>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between gap-4">
            <h2 className="font-heading text-base font-bold text-ink">
              Skills overview
            </h2>
            <Link
              href="/app/skills"
              className="inline-flex items-center gap-1 text-small text-ink-secondary transition-colors duration-200 hover:text-accent"
            >
              View all
              <IconArrowRight className="h-3.5 w-3.5" />
            </Link>
          </div>
          <ul className="mt-4 divide-y divide-line">
            {SAMPLE_SKILLS.map((skill) => (
              <li
                key={skill.name}
                className="flex items-center justify-between gap-3 py-3"
              >
                <div className="min-w-0">
                  <p className="truncate text-small font-medium text-ink">
                    {skill.name}
                  </p>
                  <p className="text-caption text-ink-muted">
                    {skill.steps} steps
                  </p>
                </div>
                <Badge>Saved</Badge>
              </li>
            ))}
          </ul>
          <p className="mt-4 text-caption text-ink-muted">
            Sample preview — your learned workflows appear here.
          </p>
        </Card>
      </section>

    </div>
  );
}
