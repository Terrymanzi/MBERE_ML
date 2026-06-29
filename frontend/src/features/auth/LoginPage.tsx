import { useState } from "react";
import type { FormEvent } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "./AuthContext";
import { ApiError, register as registerRequest } from "@/services";
import { Logo } from "@/components/layout/Logo";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { toErrorMessage } from "@/components/feedback/states";

type Mode = "login" | "register";

interface LocationState {
  from?: { pathname: string };
}

export function LoginPage() {
  const { login, isAuthenticated, isInitialising } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from =
    (location.state as LocationState | null)?.from?.pathname ?? "/app";

  const [mode, setMode] = useState<Mode>("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  if (isAuthenticated && !isInitialising) {
    return <Navigate to={from} replace />;
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      if (mode === "register") {
        await registerRequest({ email, password, full_name: fullName || null });
      }
      await login(email, password);
      navigate(from, { replace: true });
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        setError("Incorrect email or password.");
      } else {
        setError(toErrorMessage(err));
      }
    } finally {
      setSubmitting(false);
    }
  }

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

      <main className="container-page grid gap-16 py-16 lg:grid-cols-2 lg:items-center lg:py-24">
        <div className="mx-auto w-full max-w-md">
          <h1 className="text-4xl font-thin tracking-tight text-slate-900">
            {mode === "login" ? "Log in to your account" : "Create an account"}
          </h1>
          <p className="mt-3 text-slate-500 font-thin">
            {mode === "login"
              ? "Access the fleet dashboard, drivers, and predictions."
              : "Register a fleet operator account to get started."}
          </p>

          <form
            onSubmit={onSubmit}
            className="mt-10 space-y-5 font-thin"
            noValidate
          >
            {mode === "register" && (
              <Input
                label="Full name"
                type="text"
                autoComplete="name"
                placeholder="John Doe"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
              />
            )}
            <Input
              label="Email"
              type="email"
              autoComplete="username"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <Input
              label="Password"
              type="password"
              autoComplete={
                mode === "login" ? "current-password" : "new-password"
              }
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={8}
              hint={mode === "register" ? "At least 8 characters." : undefined}
            />

            {error && (
              <div
                role="alert"
                className="bg-red-50 px-4 py-3 text-sm font-mono text-red-600"
              >
                {error}
              </div>
            )}

            <Button
              type="submit"
              size="lg"
              loading={submitting}
              className="w-full"
            >
              {mode === "login" ? "Log in" : "Create account"}
            </Button>
          </form>

          <p className="mt-6 text-sm font-thin text-slate-500">
            {mode === "login" ? (
              <>
                Don't have an account?{" "}
                <button
                  type="button"
                  onClick={() => {
                    setMode("register");
                    setError(null);
                  }}
                  className="font-mono text-[#0F6CBD] hover:underline"
                >
                  Register here
                </button>
              </>
            ) : (
              <>
                Already have an account?{" "}
                <button
                  type="button"
                  onClick={() => {
                    setMode("login");
                    setError(null);
                  }}
                  className="font-mono text-brand-700 hover:underline"
                >
                  Log in
                </button>
              </>
            )}
          </p>
        </div>

        <div className="hidden overflow-hidden lg:block">
          <img
            src="/images/product-preview.png"
            alt="Product preview"
            className="w-full object-cover"
            onError={(e) => {
              (e.currentTarget as HTMLImageElement).style.display = "none";
            }}
          />
        </div>
      </main>
    </div>
  );
}
