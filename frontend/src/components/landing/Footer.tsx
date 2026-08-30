import { Container } from "@/components/ui/Container";

/**
 * Footer — FRONTEND_SPEC.md §22.
 *
 * Minimal dark footer closing the page.
 */

const footerLinks = [
  { label: "Product", href: "#product" },
  { label: "How It Works", href: "#how-it-works" },
  { label: "Use Cases", href: "#use-cases" },
  {
    label: "GitHub",
    href: "https://github.com/SohaKhare/copycat-private",
    external: true,
  },
];

export function Footer() {
  return (
    <footer className="bg-ink text-cream">
      <Container className="flex flex-col gap-10 py-16">
        <div className="flex flex-col justify-between gap-8 md:flex-row md:items-start">
          <div className="flex flex-col gap-2">
            <p className="font-heading text-lg font-bold">CopyCat</p>
            <p className="text-small text-cream/60">
              AI-powered workflow understanding.
            </p>
          </div>
          <nav
            aria-label="Footer"
            className="flex flex-wrap gap-x-8 gap-y-3 text-small text-cream/70"
          >
            {footerLinks.map((link) => (
              <a
                key={link.label}
                href={link.href}
                {...(link.external
                  ? { target: "_blank", rel: "noopener noreferrer" }
                  : {})}
                className="transition-colors duration-200 hover:text-cream"
              >
                {link.label}
              </a>
            ))}
          </nav>
        </div>
        <div className="border-t border-cream/10 pt-6">
          <p className="text-caption text-cream/40">
            © {new Date().getFullYear()} CopyCat. All rights reserved.
          </p>
        </div>
      </Container>
    </footer>
  );
}
