import type { Metadata } from "next";
import { Geist_Mono, Inter, Manrope } from "next/font/google";
import "./globals.css";

/* Headings (DESIGN.md §8) */
const manrope = Manrope({
  variable: "--font-manrope",
  subsets: ["latin"],
});

/* Body and UI (DESIGN.md §8) */
const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

/* Monospace — code snippets, timestamps, stage numbers */
const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "CopyCat — Watch. Understand. Replicate.",
  description:
    "CopyCat analyzes screen recordings and transforms them into structured, understandable digital workflows.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      className={`${manrope.variable} ${inter.variable} ${geistMono.variable} h-full`}
    >
      <body className="flex min-h-full flex-col bg-cream font-sans text-ink antialiased">
        {children}
      </body>
    </html>
  );
}

