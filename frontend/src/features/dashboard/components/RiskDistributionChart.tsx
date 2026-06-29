import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import type { RiskBand } from "@/services";
import { EmptyState } from "@/components/feedback/states";
import { RISK_BANDS, RISK_COLORS } from "@/lib/format";

export function RiskDistributionChart({
  counts,
}: {
  counts: Record<RiskBand, number>;
}) {
  const data = RISK_BANDS.map((band) => ({
    name: band,
    value: counts[band],
  })).filter((d) => d.value > 0);

  const total = data.reduce((sum, d) => sum + d.value, 0);

  if (total === 0) {
    return (
      <EmptyState
        title="No assessments yet"
        description="Risk distribution appears once drivers have predictions."
      />
    );
  }

  return (
    <div className="flex flex-col items-center gap-4 sm:flex-row">
      <div className="h-52 w-52">
        <ResponsiveContainer>
          <PieChart>
            <Pie
              data={data}
              dataKey="value"
              nameKey="name"
              innerRadius={56}
              outerRadius={84}
              paddingAngle={2}
              stroke="none"
            >
              {data.map((d) => (
                <Cell key={d.name} fill={RISK_COLORS[d.name as RiskBand]} />
              ))}
            </Pie>
            <Tooltip
              formatter={(value: number, name) => [
                `${value} driver${value === 1 ? "" : "s"}`,
                name,
              ]}
            />
            <Legend
              verticalAlign="bottom"
              height={24}
              iconType="circle"
              formatter={(value) => (
                <span className="text-sm text-slate-600">{value}</span>
              )}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>

      <ul className="flex-1 space-y-2">
        {RISK_BANDS.map((band) => (
          <li key={band} className="flex items-center justify-between text-sm">
            <span className="flex items-center gap-2 text-slate-600">
              <span
                className="h-2.5 w-2.5 rounded-full"
                style={{ background: RISK_COLORS[band] }}
              />
              {band}
            </span>
            <span className="font-semibold text-slate-900">{counts[band]}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
