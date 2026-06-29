import { forwardRef, useId } from "react";
import type { SelectHTMLAttributes } from "react";
import { cn } from "@/lib/cn";

export interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  hint?: string;
  error?: string;
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(function Select(
  { label, hint, error, className, id, children, ...rest },
  ref,
) {
  const autoId = useId();
  const selectId = id ?? autoId;
  return (
    <div className="w-full">
      {label && (
        <label htmlFor={selectId} className="mb-1.5 block text-sm font-medium text-slate-700">
          {label}
        </label>
      )}
      <select
        ref={ref}
        id={selectId}
        className={cn(
          "block w-full rounded-lg border-0 bg-white px-3.5 py-2.5 text-slate-900 shadow-sm",
          "ring-1 ring-inset ring-slate-300",
          "focus:ring-2 focus:ring-inset focus:ring-brand-600",
          "disabled:cursor-not-allowed disabled:bg-slate-50",
          error && "ring-red-400 focus:ring-red-500",
          className,
        )}
        {...rest}
      >
        {children}
      </select>
      {error ? (
        <p className="mt-1.5 text-sm text-red-600">{error}</p>
      ) : hint ? (
        <p className="mt-1.5 text-sm text-slate-500">{hint}</p>
      ) : null}
    </div>
  );
});
