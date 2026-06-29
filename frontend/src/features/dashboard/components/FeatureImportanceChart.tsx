import {
  Bar,
  BarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { FeatureImportance } from "../useDashboard";
import { EmptyState } from "@/components/feedback/states";

/**
 * Mean absolute SHAP contribution per feature across recent predictions —
 * the closest thing to "global feature importance" we can derive from the API.
 */
export function FeatureImportanceChart({
  data,
}: {
  data: FeatureImportance[];
}) {
  if (data.length === 0) {
    return (
      <EmptyState
        title="No explanations yet"
        description="Run predictions to surface which features drive risk."
      />
    );
  }

  const chartData = [...data]
    .sort((a, b) => a.importance - b.importance)
    .map((d) => ({ name: d.feature, value: Number(d.importance.toFixed(4)) }));

  const height = Math.max(180, chartData.length * 32);

  return (
    <div style={{ width: "100%", height }}>
      <ResponsiveContainer>
        <BarChart
          layout="vertical"
          data={chartData}
          margin={{ top: 4, right: 16, bottom: 4, left: 8 }}
        >
          <XAxis type="number" hide />
          <YAxis
            type="category"
            dataKey="name"
            width={120}
            tick={{ fontSize: 12, fill: "#475569" }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip
            cursor={{ fill: "rgba(148,163,184,0.12)" }}
            formatter={(value: number) => [value.toFixed(4), "mean |SHAP|"]}
          />
          <Bar dataKey="value" fill="#2563eb" radius={4} barSize={16} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
