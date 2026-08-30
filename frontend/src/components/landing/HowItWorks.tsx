import { Container } from "@/components/ui/Container";
import { Reveal } from "./Reveal";
import { SectionHeading } from "./SectionHeading";

/**
 * Section: How It Works — FRONTEND_SPEC.md §17.
 *
 * Four stages rendered as editorial rows with large stage numbers and
 * hairline dividers — deliberately not four generic feature cards.
 * Phase 4: heading + stage list reveal on scroll.
 */

const stages = [
  {
    number: "01",
    title: "Upload",
    description: "Upload a screen recording.",
  },
  {
    number: "02",
    title: "Observe",
    description:
      "CopyCat extracts important moments and interactions.",
  },
  {
    number: "03",
    title: "Understand",
    description: "AI identifies user actions and intent.",
  },
  {
    number: "04",
    title: "Structure",
    description: "The workflow becomes clear and understandable.",
  },
];

export function HowItWorks() {
  return (
    <section
      id="how-it-works"
      className="scroll-mt-20 bg-beige py-24 md:py-32"
    >
      <Container className="flex flex-col gap-16">
        <Reveal>
          <SectionHeading
            eyebrow="How it works"
            title={
              <>
                From recording
                <br />
                to understanding.
              </>
            }
          />
        </Reveal>
        <Reveal delay={100}>
          <ol className="border-b border-line">
            {stages.map((stage) => (
              <li
                key={stage.number}
                className="grid grid-cols-[4rem_1fr] items-baseline gap-6 border-t border-line py-10 md:grid-cols-[8rem_1fr] md:gap-12 md:py-12"
              >
                <span
                  aria-hidden
                  className="font-mono text-4xl font-medium text-accent md:text-5xl"
                >
                  {stage.number}
                </span>
                <div className="flex flex-col gap-2">
                  <h3 className="font-heading text-h3 font-bold text-ink">
                    {stage.title}
                  </h3>
                  <p className="max-w-xl text-base text-ink-secondary">
                    {stage.description}
                  </p>
                </div>
              </li>
            ))}
          </ol>
        </Reveal>
      </Container>
    </section>
  );
}
