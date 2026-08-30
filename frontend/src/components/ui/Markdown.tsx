import { Fragment, type ReactNode } from "react";

/**
 * Minimal Markdown renderer — dependency-free, matching the project's no-library
 * design system.
 *
 * The LLM's final summaries come back with `**bold**`, `*italic*`, `` `code` ``,
 * `- bullets`, `1. numbered`, `## headings`, `[links](url)` and blank-line
 * paragraphs. This renders that; anything it doesn't recognise falls through as
 * plain text. It is deliberately not a full CommonMark implementation.
 */

type MarkdownProps = {
  children: string;
  className?: string;
};

const INLINE = /(\*\*[^*]+\*\*|__[^_]+__|\*[^*]+\*|_[^_]+_|`[^`]+`|\[[^\]]+\]\([^)]+\))/g;

function renderInline(text: string, keyPrefix: string): ReactNode[] {
  const nodes: ReactNode[] = [];
  const parts = text.split(INLINE);

  parts.forEach((part, index) => {
    if (!part) return;
    const key = `${keyPrefix}-${index}`;

    if (
      (part.startsWith("**") && part.endsWith("**")) ||
      (part.startsWith("__") && part.endsWith("__"))
    ) {
      nodes.push(
        <strong key={key} className="font-semibold text-ink">
          {part.slice(2, -2)}
        </strong>,
      );
    } else if (part.startsWith("`") && part.endsWith("`")) {
      nodes.push(
        <code
          key={key}
          className="rounded bg-beige px-1.5 py-0.5 font-mono text-[0.85em] text-ink"
        >
          {part.slice(1, -1)}
        </code>,
      );
    } else if (
      (part.startsWith("*") && part.endsWith("*")) ||
      (part.startsWith("_") && part.endsWith("_"))
    ) {
      nodes.push(
        <em key={key} className="italic">
          {part.slice(1, -1)}
        </em>,
      );
    } else if (part.startsWith("[")) {
      const match = /^\[([^\]]+)\]\(([^)]+)\)$/.exec(part);
      if (match) {
        nodes.push(
          <a
            key={key}
            href={match[2]}
            target="_blank"
            rel="noopener noreferrer"
            className="text-accent underline underline-offset-2"
          >
            {match[1]}
          </a>,
        );
      } else {
        nodes.push(<Fragment key={key}>{part}</Fragment>);
      }
    } else {
      nodes.push(<Fragment key={key}>{part}</Fragment>);
    }
  });

  return nodes;
}

type Block =
  | { type: "heading"; level: number; text: string }
  | { type: "ul"; items: string[] }
  | { type: "ol"; items: string[] }
  | { type: "p"; text: string };

function parseBlocks(source: string): Block[] {
  const lines = source.replace(/\r\n/g, "\n").split("\n");
  const blocks: Block[] = [];
  let paragraph: string[] = [];

  const flushParagraph = () => {
    if (paragraph.length) {
      blocks.push({ type: "p", text: paragraph.join(" ") });
      paragraph = [];
    }
  };

  for (const raw of lines) {
    const line = raw.trimEnd();

    if (!line.trim()) {
      flushParagraph();
      continue;
    }

    const heading = /^(#{1,4})\s+(.*)$/.exec(line);
    if (heading) {
      flushParagraph();
      blocks.push({
        type: "heading",
        level: heading[1].length,
        text: heading[2],
      });
      continue;
    }

    const bullet = /^\s*[-*]\s+(.*)$/.exec(line);
    if (bullet) {
      flushParagraph();
      const last = blocks[blocks.length - 1];
      if (last && last.type === "ul") last.items.push(bullet[1]);
      else blocks.push({ type: "ul", items: [bullet[1]] });
      continue;
    }

    const ordered = /^\s*\d+[.)]\s+(.*)$/.exec(line);
    if (ordered) {
      flushParagraph();
      const last = blocks[blocks.length - 1];
      if (last && last.type === "ol") last.items.push(ordered[1]);
      else blocks.push({ type: "ol", items: [ordered[1]] });
      continue;
    }

    paragraph.push(line.trim());
  }

  flushParagraph();
  return blocks;
}

export function Markdown({ children, className }: MarkdownProps) {
  const blocks = parseBlocks(children ?? "");

  return (
    <div className={className}>
      {blocks.map((block, index) => {
        if (block.type === "heading") {
          return (
            <p
              key={index}
              className="mt-3 font-heading text-base font-bold text-ink first:mt-0"
            >
              {renderInline(block.text, `h-${index}`)}
            </p>
          );
        }

        if (block.type === "ul") {
          return (
            <ul
              key={index}
              className="my-2 flex list-disc flex-col gap-1 pl-5 first:mt-0 last:mb-0"
            >
              {block.items.map((item, i) => (
                <li key={i}>{renderInline(item, `ul-${index}-${i}`)}</li>
              ))}
            </ul>
          );
        }

        if (block.type === "ol") {
          return (
            <ol
              key={index}
              className="my-2 flex list-decimal flex-col gap-1 pl-5 first:mt-0 last:mb-0"
            >
              {block.items.map((item, i) => (
                <li key={i}>{renderInline(item, `ol-${index}-${i}`)}</li>
              ))}
            </ol>
          );
        }

        return (
          <p key={index} className="my-2 first:mt-0 last:mb-0">
            {renderInline(block.text, `p-${index}`)}
          </p>
        );
      })}
    </div>
  );
}
