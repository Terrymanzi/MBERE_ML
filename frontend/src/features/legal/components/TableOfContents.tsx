import type { LegalHeading } from "../lib/extractHeadings";
import { cn } from "@/lib/cn";

export function TableOfContents({
  headings,
  activeId,
}: {
  headings: LegalHeading[];
  activeId: string | null;
}) {
  if (headings.length === 0) return null;

  return (
    <nav aria-label="Table of contents" className="text-sm">
      <p className="mb-3 text-xs font-thin uppercase tracking-wide text-slate-400">
        On this page
      </p>
      <ul className="space-y-1 border-l border-slate-200">
        {headings.map((heading) => {
          const isActive = heading.id === activeId;
          return (
            <li key={heading.id}>
              <a
                href={`#${heading.id}`}
                aria-current={isActive ? "location" : undefined}
                className={cn(
                  "-ml-px block border-l-2 py-1 pl-4 font-thin transition-colors",
                  "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-600",
                  isActive
                    ? "border-[#0F6CBD] text-slate-900"
                    : "border-transparent text-slate-500 hover:text-slate-900",
                )}
              >
                {heading.text}
              </a>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
