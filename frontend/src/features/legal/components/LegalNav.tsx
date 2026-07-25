import { LegalLink } from "./LegalLink";
import { cn } from "@/lib/cn";

const DOCS = [
  { to: "/legal/terms", label: "Terms of Use" },
  { to: "/legal/privacy", label: "Privacy Policy" },
  { to: "/legal/disclaimer", label: "Disclaimer" },
];

export interface LegalNavProps {
  variant?: "inline" | "stacked";
  newTab?: boolean;
  className?: string;
}

/** Reusable cross-links to all three legal documents — footer, settings, login screen. */
export function LegalNav({ variant = "inline", newTab, className }: LegalNavProps) {
  return (
    <nav
      aria-label="Legal"
      className={cn(
        variant === "inline"
          ? "flex flex-wrap items-center gap-x-6 gap-y-2 text-sm"
          : "flex flex-col gap-3 text-sm",
        className,
      )}
    >
      {DOCS.map((doc) => (
        <LegalLink key={doc.to} to={doc.to} newTab={newTab}>
          {doc.label}
        </LegalLink>
      ))}
    </nav>
  );
}
