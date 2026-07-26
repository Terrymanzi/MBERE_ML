import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { RiskAssessmentRead } from "@/services";
import { formatDate } from "@/lib/format";
import { EmptyState } from "@/components/feedback/states";

/** This driver's risk score over time, oldest -> newest (left to right). */
export function RiskScoreTrendChart({
  assessments,
}: {
  assessments: RiskAssessmentRead[];
}) {
  const withScores = assessments.filter((a) => a.prediction != null);
  if (withScores.length < 2) {
    return (
      <EmptyState
        title="Not enough history yet"
        description="A trend appears once this driver has at least two assessments."
      />
    );
  }

  const data = [...withScores]
    .sort(
      (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime(),
    )
    .map((a) => ({
      label: formatDate(a.created_at),
      score: Number((a.prediction!.risk_score * 100).toFixed(1)),
    }));

  return (
    <div className="h-48 w-full">
      <ResponsiveContainer>
        <LineChart data={data} margin={{ top: 8, right: 12, bottom: 0, left: -16 }}>
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
            domain={[0, 100]}
            tick={{ fontSize: 11, fill: "#94a3b8" }}
            axisLine={false}
            tickLine={false}
            width={32}
          />
          <Tooltip formatter={(value: number) => [`${value}%`, "risk score"]} />
          <Line
            type="monotone"
            dataKey="score"
            stroke="#2563eb"
            strokeWidth={2}
            dot={{ r: 3 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
