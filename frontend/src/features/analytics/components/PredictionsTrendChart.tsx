import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { PredictionRow } from "@/features/dashboard/useDashboard";
import { EmptyState } from "@/components/feedback/states";

function dayKey(iso: string): string {
  return new Date(iso).toISOString().slice(0, 10);
}

/** Predictions per day over the last `days` window. */
export function PredictionsTrendChart({
  rows,
  days = 30,
}: {
  rows: PredictionRow[];
  days?: number;
}) {
  if (rows.length === 0) {
    return (
      <EmptyState
        title="No predictions yet"
        description="The trend appears once assessments are recorded."
      />
    );
  }

  const counts = new Map<string, number>();
  for (const r of rows) {
    const k = dayKey(r.prediction.created_at);
    counts.set(k, (counts.get(k) ?? 0) + 1);
  }

  // Build a continuous date axis for the window ending today.
  const data: Array<{ date: string; label: string; count: number }> = [];
  const today = new Date();
  for (let i = days - 1; i >= 0; i--) {
    const d = new Date(today);
    d.setDate(today.getDate() - i);
    const key = d.toISOString().slice(0, 10);
    data.push({
      date: key,
      label: d.toLocaleDateString(undefined, { month: "short", day: "numeric" }),
      count: counts.get(key) ?? 0,
    });
  }

  return (
    <div className="h-72 w-full">
      <ResponsiveContainer>
        <AreaChart data={data} margin={{ top: 8, right: 12, bottom: 0, left: -16 }}>
          <defs>
            <linearGradient id="trendFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#2563eb" stopOpacity={0.25} />
              <stop offset="100%" stopColor="#2563eb" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
          <XAxis
            dataKey="label"
            tick={{ fontSize: 11, fill: "#94a3b8" }}
            axisLine={false}
            tickLine={false}
            interval="preserveStartEnd"
            minTickGap={24}
          />
          <YAxis
            allowDecimals={false}
            tick={{ fontSize: 11, fill: "#94a3b8" }}
            axisLine={false}
            tickLine={false}
            width={32}
          />
          <Tooltip
            formatter={(value: number) => [`${value}`, "predictions"]}
            labelFormatter={(label) => String(label)}
          />
          <Area
            type="monotone"
            dataKey="count"
            stroke="#2563eb"
            strokeWidth={2}
            fill="url(#trendFill)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
