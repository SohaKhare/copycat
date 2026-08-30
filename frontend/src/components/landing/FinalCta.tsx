import { Button } from "@/components/ui/Button";
import { Container } from "@/components/ui/Container";
import { Reveal } from "./Reveal";

/**
 * Final CTA — FRONTEND_SPEC.md §21.
 *
 * Accent section closing the landing page background rhythm
 * (DESIGN.md §18: cream → beige → dark → cream → accent).
 * Phase 4: content reveals on scroll.
 */
export function FinalCta() {
  return (
    <section id="get-started" className="scroll-mt-20 bg-accent">
      <Container className="py-28 text-center md:py-36">
        <Reveal className="flex flex-col items-center gap-8">
          <h2 className="font-heading text-h2 font-extrabold text-cream md:text-display">
            <span className="block">Ready to</span>
            <span className="block">understand</span>
            <span className="block">your workflow?</span>
          </h2>
          <p className="text-body-lg text-cream/80">
            Upload a recording. Let CopyCat do the watching.
          </p>
          {/* Application routes exist since Phase 5 — lead to the dashboard. */}
          <Button size="lg" variant="inverse" href="/app">
            Try CopyCat →
          </Button>
          <p className="text-small text-cream/70">
            Sign in to view your previous analyses.
          </p>
        </Reveal>
      </Container>
    </section>
  );
}
