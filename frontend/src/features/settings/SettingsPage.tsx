import { PageHeader } from "@/components/layout/PageHeader";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { API_BASE_URL } from "@/services";
import { useHealth } from "@/features/system/useHealth";
import { activeModel, useModels } from "@/features/models/useModels";

function Row({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between gap-4 py-3">
      <span className="text-sm text-slate-500">{label}</span>
      <span className="text-sm font-medium text-slate-900">{children}</span>
    </div>
  );
}

export function SettingsPage() {
  const health = useHealth();
  const models = useModels();
  const active = activeModel(models.data);

  const statusBadge = () => {
    if (health.isLoading) return <Badge tone="neutral">Checking…</Badge>;
    if (health.isError || !health.data) return <Badge tone="red">Offline</Badge>;
    if (health.data.status === "ok") return <Badge tone="green">Healthy</Badge>;
    return <Badge tone="amber">Degraded</Badge>;
  };

  return (
    <div>
      <PageHeader
        title="Settings"
        description="Connection status and the active model configuration. Model and risk thresholds are configured on the backend."
      />

      <div className="grid max-w-3xl grid-cols-1 gap-6">
        <Card>
          <CardHeader title="Backend connection" />
          <CardBody className="divide-y divide-slate-100 py-0">
            <Row label="API base URL">
              <span className="font-mono text-xs">{API_BASE_URL}</span>
            </Row>
            <Row label="Status">{statusBadge()}</Row>
            <Row label="Database">
              {health.data?.db_ok ? (
                <Badge tone="green">Connected</Badge>
              ) : (
                <Badge tone="red">Unavailable</Badge>
              )}
            </Row>
            <Row label="Model loaded">
              {health.data?.model_loaded ? (
                <Badge tone="green">Yes</Badge>
              ) : (
                <Badge tone="amber">No</Badge>
              )}
            </Row>
          </CardBody>
        </Card>

        <Card>
          <CardHeader title="Active model" />
          <CardBody className="divide-y divide-slate-100 py-0">
            <Row label="Name">{active ? active.name : "—"}</Row>
            <Row label="Version">{active ? `v${active.version}` : "—"}</Row>
            <Row label="Dataset">{active ? active.dataset_name : "—"}</Row>
            <Row label="Task">{active ? active.kind : "—"}</Row>
            <Row label="Inputs">
              {health.data?.n_input_features != null
                ? `${health.data.n_input_features} features`
                : "—"}
            </Row>
          </CardBody>
        </Card>

        <Card>
          <CardHeader
            title="Risk bands"
            description="Score thresholds used to map a risk score to a band (configured server-side)."
          />
          <CardBody className="divide-y divide-slate-100 py-0">
            <Row label="Low">
              <Badge tone="green">&lt; 34%</Badge>
            </Row>
            <Row label="Medium">
              <Badge tone="amber">34% – 67%</Badge>
            </Row>
            <Row label="High">
              <Badge tone="red">&ge; 67%</Badge>
            </Row>
          </CardBody>
        </Card>
      </div>
    </div>
  );
}
