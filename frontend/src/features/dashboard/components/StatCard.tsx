import type { ReactNode } from "react";
import { Card } from "@/components/ui/Card";
import { cn } from "@/lib/cn";

export function StatCard({
  label,
  value,
  hint,
  icon,
  accent,
}: {
  label: string;
  value: ReactNode;
  hint?: string;
  icon?: ReactNode;
  accent?: "brand" | "red" | "amber" | "green";
}) {
  const accentClasses: Record<string, string> = {
    brand: "bg-brand-50 text-brand-600",
    red: "bg-red-50 text-red-600",
    amber: "bg-amber-50 text-amber-600",
    green: "bg-green-50 text-green-600",
  };
  return (
    <Card className="p-5">
      <div className="flex items-start justify-between">
        <p className="text-sm font-mono text-slate-500">{label}</p>
        {icon && (
          <span
            className={cn(
              "flex h-9 w-9 items-center justify-center rounded-lg",
              accent ? accentClasses[accent] : "bg-slate-100 text-slate-500",
            )}
          >
            {icon}
          </span>
        )}
      </div>
      <p className="mt-3 text-3xl font-mono tracking-tight text-slate-900">
        {value}
      </p>
      {hint && <p className="mt-1 text-sm text-slate-400">{hint}</p>}
    </Card>
  );
}
