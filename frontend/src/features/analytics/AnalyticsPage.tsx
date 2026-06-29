import { PageHeader } from "@/components/layout/PageHeader";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { ErrorState, LoadingState } from "@/components/feedback/states";
import { useDashboard } from "@/features/dashboard/useDashboard";
import { RiskDistributionChart } from "@/features/dashboard/components/RiskDistributionChart";
import { FeatureImportanceChart } from "@/features/dashboard/components/FeatureImportanceChart";
import { PredictionsTrendChart } from "./components/PredictionsTrendChart";
import { RiskScoreHistogram } from "./components/RiskScoreHistogram";

export function AnalyticsPage() {
  const { data, isLoading, isError, error, refetch } = useDashboard();

  return (
    <div>
      <PageHeader
        title="Analytics"
        description="Trends and distributions across all recorded risk assessments."
      />

      {isLoading ? (
        <LoadingState label="Loading analytics…" />
      ) : isError || !data ? (
        <ErrorState error={error} onRetry={() => refetch()} />
      ) : (
        <div className="space-y-6">
          <Card>
            <CardHeader
              title="Prediction trend"
              description="Predictions per day over the last 30 days."
            />
            <CardBody>
              <PredictionsTrendChart rows={data.allPredictions} />
            </CardBody>
          </Card>

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <Card>
              <CardHeader
                title="Risk-score distribution"
                description="All predictions, bucketed by score."
              />
              <CardBody>
                <RiskScoreHistogram rows={data.allPredictions} />
              </CardBody>
            </Card>

            <Card>
              <CardHeader
                title="Risk distribution"
                description="Drivers by latest assessment band."
              />
              <CardBody>
                <RiskDistributionChart counts={data.riskCounts} />
              </CardBody>
            </Card>
          </div>

          <Card>
            <CardHeader
              title="Top risk factors (SHAP)"
              description="Mean absolute contribution across recent predictions."
            />
            <CardBody>
              <FeatureImportanceChart data={data.featureImportance} />
            </CardBody>
          </Card>
        </div>
      )}
    </div>
  );
}
