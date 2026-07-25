import ReactMarkdown from "react-markdown";
import type { Components } from "react-markdown";
import type { LegalHeading } from "../lib/extractHeadings";

const LINK_CLASSES =
  "font-mono text-[#0F6CBD] underline decoration-slate-300 underline-offset-2 hover:decoration-[#0F6CBD] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-600 rounded-sm";

/**
 * Renders legal markdown with the app's Tailwind conventions instead of a
 * generic "prose" plugin. `headings` must come from `extractHeadings` on the
 * same raw markdown, in document order, so `id`s assigned here line up
 * exactly with the table of contents' anchor links.
 */
export function LegalMarkdown({
  markdown,
  headings,
}: {
  markdown: string;
  headings: LegalHeading[];
}) {
  let headingIndex = 0;

  const components: Components = {
    h2: ({ children }) => {
      const heading = headings[headingIndex++];
      return (
        <h2
          id={heading?.id}
          className="mt-10 scroll-mt-24 text-xl font-semibold tracking-tight text-slate-900 first:mt-0"
        >
          {children}
        </h2>
      );
    },
    p: ({ children }) => (
      <p className="mt-4 font-thin leading-relaxed text-slate-600">
        {children}
      </p>
    ),
    ul: ({ children }) => (
      <ul className="mt-4 list-disc space-y-2 pl-6 font-thin leading-relaxed text-slate-600">
        {children}
      </ul>
    ),
    li: ({ children }) => <li>{children}</li>,
    strong: ({ children }) => (
      <strong className="font-semibold text-slate-900">{children}</strong>
    ),
    em: ({ children }) => <em className="italic">{children}</em>,
    blockquote: ({ children }) => (
      <blockquote className="mt-4 border-l-2 border-[#0F6CBD] pl-4 font-thin italic text-slate-500">
        {children}
      </blockquote>
    ),
    hr: () => <hr className="my-10 border-slate-200" />,
    a: ({ href, children }) => (
      <a href={href} className={LINK_CLASSES}>
        {children}
      </a>
    ),
  };

  return (
    <div className="font-thin">
      <ReactMarkdown components={components}>{markdown}</ReactMarkdown>
    </div>
  );
}
