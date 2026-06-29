import type { ReactNode } from "react";
import { ApiError } from "@/services";
import { Spinner } from "@/components/ui/Spinner";
import { Button } from "@/components/ui/Button";
import { cn } from "@/lib/cn";

export function LoadingState({
  label = "Loading…",
  className,
}: {
  label?: string;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center gap-3 py-12 text-slate-500",
        className,
      )}
    >
      <Spinner className="h-6 w-6 text-brand-600" />
      <p className="text-sm">{label}</p>
    </div>
  );
}

/** Skeleton block for content-shaped placeholders. */
export function Skeleton({ className }: { className?: string }) {
  return <div className={cn("animate-pulse rounded-md bg-slate-100", className)} />;
}

export function toErrorMessage(error: unknown): string {
  if (error instanceof ApiError) return error.message;
  if (error instanceof Error) return error.message;
  return "Something went wrong.";
}

export function ErrorState({
  error,
  onRetry,
  className,
}: {
  error: unknown;
  onRetry?: () => void;
  className?: string;
}) {
  const status = error instanceof ApiError ? error.status : undefined;
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center gap-3 rounded-xl border border-red-100 bg-red-50/50 py-12 px-6 text-center",
        className,
      )}
      role="alert"
    >
      <div className="flex h-10 w-10 items-center justify-center rounded-full bg-red-100 text-red-600">
        <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="2">
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v4m0 4h.01M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0Z" />
        </svg>
      </div>
      <div>
        <p className="text-sm font-medium text-slate-900">
          {status === 0 ? "Can't reach the server" : "Couldn't load this"}
        </p>
        <p className="mt-1 text-sm text-slate-500">{toErrorMessage(error)}</p>
      </div>
      {onRetry && (
        <Button variant="secondary" size="sm" onClick={onRetry}>
          Try again
        </Button>
      )}
    </div>
  );
}

export function EmptyState({
  title,
  description,
  action,
  icon,
  className,
}: {
  title: string;
  description?: string;
  action?: ReactNode;
  icon?: ReactNode;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center gap-3 rounded-xl border border-dashed border-slate-200 py-12 px-6 text-center",
        className,
      )}
    >
      {icon && <div className="text-slate-300">{icon}</div>}
      <div>
        <p className="text-sm font-medium text-slate-900">{title}</p>
        {description && <p className="mt-1 text-sm text-slate-500">{description}</p>}
      </div>
      {action}
    </div>
  );
}

/**
 * One place to express the loading / error / empty / data state machine, so
 * every data view renders these consistently.
 */
export function QueryState<T>({
  isLoading,
  isError,
  error,
  data,
  onRetry,
  isEmpty,
  loadingFallback,
  emptyFallback,
  children,
}: {
  isLoading: boolean;
  isError: boolean;
  error?: unknown;
  data: T | undefined;
  onRetry?: () => void;
  isEmpty?: (data: T) => boolean;
  loadingFallback?: ReactNode;
  emptyFallback?: ReactNode;
  children: (data: T) => ReactNode;
}) {
  if (isLoading) return <>{loadingFallback ?? <LoadingState />}</>;
  if (isError) return <ErrorState error={error} onRetry={onRetry} />;
  if (data === undefined) return <ErrorState error={error} onRetry={onRetry} />;
  if (isEmpty?.(data)) {
    return <>{emptyFallback ?? <EmptyState title="Nothing here yet" />}</>;
  }
  return <>{children(data)}</>;
}
