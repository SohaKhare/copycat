import { Container } from "@/components/ui/Container";
import { Reveal } from "./Reveal";
import { SectionHeading } from "./SectionHeading";

/**
 * Section: Why CopyCat — FRONTEND_SPEC.md §19.
 *
 * Concise problem statement with strong editorial typography.
 * Phase 4: staggered scroll reveals.
 */
export function WhyCopyCat() {
  return (
    <section id="why" className="scroll-mt-20 bg-cream py-24 md:py-32">
      <Container className="flex flex-col gap-10">
        <Reveal>
          <SectionHeading
            eyebrow="Why CopyCat"
            title={
              <>
                Watching is easy.
                <br />
                Understanding is hard.
              </>
            }
          />
        </Reveal>
        <Reveal delay={100}>
          <p className="max-w-2xl text-body-lg text-ink-secondary">
            People generate long screen recordings. Reviewing them manually
            takes time, and the workflow hidden inside them is easy to miss.
            CopyCat transforms that visual activity into structured,
            understandable information.
          </p>
        </Reveal>
      </Container>
    </section>
  );
}
