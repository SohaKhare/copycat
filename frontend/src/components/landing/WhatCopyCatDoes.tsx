import { Container } from "@/components/ui/Container";
import { Reveal } from "./Reveal";
import { SectionHeading } from "./SectionHeading";

/**
 * Section: What CopyCat Does — FRONTEND_SPEC.md §16.
 *
 * Minimal editorial layout: large typography and whitespace only,
 * deliberately not a collection of feature cards. Phase 4: staggered
 * scroll reveals.
 */
export function WhatCopyCatDoes() {
  return (
    <section id="product" className="scroll-mt-20 bg-cream py-24 md:py-32">
      <Container className="flex flex-col gap-10">
        <Reveal>
          <SectionHeading
            eyebrow="What CopyCat does"
            title={
              <>
                Your users already
                <br />
                show you how they work.
              </>
            }
          />
        </Reveal>
        <Reveal delay={100}>
          <p className="font-heading text-h3 font-semibold text-ink">
            CopyCat helps you understand it.
          </p>
        </Reveal>
        <Reveal delay={200}>
          <p className="max-w-2xl text-body-lg text-ink-secondary">
            CopyCat analyzes screen recordings and identifies the actions
            taken, the intent behind them, and the workflow they produce —
            turning unstructured recordings into clear, structured
            information.
          </p>
        </Reveal>
      </Container>
    </section>
  );
}
