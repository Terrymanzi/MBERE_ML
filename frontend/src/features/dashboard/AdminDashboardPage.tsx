import { Link } from "react-router-dom";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { ErrorState, LoadingState } from "@/components/feedback/states";
import { DriversIcon, PredictIcon, SettingsIcon } from "@/components/icons";
import { useDashboard } from "./useDashboard";
import { useHealth } from "@/features/system/useHealth";
import { StatCard } from "./components/StatCard";
import { RiskDistributionChart } from "./components/RiskDistributionChart";
import { LatestPredictionsTable } from "./components/LatestPredictionsTable";
import { ModelRegistrySummary } from "./components/ModelRegistrySummary";

function HighRiskIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      className="h-5 w-5"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M12 9v4m0 4h.01M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z"
      />
    </svg>
  );
}

function systemStatusBadge(health: ReturnType<typeof useHealth>) {
  if (health.isLoading) return <Badge tone="neutral">Checking…</Badge>;
  if (health.isError || !health.data) return <Badge tone="red">Offline</Badge>;
  if (health.data.status === "ok") return <Badge tone="green">Healthy</Badge>;
  return <Badge tone="amber">Degraded</Badge>;
}

export function AdminDashboardPage() {
  const dashboard = useDashboard();
  const health = useHealth();

  return (
    <div>
      <PageHeader
        title="Dashboard"
        description="Fleet risk and model registry, powered by the latest active model."
        actions={
          <Link to="/app/predict">
            <Button>
              <PredictIcon className="h-4 w-4" />
              Run prediction
            </Button>
          </Link>
        }
      />

      {dashboard.isLoading ? (
        <LoadingState label="Loading dashboard…" />
      ) : dashboard.isError || !dashboard.data ? (
        <ErrorState error={dashboard.error} onRetry={() => dashboard.refetch()} />
      ) : (
        <div className="space-y-6">
          {/* KPI row */}
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <StatCard
              label="Total drivers"
              value={dashboard.data.totalDrivers}
              hint={`${dashboard.data.driversAssessed} assessed`}
              icon={<DriversIcon className="h-5 w-5" />}
              accent="brand"
            />
            <StatCard
              label="Predictions today"
              value={dashboard.data.predictionsToday}
              hint={`${dashboard.data.totalAssessments} all-time`}
              icon={<PredictIcon className="h-5 w-5" />}
              accent="brand"
            />
            <StatCard
              label="High-risk drivers"
              value={dashboard.data.riskCounts.High}
              hint={`${dashboard.data.riskCounts.Medium} medium · ${dashboard.data.riskCounts.Low} low`}
              icon={<HighRiskIcon />}
              accent="brand"
            />
            <StatCard
              label="System status"
              value={systemStatusBadge(health)}
              hint={health.data?.db_ok ? "Database connected" : "Database unavailable"}
              icon={<SettingsIcon className="h-5 w-5" />}
              accent="brand"
            />
          </div>

          {/* Charts + registry row */}
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
            <Card className="lg:col-span-1">
              <CardHeader
                title="Risk distribution"
                description="By each driver's latest assessment."
              />
              <CardBody>
                <RiskDistributionChart counts={dashboard.data.riskCounts} />
              </CardBody>
            </Card>

            <Card className="lg:col-span-2">
              <CardHeader
                title="Model registry"
                description="Catalog models and whether each passes the deployment decision gate."
                action={
                  <Link
                    to="/app/models"
                    className="text-sm font-medium text-brand-700 hover:underline"
                  >
                    Manage models
                  </Link>
                }
              />
              <CardBody className="pt-0">
                <ModelRegistrySummary />
              </CardBody>
            </Card>
          </div>

          {/* Recent predictions */}
          <Card>
            <CardHeader
              title="Latest predictions"
              description="Most recent risk assessments across the fleet."
              action={
                <Link
                  to="/app/analytics"
                  className="text-sm font-medium text-brand-700 hover:underline"
                >
                  View analytics
                </Link>
              }
            />
            <CardBody className="pt-0">
              <LatestPredictionsTable rows={dashboard.data.latestPredictions} />
            </CardBody>
          </Card>
        </div>
      )}
    </div>
  );
}
