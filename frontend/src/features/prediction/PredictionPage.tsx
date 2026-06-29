import { useSearchParams } from "react-router-dom";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import {
  EmptyState,
  ErrorState,
  LoadingState,
  toErrorMessage,
} from "@/components/feedback/states";
import { ApiError } from "@/services";
import { useDrivers } from "@/features/drivers/useDrivers";
import { useFeatureContract, usePredict } from "./usePrediction";
import { PredictionForm } from "./components/PredictionForm";
import { PredictionResult } from "./components/PredictionResult";

export function PredictionPage() {
  const [searchParams] = useSearchParams();
  const driverIdParam = searchParams.get("driver_id");
  const initialDriverId = driverIdParam ? Number(driverIdParam) : null;

  const contractQuery = useFeatureContract();
  const driversQuery = useDrivers();
  const predictMutation = usePredict();

  const modelUnavailable =
    contractQuery.error instanceof ApiError && contractQuery.error.status === 503;

  return (
    <div>
      <PageHeader
        title="Run a prediction"
        description="Enter feature values from the active model's contract to get a risk band, class probabilities, and the features that drove the result."
      />

      {contractQuery.isLoading ? (
        <LoadingState label="Loading feature contract…" />
      ) : modelUnavailable ? (
        <EmptyState
          title="No model is loaded"
          description="The backend is running in a degraded state. Point it at a model artifact and reload."
        />
      ) : contractQuery.isError || !contractQuery.data ? (
        <ErrorState error={contractQuery.error} onRetry={() => contractQuery.refetch()} />
      ) : (
        <div className="grid gap-6 lg:grid-cols-2">
          <Card>
            <CardHeader
              title="Features"
              description={`${contractQuery.data.model.name} v${contractQuery.data.model.version} · ${contractQuery.data.input_features.length} inputs`}
            />
            <CardBody>
              <PredictionForm
                features={contractQuery.data.input_features}
                drivers={driversQuery.data ?? []}
                initialDriverId={initialDriverId}
                isSubmitting={predictMutation.isPending}
                onSubmit={(features, driverId) =>
                  predictMutation.mutate({ features, driver_id: driverId })
                }
              />
            </CardBody>
          </Card>

          <div>
            {predictMutation.isPending ? (
              <Card>
                <CardBody>
                  <LoadingState label="Scoring…" />
                </CardBody>
              </Card>
            ) : predictMutation.isError ? (
              <Card>
                <CardBody>
                  <div
                    role="alert"
                    className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700"
                  >
                    <p className="font-medium">Prediction failed</p>
                    <p className="mt-1">{toErrorMessage(predictMutation.error)}</p>
                    <FeatureErrorList error={predictMutation.error} />
                  </div>
                </CardBody>
              </Card>
            ) : predictMutation.data ? (
              <PredictionResult result={predictMutation.data} />
            ) : (
              <Card>
                <CardBody>
                  <EmptyState
                    title="No prediction yet"
                    description="Fill in the feature values and run a prediction to see the risk band and explanation here."
                  />
                </CardBody>
              </Card>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

/** Surface the per-feature messages from a 422 validation error, if present. */
function FeatureErrorList({ error }: { error: unknown }) {
  if (!(error instanceof ApiError) || error.status !== 422) return null;
  const detail = error.detail as { detail?: { errors?: string[] } } | undefined;
  const errors = detail?.detail?.errors;
  if (!Array.isArray(errors) || errors.length === 0) return null;
  return (
    <ul className="mt-2 list-inside list-disc space-y-0.5 text-xs">
      {errors.map((e) => (
        <li key={e}>{e}</li>
      ))}
    </ul>
  );
}
