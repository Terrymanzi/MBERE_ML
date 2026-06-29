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
    title: "Fleet history",
    body: "Risk assessments are stored per driver, so history is auditable.",
  },
];

export function LandingPage() {
  const { isAuthenticated } = useAuth();

  return (
    <div className="min-h-screen bg-white">
      <MarketingNav />

      <main>
        <section className="container-page grid gap-12 py-20 lg:grid-cols-2 lg:items-center lg:py-28">
          <div>
            <p className="text-xl text-opacity-50 font-light tracking-widest uppercase text-black">
              Road risk intelligence
            </p>
            <h1 className="mt-4 text-5xl font-thin leading-[1.05] tracking-tight text-slate-900 sm:text-6xl">
              Predict road-accident risks{" "}
              <span className="text-[#0F6CBD] font-light">mbere</span> it
              happens.
            </h1>
            <p className="mt-6 max-w-xl text-lg text-opacity-50 font-light text-black">
              MBERE ML scores driver risk from a versioned machine-learning
              model and explains every prediction with its top contributing
              features.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link to={isAuthenticated ? "/app" : "/login"}>
                <Button size="lg">
                  {isAuthenticated ? "Open dashboard" : "Log in"}
                </Button>
              </Link>
              <a href="#how-it-works">
                <Button variant="secondary" size="lg">
                  How it works
                </Button>
              </a>
            </div>
          </div>

          {/* hero product preview image */}
          <div className="overflow-hidden">
            <img
              src="/images/product-preview.png"
              alt="Product dashboard preview"
              className="w-full object-cover"
              onError={(e) => {
                (e.currentTarget as HTMLImageElement).style.display = "none";
              }}
            />
          </div>
        </section>

        <section
          id="how-it-works"
          className="border-t border-slate-100 bg-slate-100"
        >
          <div className="container-page py-20">
            <h2 className="text-3xl font-thin tracking-widest uppercase text-slate-900">
              How it works
            </h2>
            <div className="mt-10 grid gap-8 sm:grid-cols-3">
              {STEPS.map((step, i) => (
                <div key={step.title}>
                  <div className="flex h-10 w-10 items-center justify-center bg-[#0F6CBD] text-xl font-thin text-white">
                    {i + 1}
                  </div>
                  <h3 className="mt-4 text-lg font-thin text-slate-900">
                    {step.title}
                  </h3>
                  <p className="mt-2 font-extralight text-slate-500">
                    {step.body}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </section>
      </main>

      <footer className="bg-slate-100 border-t border-slate-200">
        <div className="container-page flex h-16 items-center text-sm font-thin text-slate-400">
          MBERE ML — Research by Terry manzi © 2026
        </div>
      </footer>
    </div>
  );
}
