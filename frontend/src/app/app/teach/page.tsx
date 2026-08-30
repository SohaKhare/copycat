import type { Metadata } from "next";
import { PageHeader } from "@/components/app/PageHeader";
import { TeachUpload } from "@/components/teach/TeachUpload";
import { Card } from "@/components/ui/Card";
import { IconSparkles } from "@/components/ui/Icons";

export const metadata: Metadata = {
  title: "Teach CopyCat",
};

/**
 * Teach CopyCat — FRONTEND_SPEC.md Phase 6.
 *
 * Title and supporting text are taken verbatim from the spec. The guidance
 * column stays subtle and concise, and the example workflows frame CopyCat
 * as learning complex, multi-step processes — never simple one-action tasks.
 */

const GUIDANCE_STEPS = [
  "Start with the task already prepared.",
  "Show it in a recording, or describe the steps out loud.",
  "Include important decisions and steps.",
  "Avoid unnecessary unrelated actions.",
];

const WORKFLOW_EXAMPLES = [
  "Organize a semester workspace",
  "Prepare a project folder",
  "Process downloaded documents",
  "Complete a browser workflow",
  "Handle a repeated email workflow",
];

export default function TeachPage() {
  return (
    <>
      <PageHeader
        title="Teach CopyCat"
        description="Show CopyCat a workflow with a screen recording, or describe it by voice or text."
      />

      <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_320px]">
        <TeachUpload />

        <aside className="flex flex-col gap-8">
          <section aria-labelledby="teach-guidance-heading">
            <Card className="flex flex-col gap-4 p-6">
              <h2
                id="teach-guidance-heading"
                className="text-caption font-medium uppercase tracking-[0.18em] text-ink-muted"
              >
                For best results
              </h2>
              <ol className="flex list-decimal flex-col gap-2 pl-4 text-small text-ink-secondary">
                {GUIDANCE_STEPS.map((step) => (
                  <li key={step}>{step}</li>
                ))}
              </ol>
            </Card>
          </section>

          <section aria-labelledby="teach-examples-heading">
            <Card className="flex flex-col gap-4 p-6">
              <div className="flex items-center gap-2">
                <IconSparkles className="h-4 w-4 text-accent" />
                <h2
                  id="teach-examples-heading"
                  className="text-caption font-medium uppercase tracking-[0.18em] text-ink-muted"
                >
                  Workflows worth teaching
                </h2>
              </div>
              <ul className="flex flex-col gap-2">
                {WORKFLOW_EXAMPLES.map((example) => (
                  <li
                    key={example}
                    className="rounded-md border border-line bg-surface px-3 py-2 text-small text-ink-secondary"
                  >
                    {example}
                  </li>
                ))}
              </ul>
              <p className="text-caption text-ink-muted">
                CopyCat is built for multi-step, repeated processes — not
                single-click actions.
              </p>
            </Card>
          </section>
        </aside>
      </div>
    </>
  );
}
