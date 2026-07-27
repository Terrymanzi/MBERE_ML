import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import { cn } from "@/lib/cn";

export interface LegalLinkProps {
  to: string;
  children: ReactNode;
  /** Opens in a new tab, use when linking out of an in-progress flow (signup, login) so form state isn't lost. */
  newTab?: boolean;
  className?: string;
}

const LINK_CLASSES =
  "font-mono text-[#0F6CBD] underline decoration-slate-300 underline-offset-2 hover:decoration-[#0F6CBD] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-600 rounded-sm";

/** Semantic link primitive every other legal component composes, so new-tab/a11y behaviour stays consistent in one place. */
export function LegalLink({ to, children, newTab, className }: LegalLinkProps) {
  if (newTab) {
    return (
      <a
        href={to}
        target="_blank"
        rel="noopener noreferrer"
        className={cn(LINK_CLASSES, className)}
      >
        {children}
        <span className="sr-only"> (opens in new tab)</span>
      </a>
    );
  }

  return (
    <Link to={to} className={cn(LINK_CLASSES, className)}>
      {children}
    </Link>
  );
}
