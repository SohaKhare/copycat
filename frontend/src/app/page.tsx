import { FinalCta } from "@/components/landing/FinalCta";
import { Footer } from "@/components/landing/Footer";
import { Hero } from "@/components/landing/Hero";
import { HowItWorks } from "@/components/landing/HowItWorks";
import { Navbar } from "@/components/landing/Navbar";
import { ProductDemonstration } from "@/components/landing/ProductDemonstration";
import { UseCases } from "@/components/landing/UseCases";
import { WhatCopyCatDoes } from "@/components/landing/WhatCopyCatDoes";
import { WhyCopyCat } from "@/components/landing/WhyCopyCat";

/**
 * Landing page — FRONTEND_SPEC.md §12–22.
 *
 * Static structure (Phase 3). Scroll behavior and reveal animations
 * are added in Phase 4.
 */
export default function Home() {
  return (
    <>
      <Navbar />
      <main>
        <Hero />
        <WhatCopyCatDoes />
        <HowItWorks />
        <ProductDemonstration />
        <WhyCopyCat />
        <UseCases />
        <FinalCta />
      </main>
      <Footer />
    </>
  );
}


