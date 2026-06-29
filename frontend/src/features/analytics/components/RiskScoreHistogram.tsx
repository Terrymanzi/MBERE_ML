import {
  Bar,
  BarChart,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { PredictionRow } from "@/features/dashboard/useDashboard";
import { EmptyState } from "@/components/feedback/states";

const BINS = 10;
// Risk band thresholds (mirror backend Settings: 0.34 / 0.67).
const LOW_MAX = 0.34;
const MED_MAX = 0.67;

function colorForCenter(center: number): string {
  if (center < LOW_MAX) return "#16a34a";
  if (center < MED_MAX) return "#d97706";
  return "#dc2626";
}

/** Distribution of risk scores across all predictions, in 10% buckets. */
export function RiskScoreHistogram({ rows }: { rows: PredictionRow[] }) {
  if (rows.length === 0) {
    return (
      <EmptyState
        title="No predictions yet"
        description="Risk-score distribution appears once assessments exist."
      />
    );
  }

  const buckets = Array.from({ length: BINS }, (_, i) => ({
    label: `${i * 10}–${(i + 1) * 10}%`,
    center: (i + 0.5) / BINS,
    count: 0,
  }));

  for (const r of rows) {
    const s = Math.min(0.999, Math.max(0, r.prediction.risk_score));
    buckets[Math.floor(s * BINS)].count += 1;
  }

  return (
    <div className="h-72 w-full">
      <ResponsiveContainer>
        <BarChart data={buckets} margin={{ top: 8, right: 12, bottom: 0, left: -16 }}>
          <XAxis
            dataKey="label"
            tick={{ fontSize: 10, fill: "#94a3b8" }}
            axisLine={false}
            tickLine={false}
            interval={0}
            angle={-30}
            textAnchor="end"
            height={48}
          />
          <YAxis
            allowDecimals={false}
            tick={{ fontSize: 11, fill: "#94a3b8" }}
            axisLine={false}
            tickLine={false}
            width={32}
          />
          <Tooltip
            cursor={{ fill: "rgba(148,163,184,0.12)" }}
            formatter={(value: number) => [`${value}`, "predictions"]}
          />
          <Bar dataKey="count" radius={4}>
            {buckets.map((b) => (
              <Cell key={b.label} fill={colorForCenter(b.center)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
