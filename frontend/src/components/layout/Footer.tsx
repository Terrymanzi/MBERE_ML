import type { SyntheticEvent } from "react";
import { Link } from "react-router-dom";
import { LegalNav } from "@/features/legal/components/LegalNav";

const FOOTER_COLUMNS = [
  { title: "Product", links: ["Features", "Use cases"] },
  { title: "Research", links: ["Abstract", "Datasets"] },
];

function hideOnError(e: SyntheticEvent<HTMLImageElement>) {
  e.currentTarget.style.display = "none";
}

export interface FooterProps {
  /** `full` — the marketing footer (link columns, contacts). `minimal` — a slim legal-links bar for auth/app shells. */
  variant?: "full" | "minimal";
}

export function Footer({ variant = "full" }: FooterProps) {
  if (variant === "minimal") {
    return (
      <footer className="border-t border-slate-200 bg-white">
        <div className="container-page flex flex-col items-center justify-between gap-4 py-6 text-xs text-slate-400 sm:flex-row">
          <span>© Mbere Machine Learning {new Date().getFullYear()}</span>
          <LegalNav />
        </div>
      </footer>
    );
  }

  return (
    <footer id="contact" className="z-0 -mt-6 bg-[#FFFFEB]">
      <div className="container-page grid gap-12 py-16 sm:grid-cols-3">
        {FOOTER_COLUMNS.map((column) => (
          <div key={column.title}>
            <h3 className="text-sm font-bold uppercase tracking-wide text-slate-900">
              {column.title}
            </h3>
            <ul className="mt-4 space-y-3 text-sm text-slate-500">
              {column.links.map((link) => (
                <li key={link}>
                  <a href="#" className="hover:text-slate-900">
                    {link}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        ))}
        <div>
          <h3 className="text-sm font-bold uppercase tracking-wide text-slate-900">
            Legal terms
          </h3>
          <div className="mt-4">
            <LegalNav variant="stacked" className="text-slate-500" />
          </div>
        </div>
      </div>

      <div className="border-t border-slate-100">
        <div className="container-page pb-2">
          <div className="flex flex-col gap-4 py-4 sm:flex-row sm:items-center sm:justify-start">
            <h3 className="text-sm font-bold tracking-wide text-slate-900">
              Get in Touch:
            </h3>
            <div className="flex items-center gap-4">
              <a
                href="https://github.com/Terrymanzi/MBERE_ML"
                aria-label="GitHub"
                target="_blank"
                rel="noreferrer"
              >
                <img
                  src="/images/GitHub-icon.png"
                  alt=""
                  className="h-6 w-6"
                  onError={hideOnError}
                />
              </a>
              <a
                href="https://www.linkedin.com/in/manzi-terry"
                aria-label="LinkedIn"
              >
                <img
                  src="/images/LinkedIn-icon.png"
                  alt=""
                  className="h-6 w-6"
                  onError={hideOnError}
                />
              </a>
              <a href="mailto:terrymanzi@outlook.com" aria-label="Email">
                <img
                  src="/images/Email-icon.png"
                  alt="mailto:terrymanzi@outlook.com"
                  className="h-6 w-6"
                  onError={hideOnError}
                />
              </a>
            </div>
          </div>
          {/* <div className="flex flex-col gap-2 text-sm text-slate-500 pt-1">
            <h6>+250 796 595 584</h6>
            <h6>Kigali, Rwanda</h6>
          </div> */}

          <div className="mt-6 flex flex-wrap items-center justify-between gap-4 text-xs text-slate-400">
            <span>© {new Date().getFullYear()} Mbere Machine Learning</span>
            <Link
              to="https://nrx1yhr8.status.cron-job.org/"
              className="hover:text-slate-600"
            >
              System Status
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
