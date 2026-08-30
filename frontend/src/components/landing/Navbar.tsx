"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/Button";
import { Container } from "@/components/ui/Container";
import { cn } from "@/lib/utils";

/**
 * Landing page navigation — FRONTEND_SPEC.md §13.
 *
 * Phase 4: blends into the cream page at the top; once the user scrolls
 * it picks up a translucent background, backdrop blur, and a hairline
 * bottom border. The border is always rendered (transparent → line) so
 * the transition never causes layout shift.
 *
 * Try It Out leads to the application dashboard (/app, built in Phase 5).
 * Sign In stays on the final CTA section until the authentication
 * routes exist (Phase 10).
 */
export function Navbar() {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header
      className={cn(
        "sticky top-0 z-50 border-b transition-colors duration-300",
        scrolled
          ? "border-line bg-cream/90 backdrop-blur-md"
          : "border-transparent bg-cream",
      )}
    >
      <Container className="flex items-center justify-between py-4">
        <Link
          href="/"
          className="font-heading text-xl font-bold tracking-tight text-ink"
        >
          CopyCat
        </Link>
        <nav className="flex items-center gap-3" aria-label="Main">
          <Button
            variant="secondary"
            size="sm"
            href="#get-started"
            className="hidden sm:inline-flex"
          >
            Sign In
          </Button>
          <Button size="sm" href="/app">
            Try It Out →
          </Button>
        </nav>
      </Container>
    </header>
  );
}

