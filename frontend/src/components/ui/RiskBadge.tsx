import type { RiskBand } from "@/services";
import { cn } from "@/lib/cn";
import { riskBadgeClasses } from "@/lib/format";

export function RiskBadge({
  band,
  className,
}: {
  band: RiskBand;
  className?: string;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center px-2.5 py-1 text-xs font-mono ring-1 ring-inset",
        riskBadgeClasses(band),
        className,
      )}
    >
      {band}
    </span>
  );
}
