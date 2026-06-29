import type { RiskBand } from "@/services";
import { formatPercent, RISK_COLORS } from "@/lib/format";

/** Risk score on a 0–100% track with Low/Medium/High zones and a marker. */
export function RiskBandMeter({
  score,
  band,
}: {
  score: number;
  band: RiskBand;
}) {
  const pct = Math.min(100, Math.max(0, score * 100));
  return (
    <div>
      <div className="flex items-baseline justify-between">
        <span
          className="text-3xl font-bold tracking-tight"
          style={{ color: RISK_COLORS[band] }}
        >
          {band} risk
        </span>
        <span className="text-2xl font-semibold tabular-nums text-slate-900">
          {formatPercent(score)}
        </span>
      </div>

      <div className="relative mt-4 h-3 w-full overflow-hidden rounded-full">
        {/* zone backdrop: 0–34 / 34–67 / 67–100 */}
        <div className="absolute inset-0 flex">
          <div style={{ width: "34%", background: "#dcfce7" }} />
          <div style={{ width: "33%", background: "#fef3c7" }} />
          <div style={{ width: "33%", background: "#fee2e2" }} />
        </div>
        {/* marker */}
        <div
          className="absolute top-1/2 h-5 w-1.5 -translate-y-1/2 rounded-full ring-2 ring-white"
          style={{ left: `calc(${pct}% - 3px)`, background: RISK_COLORS[band] }}
        />
      </div>
      <div className="mt-1 flex justify-between text-xs text-slate-400">
        <span>Low</span>
        <span>Medium</span>
        <span>High</span>
      </div>
    </div>
  );
}
