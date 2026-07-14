import type { SyntheticEvent } from "react";
import { Link } from "react-router-dom";
import { MarketingNav } from "./MarketingNav";
import { Button } from "@/components/ui/Button";
import { useAuth } from "@/features/auth/AuthContext";

const STEPS = [
  {
    title: "Versioned model",
    body: "Every prediction is traced to a specific model artifact and feature contract.",
  },
  {
    title: "Explainable risk predictions",
    body: "Each score comes with the SHAP features that drove it no bluff.",
  },
  {
    title: "Fleet Analytics",
    body: "Risk assessments are stored per driver, so history is auditable.",
  },
];

const FOOTER_COLUMNS = [
  { title: "Product", links: ["Features", "Use cases", "Disclaimer"] },
  { title: "Research", links: ["Abstract", "Datasets"] },
];

function hideOnError(e: SyntheticEvent<HTMLImageElement>) {
  e.currentTarget.style.display = "none";
}

export function LandingPage() {
  const { isAuthenticated } = useAuth();
  const ctaHref = isAuthenticated ? "/app" : "/login";
  const ctaLabel = isAuthenticated ? "Open dashboard" : "Get started";

  return (
    <div className="min-h-screen bg-white">
      <MarketingNav />

      <main>
        {/* Decorative badge: a sticky `top` (not `bottom`) offset is what
                pins it while scrolling down — `bottom` only clamps against
                upward scrolling. Sharing this container with the rest of the
                hero gives it the section's full height as its stick range;
                the container's bottom padding above is what gives the stuck
                position room to hold before the section boundary releases it. */}
        <div className="sticky top-[calc(100vh-8rem)] z-50 -mt-7 sm:ml-10 flex h-14 w-14 left-4 items-center justify-center rounded-full bg-[#0F6CBD] shadow-lg shadow-slate-900/20 sm:h-16 sm:w-16 opacity-60 hover:opacity-100">
          <img
            src="/images/MBERE ML logo.png"
            alt=""
            aria-hidden="true"
            className="h-12 w-12 sm:h-14 sm:w-14 object-contain"
          />
        </div>

        {/* Hero */}
        <section id="product" className="relative">
          <div className="container-page pb-0 pt-14 sm:pb-0 sm:pt-20">
            <div className="text-center">
              <h1 className="mx-auto max-w-2xl text-4xl font-bold leading-[1.1] tracking-tight text-slate-900 sm:text-5xl">
                Your driver's accident risk profile{" "}
                <span className="text-[#0F6CBD]">Mbere</span> it happens.
              </h1>
              <p className="mx-auto mt-6 max-w-xl text-base text-slate-500 sm:text-lg">
                Score risk, severity from a versioned ml model with transparent
                SHAP feature explanations.
              </p>
              <div className="mt-8 flex justify-center">
                <Link to={ctaHref}>
                  <Button variant="primaryMarketing" size="md">
                    {ctaLabel}
                  </Button>
                </Link>
              </div>

              <div className="mt-14 sm:mt-16">
                <img
                  src="/images/product-preview-laptop.png"
                  alt="MBERE ML dashboard preview"
                  className="mx-auto w-full max-w-18 scro"
                  onError={hideOnError}
                />
              </div>
            </div>
          </div>
        </section>

        {/* Road risk intelligence banner */}
        <section className="relative z-40 mx-4 rounded-[2.5rem] bg-[#0F6CBD] py-16 sm:mx-8 sm:py-20">
          <div className="container-page grid items-center gap-10 lg:grid-cols-2 lg:gap-16">
            <div>
              <h2 className="text-3xl font-bold text-white sm:text-4xl">
                Road risk intelligence
              </h2>
              <p className="mt-4 max-w-md text-blue-100 tracking-tight">
                Seamless inference on your driver's profiles high accuracy,
                transparent and explain-ability.
              </p>
              <div className="flex md:flex-col mt-8 justify-center">
                <Link to={ctaHref}>
                  <Button variant="inverse" size="md">
                    {ctaLabel}
                  </Button>
                </Link>
              </div>
            </div>
            <div className="flex justify-center lg:justify-end">
              <img
                src="/images/product-preview-tablet.png"
                alt="MBERE ML on tablet"
                className="w-full max-w-xs object-contain"
                onError={hideOnError}
              />
            </div>
          </div>
        </section>

        {/* How it works */}
        {/* Added: relative z-0 to establish base layer */}
        {/* Added: -mt-16 to pull this section up underneath the blue card */}
        {/* Added: pt-32 to push the "How it works" text down so it doesn't get covered by the blue card overlap */}
        <section
          id="how-it-works"
          className="relative z-30 bg-black -mt-16 pt-32 pb-32 sm:pb-48 rounded-b-[2rem] shadow-md"
        >
          <div className="container-page">
            <h2 className="text-center text-3xl text-white sm:text-4xl">
              <span className="font-bold">How</span>{" "}
              <span className="font-light">it works</span>
            </h2>

            {/* Changed: Added md:min-h-[600px] or extra bottom padding to accommodate the staggered cards */}
            <div className="relative mt-24 grid gap-x-64 gap-y-16 sm:grid-cols-3 items-start md:min-h-[700px]">
              {/* Positioned Arrows relative to the staggered layout */}
              <img
                src="/images/swigly-arrow.svg"
                alt=""
                aria-hidden="true"
                className="pointer-events-none absolute left-[22%] top-[-0.5rem] hidden h-36 w-auto opacity-90 sm:block"
              />
              <img
                src="/images/swigly-arrow.svg"
                alt=""
                aria-hidden="true"
                className="pointer-events-none absolute left-[62%] top-[12rem] hidden h-36 w-auto opacity-90 sm:block"
              />

              {STEPS.map((step, index) => {
                // Dynamically apply the downward shift depending on the step index
                const staggerClass =
                  index === 1
                    ? "sm:translate-y-48"
                    : index === 2
                      ? "sm:translate-y-96"
                      : "";

                return (
                  <div
                    key={step.title}
                    className={`flex flex-col items-center sm:items-start text-center sm:text-left ${staggerClass}`}
                  >
                    <p className="text-base font-semibold text-white">
                      {step.title}
                    </p>

                    {/* Updated: Styled white card with rounded corners matching your image */}
                    <div className="mt-4 aspect-[3/4] w-full max-w-[240px] bg-white/25 rounded-3xl shadow-xl">
                      <img src="/images/product-preview-tablet.png" />
                    </div>

                    <p className="mt-5 max-w-[240px] text-sm leading-relaxed text-slate-400">
                      {step.body}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        {/* Why Mbere ML */}
        <section className="relative -z-0 bg-white -mt-16 pt-32 pb-32 sm:pb-24 rounded-b-[2rem] shadow-md">
          <div className="container-page">
            <h2 className="text-center text-3xl text-slate-900 sm:text-4xl">
              <span className="font-light">Why</span>{" "}
              <span className="font-bold text-[#0F6CBD]">Mbere ML?</span>
            </h2>

            <div className="relative mx-auto mt-16 h-64 w-full max-w-xl sm:h-80 lg:h-96">
              <div className="absolute bottom-0 right-[6%] h-[45%] w-[28%] bg-sky-300" />
              <div className="absolute left-0 top-0 h-[85%] w-[34%] bg-[#0F6CBD] p-4 sm:p-6">
                <span className="text-3xl font-extralight text-sky-300 sm:text-2xl lg:text-6xl">
                  Made
                </span>
              </div>
              <div className="absolute left-[26%] top-[30%] flex h-[62%] w-[50%] items-center bg-sky-100 p-4 sm:p-6">
                <span className="text-5xl font-mono text-slate-800 sm:text-2xl lg:text-7xl">
                  For the way
                </span>
              </div>
              <div className="absolute left-[54%] top-[12%] flex h-[62%] w-[50%] items-center justify-end bg-[#0F6CBD] p-4 text-right sm:p-6">
                <span className="text-4xl font-semibold text-white sm:text-2xl lg:text-6xl">
                  You work
                </span>
              </div>
            </div>
          </div>
        </section>
      </main>

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
              Contacts
            </h3>
            <div className="mt-4 flex items-center gap-4">
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
            <div className="flex flex-col gap-2 text-sm text-slate-500 hover:text-slate-900 pt-3">
              <h6>+250 796 595 584</h6>
              <h6>Kigali, Rwanda</h6>
            </div>
          </div>
        </div>

        <div className="border-t border-slate-100">
          <div className="container-page pb-2">
            {/* Bottom footer logo */}
            {/* <div className="flex items-center gap-3">
              <img
                src="/images/MBERE ML logo.png"
                alt="Mbere ML logo"
                className="h-14 w-14 object-contain"
                onError={hideOnError}
              />
              <span className="text-3xl font-bold tracking-tight text-[#0F6CBD] sm:text-4xl">
                MBERE ML
              </span>
            </div> */}
            <div className="mt-6 flex flex-wrap items-center justify-between gap-4 text-xs text-slate-400">
              <span>© Mbere Machine Learning {new Date().getFullYear()}</span>
              <div className="flex gap-6">
                <a href="#" className="hover:text-slate-600">
                  Privacy
                </a>
                <a href="#" className="hover:text-slate-600">
                  Data Controls
                </a>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
