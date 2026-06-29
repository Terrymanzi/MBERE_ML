import { Link } from "react-router-dom";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { ErrorState, LoadingState } from "@/components/feedback/states";
import {
  DriversIcon,
  ModelsIcon,
  PlusIcon,
  PredictIcon,
} from "@/components/icons";
import { useDashboard } from "./useDashboard";
import { activeModel, useModels } from "@/features/models/useModels";
import { StatCard } from "./components/StatCard";
import { RiskDistributionChart } from "./components/RiskDistributionChart";
import { FeatureImportanceChart } from "./components/FeatureImportanceChart";
import { LatestPredictionsTable } from "./components/LatestPredictionsTable";
import { MetricsGrid } from "@/features/models/components/MetricsGrid";

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

export function DashboardPage() {
  const dashboard = useDashboard();
  const models = useModels();
  const active = activeModel(models.data);

  return (
    <div>
      <PageHeader
        title="Dashboard"
        description="Fleet risk at a glance, powered by the latest active model."
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
        <ErrorState
          error={dashboard.error}
          onRetry={() => dashboard.refetch()}
        />
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
              accent="green"
            />
            <StatCard
              label="High-risk drivers"
              value={dashboard.data.riskCounts.High}
              hint={`${dashboard.data.riskCounts.Medium} medium · ${dashboard.data.riskCounts.Low} low`}
              icon={<HighRiskIcon />}
              accent="red"
            />
            <StatCard
              label="Active model"
              value={
                active ? (
                  <span className="text-2xl">
                    {active.name}{" "}
                    <span className="text-base font-medium text-slate-400">
                      v{active.version}
                    </span>
                  </span>
                ) : (
                  "—"
                )
              }
              hint={active ? active.dataset_name : "No active model"}
              icon={<ModelsIcon className="h-5 w-5" />}
              accent="brand"
            />
          </div>

          {/* Charts row */}
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
                title="Risk factors (SHAP)"
                description="Mean absolute feature contribution across recent predictions."
              />
              <CardBody>
                <FeatureImportanceChart
                  data={dashboard.data.featureImportance}
                />
              </CardBody>
            </Card>
          </div>

          {/* Table + model performance */}
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
            <Card className="lg:col-span-2">
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
                <LatestPredictionsTable
                  rows={dashboard.data.latestPredictions}
                />
              </CardBody>
            </Card>

            <Card className="lg:col-span-1">
              <CardHeader
                title="Model performance"
                description="Cross-validation metrics."
              />
              <CardBody>
                {models.isLoading ? (
                  <LoadingState label="Loading model…" />
                ) : models.isError ? (
                  <ErrorState
                    error={models.error}
                    onRetry={() => models.refetch()}
                  />
                ) : active ? (
                  <MetricsGrid metrics={active.metrics} />
                ) : (
                  <p className="text-sm text-slate-500">
                    No active model registered.
                  </p>
                )}
              </CardBody>
            </Card>
          </div>

          {dashboard.data.totalDrivers === 0 && (
            <Card>
              <CardBody className="flex flex-col items-center gap-3 py-10 text-center">
                <p className="text-sm font-medium text-slate-900">
                  Your fleet is empty
                </p>
                <p className="max-w-md text-sm text-slate-500">
                  Add drivers and run predictions to populate these widgets.
                </p>
                <Link to="/app/drivers">
                  <Button size="sm">
                    <PlusIcon className="h-4 w-4" />
                    Add drivers
                  </Button>
                </Link>
              </CardBody>
            </Card>
          )}
        </div>
      )}
    </div>
  );
}
