import { formatPercent } from "@/lib/format";

/** Class-probability distribution as labelled horizontal bars. */
export function ProbabilityBars({
  probabilities,
  predictedClass,
}: {
  probabilities: Record<string, number>;
  predictedClass: string;
}) {
  const entries = Object.entries(probabilities).sort((a, b) => b[1] - a[1]);

  return (
    <ul className="space-y-3">
      {entries.map(([label, value]) => {
        const isPredicted = label === predictedClass;
        return (
          <li key={label}>
            <div className="mb-1 flex items-center justify-between text-sm">
              <span
                className={isPredicted ? "font-semibold text-slate-900" : "text-slate-600"}
              >
                {label}
              </span>
              <span
                className={
                  isPredicted
                    ? "font-semibold text-slate-900"
                    : "tabular-nums text-slate-500"
                }
              >
                {formatPercent(value)}
              </span>
            </div>
            <div className="h-2.5 w-full overflow-hidden rounded-full bg-slate-100">
              <div
                className={isPredicted ? "h-full bg-brand-600" : "h-full bg-brand-300"}
                style={{ width: `${Math.max(2, value * 100)}%` }}
              />
            </div>
          </li>
        );
      })}
    </ul>
  );
}
