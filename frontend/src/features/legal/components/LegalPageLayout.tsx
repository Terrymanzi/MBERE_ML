import { useMemo } from "react";
import { Link } from "react-router-dom";
import { Logo } from "@/components/layout/Logo";
import { Footer } from "@/components/layout/Footer";
import { useDocumentMeta } from "@/lib/useDocumentMeta";
import { extractHeadings } from "../lib/extractHeadings";
import { useActiveHeading } from "../lib/useActiveHeading";
import { TableOfContents } from "./TableOfContents";
import { LegalMarkdown } from "./LegalMarkdown";
import { LegalNav } from "./LegalNav";
import { EFFECTIVE_DATE, LAST_UPDATED } from "../content/meta";

export function LegalPageLayout({
  title,
  description,
  markdown,
}: {
  title: string;
  description: string;
  markdown: string;
}) {
  useDocumentMeta(title, description);

  const headings = useMemo(() => extractHeadings(markdown), [markdown]);
  const activeId = useActiveHeading(useMemo(() => headings.map((h) => h.id), [headings]));

  return (
    <div className="min-h-screen bg-white">
      <header className="border-b border-slate-200">
        <div className="container-page flex h-20 items-center justify-between">
          <Link to="/" aria-label="MBERE ML home">
            <Logo />
          </Link>
          <Link
            to="/"
            className="text-sm font-thin text-slate-500 hover:text-slate-900"
          >
            ← Back home
          </Link>
        </div>
      </header>

      <main className="container-page py-14">
        <h1 className="text-4xl font-thin tracking-tight text-slate-900">
          {title}
        </h1>
        <p className="mt-3 font-mono text-xs uppercase tracking-wide text-slate-400">
          Effective {EFFECTIVE_DATE} · Last updated {LAST_UPDATED}
        </p>

        <div className="mt-6 border-b border-slate-100 pb-6">
          <LegalNav />
        </div>

        <div className="mt-10 grid gap-12 lg:grid-cols-[220px_1fr]">
          <aside className="hidden lg:block">
            <div className="sticky top-8">
              <TableOfContents headings={headings} activeId={activeId} />
            </div>
          </aside>

          <article className="max-w-3xl">
            <LegalMarkdown markdown={markdown} headings={headings} />
          </article>
        </div>
      </main>

      <Footer variant="full" />
    </div>
  );
}
