import { PageHeader } from "@/components/layout/PageHeader";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import {
  EmptyState,
  ErrorState,
  LoadingState,
  toErrorMessage,
} from "@/components/feedback/states";
import type { ModelCatalogEntry } from "@/services";
import { useActivateModel, useModelCatalog } from "./useModels";
import { MetricsGrid } from "./components/MetricsGrid";

function ModelCard({
  entry,
  onActivate,
  isActivating,
}: {
  entry: ModelCatalogEntry;
  onActivate: (name: string) => void;
  isActivating: boolean;
}) {
  const { metrics_test } = entry;

  return (
    <Card>
      <CardHeader
        title={
          <span className="flex items-center gap-2">
            {entry.name}
            <span className="text-sm font-normal text-slate-400">v{entry.version}</span>
            {entry.is_active && <Badge tone="green">Active</Badge>}
          </span>
        }
        description={`${entry.dataset_name} · ${entry.kind}`}
      />
      <CardBody className="space-y-5">
        <div className="flex flex-wrap gap-2">
          {entry.target_classes.map((c) => (
            <Badge key={c} tone="brand">
              {c}
            </Badge>
          ))}
        </div>

        {metrics_test ? (
          <div>
            <MetricsGrid
              metrics={{
                accuracy: metrics_test.accuracy,
                f1_macro: metrics_test.f1_macro,
                recall_macro: metrics_test.recall_macro,
                precision_macro: metrics_test.precision_macro,
                roc_auc_ovr_macro: metrics_test.roc_auc_ovr_macro,
              }}
            />
            <p className="mt-3 text-xs text-slate-400">
              Held-out test set · n = {metrics_test.n_samples}
            </p>
          </div>
        ) : (
          <p className="text-sm text-slate-500">
            No held-out test metrics recorded for this model yet.
          </p>
        )}

        <div className="flex items-center justify-between gap-4 border-t border-slate-100 pt-4">
          <div className="text-sm">
            <dt className="text-xs uppercase tracking-wide text-slate-400">Git commit</dt>
            <dd className="mt-1 font-mono text-xs text-slate-600">
              {entry.git_commit ? entry.git_commit.slice(0, 10) : "—"}
            </dd>
          </div>
          {entry.is_active ? (
            <Button variant="secondary" size="sm" disabled>
              Active
            </Button>
          ) : (
            <Button
              variant="primary"
              size="sm"
              loading={isActivating}
              onClick={() => onActivate(entry.name)}
            >
              Set active
            </Button>
          )}
        </div>
      </CardBody>
    </Card>
  );
}

export function ModelsPage() {
  const { data, isLoading, isError, error, refetch } = useModelCatalog();
  const activateModel = useActivateModel();

  function handleActivate(name: string) {
    if (
      !confirm(
        `Set "${name}" as the active model? It will become the default used for new predictions.`,
      )
    ) {
      return;
    }
    activateModel.mutate(name);
  }

  return (
    <div>
      <PageHeader
        title="Models"
        description="Models available for predictions. Pick one to set it as the active default."
      />

      {activateModel.isError && (
        <div
          role="alert"
          className="mb-6 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700"
        >
          {toErrorMessage(activateModel.error)}
        </div>
      )}

      {isLoading ? (
        <LoadingState label="Loading models…" />
      ) : isError || !data ? (
        <ErrorState error={error} onRetry={() => refetch()} />
      ) : data.models.length === 0 ? (
        <EmptyState
          title="No models found"
          description={`No models were found under ${data.catalog_dir}.`}
        />
      ) : (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          {data.models.map((entry) => (
            <ModelCard
              key={entry.name}
              entry={entry}
              onActivate={handleActivate}
              isActivating={activateModel.isPending && activateModel.variables === entry.name}
            />
          ))}
        </div>
      )}
    </div>
  );
}
