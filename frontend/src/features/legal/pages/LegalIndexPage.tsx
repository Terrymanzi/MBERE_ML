import { Link } from "react-router-dom";
import { Logo } from "@/components/layout/Logo";
import { Footer } from "@/components/layout/Footer";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { useDocumentMeta } from "@/lib/useDocumentMeta";
import { EFFECTIVE_DATE, LAST_UPDATED } from "../content/meta";

const DOCS = [
  {
    to: "/legal/terms",
    title: "Terms of Use",
    description:
      "The terms governing your use of the MBERE ML platform, its API, and its outputs.",
  },
  {
    to: "/legal/privacy",
    title: "Privacy Policy",
    description:
      "What data we collect, why, and the rights you have over it under Rwandan law.",
  },
  {
    to: "/legal/disclaimer",
    title: "Disclaimer",
    description:
      "Known limitations of the risk model and what its outputs do and don't mean.",
  },
];

export function LegalIndexPage() {
  useDocumentMeta(
    "Legal",
    "Terms of Use, Privacy Policy, and Disclaimer for the MBERE ML platform.",
  );

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
          Legal
        </h1>
        <p className="mt-3 max-w-2xl font-thin text-slate-500">
          Everything governing your use of MBERE ML, in one place.
        </p>
        <p className="mt-3 font-mono text-xs uppercase tracking-wide text-slate-400">
          Effective {EFFECTIVE_DATE} · Last updated {LAST_UPDATED}
        </p>

        <div className="mt-10 grid gap-6 sm:grid-cols-3">
          {DOCS.map((doc) => (
            <Link key={doc.to} to={doc.to} className="group block">
              <Card className="h-full transition-colors group-hover:border-[#0F6CBD]">
                <CardHeader title={doc.title} />
                <CardBody>
                  <p className="text-sm font-thin text-slate-500">
                    {doc.description}
                  </p>
                </CardBody>
              </Card>
            </Link>
          ))}
        </div>
      </main>

      <Footer variant="full" />
    </div>
  );
}
