import { Link } from "react-router-dom";
import { Badge } from "@/components/ui/Badge";
import { EmptyState, ErrorState, LoadingState } from "@/components/feedback/states";
import type { ModelCatalogEntry } from "@/services";
import { useModelCatalog } from "@/features/models/useModels";

function GateBadge({ entry }: { entry: ModelCatalogEntry }) {
  if (entry.gate_passed === null) return <Badge>—</Badge>;
  return entry.gate_passed ? (
    <Badge tone="green">Passes gate</Badge>
  ) : (
    <Badge tone="red">Fails gate</Badge>
  );
}

export function ModelRegistrySummary() {
  const { data, isLoading, isError, error, refetch } = useModelCatalog();

  if (isLoading) return <LoadingState label="Loading models…" />;
  if (isError || !data) return <ErrorState error={error} onRetry={() => refetch()} />;
  if (data.models.length === 0) {
    return (
      <EmptyState
        title="No models found"
        description={`No models were found under ${data.catalog_dir}.`}
      />
    );
  }

  return (
    <div className="divide-y divide-slate-100">
      {data.models.map((entry) => (
        <Link
          key={entry.name}
          to="/app/models"
          className="flex items-center justify-between gap-4 py-3 hover:bg-slate-50"
        >
          <div>
            <p className="font-mono text-sm text-slate-900">
              {entry.name} <span className="text-slate-400">v{entry.version}</span>
            </p>
            <p className="text-xs text-slate-500">{entry.dataset_name}</p>
          </div>
          <div className="flex items-center gap-2">
            {entry.is_active && <Badge tone="brand">Active</Badge>}
            <GateBadge entry={entry} />
          </div>
        </Link>
      ))}
    </div>
  );
}
