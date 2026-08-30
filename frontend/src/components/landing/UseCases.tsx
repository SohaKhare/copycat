import { Container } from "@/components/ui/Container";
import { Reveal } from "./Reveal";
import { SectionHeading } from "./SectionHeading";

/**
 * Section: Use Cases — FRONTEND_SPEC.md §20.
 *
 * Editorial 2×2 grid separated by hairline dividers — no card
 * backgrounds, per the design system's "do not overuse cards" rule.
 * Phase 4: staggered reveals per cell + subtle background hover.
 */

const useCases = [
  {
    number: "01",
    title: "User Research",
    description: "Understand how people actually interact with software.",
  },
  {
    number: "02",
    title: "Workflow Documentation",
    description: "Turn recorded workflows into structured processes.",
  },
  {
    number: "03",
    title: "UX Analysis",
    description: "Discover how users navigate through digital products.",
  },
  {
    number: "04",
    title: "AI Training",
    description: "Transform human interactions into structured information.",
  },
];

export function UseCases() {
  return (
    <section id="use-cases" className="scroll-mt-20 bg-cream py-24 md:py-32">
      <Container className="flex flex-col gap-16">
        <Reveal>
          <SectionHeading eyebrow="Use cases" title="Put CopyCat to work." />
        </Reveal>
        <div className="grid grid-cols-1 border-l border-t border-line sm:grid-cols-2">
          {useCases.map((useCase, index) => (
            <div
              key={useCase.number}
              className="flex flex-col gap-3 border-b border-r border-line p-8 transition-colors duration-300 hover:bg-beige/50 md:p-12"
            >
              <Reveal delay={(index % 2) * 100}>
                <span
                  aria-hidden
                  className="font-mono text-small font-medium text-accent"
                >
                  {useCase.number}
                </span>
                <h3 className="mt-3 font-heading text-h3 font-bold text-ink">
                  {useCase.title}
                </h3>
                <p className="mt-2 max-w-sm text-base text-ink-secondary">
                  {useCase.description}
                </p>
              </Reveal>
            </div>
          ))}
        </div>
      </Container>
    </section>
  );
}
