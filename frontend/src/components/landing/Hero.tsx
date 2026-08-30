import { Button } from "@/components/ui/Button";
import { Container } from "@/components/ui/Container";

/**
 * Landing page hero — FRONTEND_SPEC.md §14–15.
 *
 * ~100vh, typography-first, generous whitespace. No video or heavy
 * background effects (a video layer may be added in a later phase).
 * Phase 4: short staggered fade/rise entrance on load; disabled under
 * prefers-reduced-motion via the global guard in globals.css.
 */
export function Hero() {
  return (
    <section className="flex min-h-[calc(100svh-4.5rem)] items-center">
      <Container className="flex flex-col items-start gap-8 py-24">
        <p className="animate-fade-rise font-mono text-2xl font-semibold uppercase tracking-[0.25em] text-accent">
          CopyCat
        </p>
        <h1 className="animate-fade-rise font-heading text-hero font-extrabold text-ink [animation-delay:120ms]">
          <span className="block">Watch.</span>
          <span className="block">Understand.</span>
          <span className="block">Replicate.</span>
        </h1>
        <p className="animate-fade-rise max-w-xl text-body-lg text-ink-secondary [animation-delay:240ms]">
          AI that transforms screen recordings into structured digital
          workflows.
        </p>
        <div className="animate-fade-rise flex flex-wrap items-center gap-6 [animation-delay:360ms]">
          <Button size="lg" href="#get-started">
            Try It Out →
          </Button>
          <a
            href="#product"
            className="text-small text-ink-secondary underline-offset-4 transition-colors duration-200 hover:text-ink hover:underline"
          >
            Learn more ↓
          </a>
        </div>
      </Container>
    </section>
  );
}
