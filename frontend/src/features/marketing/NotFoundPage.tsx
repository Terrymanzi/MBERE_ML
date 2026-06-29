import { Link } from "react-router-dom";
import { Button } from "@/components/ui/Button";

export function NotFoundPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 px-6 text-center">
      <p className="text-sm font-semibold uppercase tracking-wide text-brand-600">
        404
      </p>
      <h1 className="text-3xl font-bold tracking-tight text-slate-900">
        Page not found
      </h1>
      <p className="max-w-md text-slate-500">
        The page you're looking for doesn't exist or has moved.
      </p>
      <Link to="/">
        <Button variant="secondary">Back home</Button>
      </Link>
    </div>
  );
}
