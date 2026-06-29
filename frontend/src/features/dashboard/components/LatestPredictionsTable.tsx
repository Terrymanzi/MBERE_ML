import { Link } from "react-router-dom";
import { RiskBadge } from "@/components/ui/RiskBadge";
import { EmptyState } from "@/components/feedback/states";
import { formatPercent, relativeTime } from "@/lib/format";
import type { PredictionRow } from "../useDashboard";

export function LatestPredictionsTable({ rows }: { rows: PredictionRow[] }) {
  if (rows.length === 0) {
    return (
      <EmptyState
        title="No predictions yet"
        description="Recent risk assessments will appear here."
      />
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-sm">
        <thead>
          <tr className="border-b border-slate-100 text-xs uppercase tracking-wide text-slate-400">
            <th className="px-4 py-3 font-medium">Driver</th>
            <th className="px-4 py-3 font-medium">Risk score</th>
            <th className="px-4 py-3 font-medium">Band</th>
            <th className="px-4 py-3 font-medium">When</th>
            <th className="px-4 py-3 font-medium" />
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {rows.map((row) => (
            <tr key={row.assessmentId} className="hover:bg-slate-50">
              <td className="px-4 py-3 font-medium text-slate-900">
                {row.driver ? row.driver.full_name : "One-off"}
              </td>
              <td className="px-4 py-3 tabular-nums text-slate-600">
                {formatPercent(row.prediction.risk_score)}
              </td>
              <td className="px-4 py-3">
                <RiskBadge band={row.prediction.risk_band} />
              </td>
              <td className="px-4 py-3 text-slate-500">
                {relativeTime(row.prediction.created_at)}
              </td>
              <td className="px-4 py-3 text-right">
                {row.driver && (
                  <Link
                    to={`/app/drivers/${row.driver.id}`}
                    className="font-medium text-brand-700 hover:underline"
                  >
                    View
                  </Link>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
