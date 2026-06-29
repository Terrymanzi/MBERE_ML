import {
  Bar,
  BarChart,
  Cell,
  LabelList,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { FeatureContribution } from "@/services";
import { EmptyState } from "@/components/feedback/states";

const POSITIVE = "#dc2626"; // pushes risk up
const NEGATIVE = "#2563eb"; // pulls risk down

/**
 * Per-prediction SHAP contributions as a signed horizontal bar chart.
 * Red bars push the predicted class up; blue bars pull it down.
 */
export function ShapContributions({
  features,
  method,
}: {
  features: FeatureContribution[];
  method: string;
}) {
  if (!features || features.length === 0 || method === "none") {
    return (
      <EmptyState
        title="No explanation available"
        description="The active model didn't return feature contributions for this prediction."
      />
    );
  }

  const data = [...features]
    .sort((a, b) => a.abs_contribution - b.abs_contribution)
    .map((f) => ({
      name: f.feature,
      value: Number(f.contribution.toFixed(4)),
      raw: f.value,
    }));

  const height = Math.max(180, data.length * 34);

  return (
    <div style={{ width: "100%", height }}>
      <ResponsiveContainer>
        <BarChart
          layout="vertical"
          data={data}
          margin={{ top: 4, right: 56, bottom: 4, left: 8 }}
        >
          <XAxis type="number" hide />
          <YAxis
            type="category"
            dataKey="name"
            width={110}
            tick={{ fontSize: 12, fill: "#475569" }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip
            cursor={{ fill: "rgba(148,163,184,0.12)" }}
            formatter={(value: number) => [value.toFixed(4), "contribution"]}
          />
          <Bar dataKey="value" radius={4} barSize={16}>
            {data.map((d) => (
              <Cell key={d.name} fill={d.value >= 0 ? POSITIVE : NEGATIVE} />
            ))}
            <LabelList
              dataKey="value"
              position="right"
              formatter={(v: number) => v.toFixed(3)}
              style={{ fontSize: 11, fill: "#64748b" }}
            />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
