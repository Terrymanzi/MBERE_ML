import { useQuery } from "@tanstack/react-query";
import {
  getDriverRiskHistory,
  listDrivers,
  type DriverRead,
  type PredictionRead,
  type RiskBand,
} from "@/services";
import { queryKeys } from "@/lib/queryKeys";

export interface PredictionRow {
  assessmentId: number;
  driver: DriverRead | null;
  prediction: PredictionRead;
}

export interface FeatureImportance {
  feature: string;
  importance: number;
}

export interface DashboardData {
  totalDrivers: number;
  totalAssessments: number;
  predictionsToday: number;
  /** Risk band of each driver's most recent assessment. */
  riskCounts: Record<RiskBand, number>;
  driversAssessed: number;
  latestPredictions: PredictionRow[];
  /** All predictions across the fleet, most-recent-first. */
  allPredictions: PredictionRow[];
  /** Mean |SHAP contribution| per feature across recent predictions. */
  featureImportance: FeatureImportance[];
}

const EMPTY_COUNTS: Record<RiskBand, number> = { High: 0, Medium: 0, Low: 0 };
const RECENT_FOR_IMPORTANCE = 30;

function isToday(iso: string): boolean {
  const d = new Date(iso);
  const now = new Date();
  return (
    d.getFullYear() === now.getFullYear() &&
    d.getMonth() === now.getMonth() &&
    d.getDate() === now.getDate()
  );
}

/**
 * The backend has no aggregate endpoint, so the dashboard is composed from the
 * driver list plus each driver's risk history (real data, fanned out). Fine for
 * a fleet of this size; the result is cached under one query key.
 */
async function fetchDashboard(signal?: AbortSignal): Promise<DashboardData> {
  const drivers = await listDrivers({ limit: 200, offset: 0 }, signal);

  const histories = await Promise.all(
    drivers.map((d) =>
      getDriverRiskHistory(d.id, signal).then(
        (assessments) => ({ driver: d, assessments }),
        () => ({ driver: d, assessments: [] }),
      ),
    ),
  );

  const driverById = new Map(drivers.map((d) => [d.id, d]));
  const riskCounts: Record<RiskBand, number> = { ...EMPTY_COUNTS };
  const rows: PredictionRow[] = [];
  let driversAssessed = 0;

  for (const { driver, assessments } of histories) {
    // assessments arrive most-recent-first
    const withPrediction = assessments.filter((a) => a.prediction != null);
    if (withPrediction.length > 0) {
      driversAssessed += 1;
      const latestBand = withPrediction[0].prediction!.risk_band;
      if (latestBand in riskCounts) riskCounts[latestBand] += 1;
    }
    for (const a of withPrediction) {
      rows.push({
        assessmentId: a.id,
        driver,
        prediction: a.prediction!,
      });
    }
  }

  rows.sort(
    (a, b) =>
      new Date(b.prediction.created_at).getTime() -
      new Date(a.prediction.created_at).getTime(),
  );

  const featureImportance = aggregateImportance(rows.slice(0, RECENT_FOR_IMPORTANCE));
  const predictionsToday = rows.filter((r) => isToday(r.prediction.created_at)).length;

  void driverById; // map kept for parity with row.driver lookups

  return {
    totalDrivers: drivers.length,
    totalAssessments: rows.length,
    predictionsToday,
    riskCounts,
    driversAssessed,
    latestPredictions: rows.slice(0, 8),
    allPredictions: rows,
    featureImportance,
  };
}

function aggregateImportance(rows: PredictionRow[]): FeatureImportance[] {
  const sums = new Map<string, number>();
  let counted = 0;
  for (const { prediction } of rows) {
    const top = prediction.explanation?.top_features;
    if (!Array.isArray(top)) continue;
    counted += 1;
    for (const f of top) {
      sums.set(f.feature, (sums.get(f.feature) ?? 0) + Math.abs(f.contribution));
    }
  }
  if (counted === 0) return [];
  return Array.from(sums.entries())
    .map(([feature, total]) => ({ feature, importance: total / counted }))
    .sort((a, b) => b.importance - a.importance)
    .slice(0, 8);
}

export function useDashboard() {
  return useQuery({
    queryKey: queryKeys.dashboard,
    queryFn: ({ signal }) => fetchDashboard(signal),
    staleTime: 20_000,
  });
}
