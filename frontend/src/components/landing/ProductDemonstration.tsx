import { Container } from "@/components/ui/Container";
import { cn } from "@/lib/utils";
import { Reveal } from "./Reveal";
import { SectionHeading } from "./SectionHeading";

/**
 * Section: Product Demonstration — FRONTEND_SPEC.md §18.
 *
 * Dark section (DESIGN.md §20) with a split layout: a mock frame viewer
 * on the left, the resulting analysis on the right. Uses mock data, which
 * the spec allows for the initial demonstration. Phase 4: columns reveal
 * with a stagger on scroll.
 */

const userGoal = "Delete unnecessary files from File Explorer.";

const detectedActions = [
  "Open File Explorer",
  "Select sem4.zip",
  "Delete the file",
  "Select New Folder",
  "Delete the folder",
];

const frameCount = 12;
const keyFrames = [1, 4, 7, 10];

function FrameTimeline() {
  return (
    <div className="border-t border-cream/10 px-4 py-4 md:px-6">
      <div className="flex gap-1" aria-hidden>
        {Array.from({ length: frameCount }).map((_, index) => (
          <div
            key={index}
            className={cn(
              "h-7 flex-1 rounded-sm",
              keyFrames.includes(index) ? "bg-accent-soft/70" : "bg-cream/10",
            )}
          />
        ))}
      </div>
      <div className="mt-3 flex items-center justify-between">
        <span className="font-mono text-caption text-cream/40">00:00</span>
        <span className="font-mono text-caption uppercase tracking-[0.2em] text-cream/40">
          {frameCount} frames extracted
        </span>
        <span className="font-mono text-caption text-cream/40">00:12</span>
      </div>
    </div>
  );
}

export function ProductDemonstration() {
  return (
    <section id="demo" className="scroll-mt-20 bg-ink py-24 md:py-32">
      <Container className="flex flex-col gap-16">
        <Reveal>
          <SectionHeading
            eyebrow="Product demonstration"
            title="See what CopyCat sees."
            dark
          />
        </Reveal>
        <div className="grid items-start gap-12 lg:grid-cols-[1.15fr_1fr] lg:gap-16">
          {/* Mock video / frame area */}
          <Reveal delay={100}>
            <div className="overflow-hidden rounded-xl border border-cream/15 bg-[#141312]">
            <div className="flex items-center justify-between border-b border-cream/10 px-4 py-3 md:px-6">
              <span className="font-mono text-caption uppercase tracking-[0.2em] text-cream/50">
                screen-recording.mp4
              </span>
              <span className="font-mono text-caption text-cream/40">
                00:12
              </span>
            </div>
            <div className="flex aspect-video items-center justify-center">
              <div className="flex h-16 w-16 items-center justify-center rounded-full border border-cream/25 text-cream/70">
                <svg
                  viewBox="0 0 24 24"
                  fill="currentColor"
                  aria-hidden
                  className="h-6 w-6"
                >
                  <path d="M8 5v14l11-7z" />
                </svg>
              </div>
            </div>
            <FrameTimeline />
          </div>
          </Reveal>

          {/* Analysis area */}
          <Reveal delay={200}>
            <div className="flex flex-col gap-10">
            <div className="flex flex-col gap-3">
              <p className="font-mono text-small font-medium uppercase tracking-[0.3em] text-cream/50">
                User goal
              </p>
              <p className="font-heading text-h3 font-bold text-cream">
                {userGoal}
              </p>
            </div>
            <div>
              <p className="font-mono text-small font-medium uppercase tracking-[0.3em] text-cream/50">
                Actions detected
              </p>
              <ol className="mt-4">
                {detectedActions.map((action, index) => (
                  <li
                    key={action}
                    className="flex items-baseline gap-6 border-t border-cream/10 py-4"
                  >
                    <span className="font-mono text-small text-cream/40">
                      {String(index + 1).padStart(2, "0")}
                    </span>
                    <span className="text-base text-cream/90">{action}</span>
                  </li>
                ))}
              </ol>
            </div>
          </div>
          </Reveal>
        </div>
      </Container>
    </section>
  );
}
