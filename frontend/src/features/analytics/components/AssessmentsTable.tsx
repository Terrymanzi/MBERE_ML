import { Fragment, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { RiskBadge } from "@/components/ui/RiskBadge";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/feedback/states";
import { ChevronDownIcon, SearchIcon } from "@/components/icons";
import { formatDateTime, formatPercent } from "@/lib/format";
import { cn } from "@/lib/cn";
import type { RiskBand } from "@/services";
import type { PredictionRow } from "@/features/dashboard/useDashboard";
import { ShapContributions } from "@/features/prediction/components/ShapContributions";

const PAGE_SIZE = 10;
type BandFilter = RiskBand | "All";

function matchesDriver(row: PredictionRow, query: string): boolean {
  if (!query) return true;
  if (!row.driver) return "one-off".includes(query);
  return (
    row.driver.full_name.toLowerCase().includes(query) ||
    row.driver.license_number.toLowerCase().includes(query)
  );
}

/** Local calendar-day boundary (not UTC) so "to" is inclusive of the whole day. */
function dayBoundary(value: string, end: boolean): number | null {
  if (!value) return null;
  const d = new Date(`${value}T${end ? "23:59:59.999" : "00:00:00"}`);
  return Number.isNaN(d.getTime()) ? null : d.getTime();
}

export function AssessmentsTable({ rows }: { rows: PredictionRow[] }) {
  const [driverQuery, setDriverQuery] = useState("");
  const [band, setBand] = useState<BandFilter>("All");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [page, setPage] = useState(1);
  const [expanded, setExpanded] = useState<Set<number>>(new Set());

  const from = dayBoundary(dateFrom, false);
  const to = dayBoundary(dateTo, true);

  const filtered = useMemo(() => {
    const q = driverQuery.trim().toLowerCase();
    return rows.filter((row) => {
      if (!matchesDriver(row, q)) return false;
      if (band !== "All" && row.prediction.risk_band !== band) return false;
      const t = new Date(row.prediction.created_at).getTime();
      if (from != null && t < from) return false;
      if (to != null && t > to) return false;
      return true;
    });
  }, [rows, driverQuery, band, from, to]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const currentPage = Math.min(page, totalPages);
  const pageRows = filtered.slice(
    (currentPage - 1) * PAGE_SIZE,
    currentPage * PAGE_SIZE,
  );
  const hasFilters =
    driverQuery.trim() !== "" || band !== "All" || dateFrom !== "" || dateTo !== "";

  function clearFilters() {
    setDriverQuery("");
    setBand("All");
    setDateFrom("");
    setDateTo("");
    setPage(1);
  }

  function toggleExpanded(assessmentId: number) {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(assessmentId)) next.delete(assessmentId);
      else next.add(assessmentId);
      return next;
    });
  }

  if (rows.length === 0) {
    return (
      <EmptyState
        title="No assessments yet"
        description="Every prediction you run will be listed here, with a full breakdown of what drove the result."
      />
    );
  }

  return (
    <div>
      <div className="mb-4 flex flex-wrap items-center gap-3">
        <div className="relative w-full max-w-xs">
          <SearchIcon className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <Input
            className="pl-9"
            placeholder="Search by driver name or license…"
            value={driverQuery}
            onChange={(e) => {
              setDriverQuery(e.target.value);
              setPage(1);
            }}
            aria-label="Search by driver"
          />
        </div>

        <div className="w-36">
          <Select
            aria-label="Filter by risk band"
            value={band}
            onChange={(e) => {
              setBand(e.target.value as BandFilter);
              setPage(1);
            }}
          >
            <option value="All">All bands</option>
            <option value="Low">Low</option>
            <option value="Medium">Medium</option>
            <option value="High">High</option>
          </Select>
        </div>

        <div className="flex items-center gap-2">
          <Input
            type="date"
            aria-label="From date"
            value={dateFrom}
            onChange={(e) => {
              setDateFrom(e.target.value);
              setPage(1);
            }}
            className="w-[9.5rem]"
          />
          <span className="text-sm text-slate-400">to</span>
          <Input
            type="date"
            aria-label="To date"
            value={dateTo}
            onChange={(e) => {
              setDateTo(e.target.value);
              setPage(1);
            }}
            className="w-[9.5rem]"
          />
        </div>

        {hasFilters && (
          <Button variant="ghost" size="sm" onClick={clearFilters}>
            Clear filters
          </Button>
        )}

        <span className="ml-auto text-sm text-slate-500">
          {filtered.length} of {rows.length} assessments
        </span>
      </div>

      {filtered.length === 0 ? (
        <EmptyState
          title="No assessments match your filters"
          description="Try a different driver, band, or date range."
          action={
            <Button variant="secondary" size="sm" onClick={clearFilters}>
              Clear filters
            </Button>
          }
        />
      ) : (
        <>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-slate-100 text-xs uppercase tracking-wide text-slate-400">
                  <th className="px-4 py-3 font-medium">Driver</th>
                  <th className="px-4 py-3 font-medium">Predicted class</th>
                  <th className="px-4 py-3 font-medium">Band</th>
                  <th className="px-4 py-3 font-medium">Risk score</th>
                  <th className="px-4 py-3 font-medium">Top factors</th>
                  <th className="px-4 py-3 font-medium">When</th>
                  <th className="px-4 py-3 font-medium" />
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {pageRows.map((row) => {
                  const isOpen = expanded.has(row.assessmentId);
                  const topFeatures = row.prediction.explanation?.top_features ?? [];
                  const method = row.prediction.explanation?.method ?? "none";
                  return (
                    <Fragment key={row.assessmentId}>
                      <tr className="hover:bg-slate-50">
                        <td className="px-4 py-3 font-medium text-slate-900">
                          {row.driver ? (
                            <Link
                              to={`/app/drivers/${row.driver.id}`}
                              className="hover:text-brand-700 hover:underline"
                            >
                              {row.driver.full_name}
                            </Link>
                          ) : (
                            <span className="text-slate-500">One-off</span>
                          )}
                        </td>
                        <td className="px-4 py-3 font-mono text-xs text-slate-600">
                          {row.prediction.predicted_class}
                        </td>
                        <td className="px-4 py-3">
                          <RiskBadge band={row.prediction.risk_band} />
                        </td>
                        <td className="px-4 py-3 tabular-nums text-slate-600">
                          {formatPercent(row.prediction.risk_score)}
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex flex-wrap gap-1">
                            {topFeatures.length === 0 ? (
                              <span className="text-slate-300">—</span>
                            ) : (
                              topFeatures.slice(0, 3).map((f) => (
                                <span
                                  key={f.feature}
                                  className="bg-slate-200 px-2 py-0.5 text-xs text-slate-600"
                                  title={`contribution ${f.contribution.toFixed(4)}`}
                                >
                                  {f.feature}
                                </span>
                              ))
                            )}
                          </div>
                        </td>
                        <td className="px-4 py-3 text-slate-500">
                          {formatDateTime(row.prediction.created_at)}
                        </td>
                        <td className="px-4 py-3 text-right">
                          <button
                            type="button"
                            onClick={() => toggleExpanded(row.assessmentId)}
                            className="inline-flex items-center gap-1 font-medium text-brand-700 hover:underline"
                            aria-expanded={isOpen}
                          >
                            Details
                            <ChevronDownIcon
                              className={cn(
                                "h-3.5 w-3.5 transition-transform",
                                isOpen && "rotate-180",
                              )}
                            />
                          </button>
                        </td>
                      </tr>
                      {isOpen && (
                        <tr className="bg-slate-50/60">
                          <td colSpan={7} className="px-4 py-4">
                            <p className="mb-2 text-xs font-medium uppercase tracking-wide text-slate-400">
                              How each feature affected this prediction ({method})
                            </p>
                            <ShapContributions features={topFeatures} method={method} />
                          </td>
                        </tr>
                      )}
                    </Fragment>
                  );
                })}
              </tbody>
            </table>
          </div>

          {totalPages > 1 && (
            <div className="mt-4 flex items-center justify-between text-sm text-slate-500">
              <span>
                Page {currentPage} of {totalPages}
              </span>
              <div className="flex gap-2">
                <Button
                  variant="secondary"
                  size="sm"
                  disabled={currentPage <= 1}
                  onClick={() => setPage(currentPage - 1)}
                >
                  Previous
                </Button>
                <Button
                  variant="secondary"
                  size="sm"
                  disabled={currentPage >= totalPages}
                  onClick={() => setPage(currentPage + 1)}
                >
                  Next
                </Button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
