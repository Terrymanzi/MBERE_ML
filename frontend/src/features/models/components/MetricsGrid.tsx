import { EmptyState } from "@/components/feedback/states";

const PREFERRED_ORDER = [
  "accuracy",
  "balanced_accuracy",
  "precision",
  "precision_macro",
  "recall",
  "recall_macro",
  "f1",
  "f1_macro",
  "roc_auc",
  "roc_auc_ovr_macro",
  "pr_auc",
  "log_loss",
];

function prettyLabel(key: string): string {
  const overrides: Record<string, string> = {
    roc_auc: "ROC AUC",
    roc_auc_ovr_macro: "ROC AUC (macro)",
    pr_auc: "PR AUC",
    f1: "F1",
    f1_macro: "F1 (macro)",
    precision_macro: "Precision (macro)",
    recall_macro: "Recall (macro)",
    log_loss: "Log loss",
  };
  if (overrides[key]) return overrides[key];
  return key
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

function formatMetric(value: number | string | null): string {
  if (value == null) return "—";
  if (typeof value === "string") return value;
  if (!Number.isFinite(value)) return "—";
  // Scores in [0,1] read better as percentages; leave larger numbers as-is.
  if (value >= 0 && value <= 1) return `${(value * 100).toFixed(1)}%`;
  return value.toFixed(3);
}

export function MetricsGrid({
  metrics,
}: {
  metrics: Record<string, number | string | null>;
}) {
  const keys = Object.keys(metrics);
  if (keys.length === 0) {
    return (
      <EmptyState
        title="No metrics recorded"
        description="This model version has no stored evaluation metrics."
      />
    );
  }

  const ordered = [
    ...PREFERRED_ORDER.filter((k) => k in metrics),
    ...keys.filter((k) => !PREFERRED_ORDER.includes(k)),
  ];

  return (
    <dl className="grid grid-cols-2 gap-x-6 gap-y-4 sm:grid-cols-3">
      {ordered.map((key) => (
        <div key={key}>
          <dt className="text-xs font-medium uppercase tracking-wide text-slate-400">
            {prettyLabel(key)}
          </dt>
          <dd className="mt-1 text-xl font-semibold tabular-nums text-slate-900">
            {formatMetric(metrics[key])}
          </dd>
        </div>
      ))}
    </dl>
  );
}
