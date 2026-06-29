import { PageHeader } from "@/components/layout/PageHeader";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import {
  EmptyState,
  ErrorState,
  LoadingState,
} from "@/components/feedback/states";
import { formatDateTime } from "@/lib/format";
import type { ModelVersionRead } from "@/services";
import { useModels } from "./useModels";
import { MetricsGrid } from "./components/MetricsGrid";

function ModelCard({ model }: { model: ModelVersionRead }) {
  return (
    <Card>
      <CardHeader
        title={
          <span className="flex items-center gap-2">
            {model.name}
            <span className="text-sm font-normal text-slate-400">v{model.version}</span>
            {model.is_active && <Badge tone="green">Active</Badge>}
          </span>
        }
        description={`${model.dataset_name} · ${model.kind}`}
      />
      <CardBody className="space-y-5">
        <div className="flex flex-wrap gap-2">
          {model.target_classes.map((c) => (
            <Badge key={c} tone="brand">
              {c}
            </Badge>
          ))}
        </div>

        <MetricsGrid metrics={model.metrics} />

        <dl className="grid grid-cols-2 gap-4 border-t border-slate-100 pt-4 text-sm">
          <div>
            <dt className="text-xs uppercase tracking-wide text-slate-400">Git commit</dt>
            <dd className="mt-1 font-mono text-xs text-slate-600">
              {model.git_commit ? model.git_commit.slice(0, 10) : "—"}
            </dd>
          </div>
          <div>
            <dt className="text-xs uppercase tracking-wide text-slate-400">Registered</dt>
            <dd className="mt-1 text-slate-600">{formatDateTime(model.created_at)}</dd>
          </div>
        </dl>
      </CardBody>
    </Card>
  );
}

export function ModelsPage() {
  const { data, isLoading, isError, error, refetch } = useModels();

  return (
    <div>
      <PageHeader
        title="Models"
        description="Registered model versions. Every prediction is traceable to one of these."
      />

      {isLoading ? (
        <LoadingState label="Loading models…" />
      ) : isError || !data ? (
        <ErrorState error={error} onRetry={() => refetch()} />
      ) : data.length === 0 ? (
        <EmptyState
          title="No models registered"
          description="The backend registers a model version on startup when an artifact is loaded."
        />
      ) : (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          {data.map((m) => (
            <ModelCard key={m.id} model={m} />
          ))}
        </div>
      )}
    </div>
  );
}
