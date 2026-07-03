import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { RiskBadge } from "@/components/ui/RiskBadge";
import { ChevronLeftIcon, PredictIcon } from "@/components/icons";
import {
  EmptyState,
  ErrorState,
  LoadingState,
} from "@/components/feedback/states";
import { formatDate, formatDateTime, formatPercent } from "@/lib/format";
import type { RiskAssessmentRead } from "@/services";
import { useDeleteDriver, useDriverRiskHistory, useDrivers } from "./useDrivers";
import { EditDriverModal } from "./components/EditDriverModal";

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-xs font-thin uppercase tracking-wide text-slate-400">
        {label}
      </dt>
      <dd className="mt-1 text-sm text-slate-900">{value}</dd>
    </div>
  );
}

function AssessmentRow({ assessment }: { assessment: RiskAssessmentRead }) {
  const p = assessment.prediction;
  return (
    <div className="flex flex-col gap-3 py-4 sm:flex-row sm:items-center sm:justify-between">
      <div className="flex items-center gap-4">
        {p ? (
          <RiskBadge band={p.risk_band} />
        ) : (
          <span className="text-sm text-slate-400">—</span>
        )}
        <div>
          <p className="text-sm font-mono text-slate-900">
            {p ? p.predicted_class : assessment.status}
          </p>
          <p className="text-xs text-slate-500">
            {formatDateTime(assessment.created_at)}
          </p>
        </div>
      </div>

      {p && (
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-sm text-slate-500">
            Risk score{" "}
            <span className="font-thin text-slate-900">
              {formatPercent(p.risk_score)}
            </span>
          </span>
          {p.explanation?.top_features?.slice(0, 3).map((f) => (
            <span
              key={f.feature}
              className="bg-slate-200 px-2 py-0.5 text-xs text-slate-600"
              title={`contribution ${f.contribution.toFixed(4)}`}
            >
              {f.feature}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

export function DriverDetailsPage() {
  const { driverId } = useParams();
  const id = Number(driverId);
  const navigate = useNavigate();
  const [editOpen, setEditOpen] = useState(false);

  const driversQuery = useDrivers();
  const driver = driversQuery.data?.find((d) => d.id === id);
  const historyQuery = useDriverRiskHistory(
    Number.isFinite(id) ? id : undefined,
  );
  const deleteDriver = useDeleteDriver();

  function handleDelete() {
    if (!driver) return;
    if (!confirm(`Delete driver "${driver.full_name}"? This cannot be undone.`)) return;
    deleteDriver.mutate(driver.id, {
      onSuccess: () => navigate("/app/drivers"),
    });
  }

  return (
    <div>
      <Link
        to="/app/drivers"
        className="mb-6 inline-flex items-center gap-1 text-sm font-thin text-slate-500 hover:text-slate-900"
      >
        <ChevronLeftIcon className="h-4 w-4" />
        Back to drivers
      </Link>

      {driversQuery.isLoading ? (
        <LoadingState label="Loading driver…" />
      ) : driversQuery.isError ? (
        <ErrorState
          error={driversQuery.error}
          onRetry={() => driversQuery.refetch()}
        />
      ) : !driver ? (
        <EmptyState
          title="Driver not found"
          description="This driver may have been removed."
          action={
            <Button
              variant="secondary"
              onClick={() => navigate("/app/drivers")}
            >
              Back to drivers
            </Button>
          }
        />
      ) : (
        <>
          <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <h1 className="text-3xl font-mono tracking-tight text-slate-900">
                {driver.full_name}
              </h1>
              <p className="mt-1 font-thin text-sm text-slate-500">
                {driver.license_number}
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="secondary"
                onClick={() => setEditOpen(true)}
              >
                Edit
              </Button>
              <Button
                variant="danger"
                loading={deleteDriver.isPending}
                onClick={handleDelete}
              >
                Delete
              </Button>
              <Button
                onClick={() => navigate(`/app/predict?driver_id=${driver.id}`)}
              >
                <PredictIcon className="h-4 w-4" />
                Run prediction
              </Button>
            </div>
          </div>

          <div className="grid gap-6 lg:grid-cols-3">
            <Card className="lg:col-span-1">
              <CardHeader title="Details" />
              <CardBody>
                <dl className="grid grid-cols-2 gap-5">
                  <InfoRow
                    label="Date of birth"
                    value={formatDate(driver.date_of_birth)}
                  />
                  <InfoRow
                    label="Added"
                    value={formatDate(driver.created_at)}
                  />
                  <div className="col-span-2">
                    <InfoRow label="Notes" value={driver.notes || "—"} />
                  </div>
                </dl>
              </CardBody>
            </Card>

            <Card className="lg:col-span-2">
              <CardHeader
                title="Risk history"
                description="Past assessments for this driver, sorted by most recent."
              />
              <CardBody className="pt-0">
                {historyQuery.isLoading ? (
                  <LoadingState label="Loading history…" />
                ) : historyQuery.isError ? (
                  <ErrorState
                    error={historyQuery.error}
                    onRetry={() => historyQuery.refetch()}
                  />
                ) : !historyQuery.data || historyQuery.data.length === 0 ? (
                  <EmptyState
                    title="No assessments yet"
                    description="Run a prediction to create the first risk assessment."
                    action={
                      <Button
                        size="sm"
                        onClick={() =>
                          navigate(`/app/predict?driver_id=${driver.id}`)
                        }
                      >
                        Run prediction
                      </Button>
                    }
                  />
                ) : (
                  <div className="divide-y divide-slate-100">
                    {historyQuery.data.map((a) => (
                      <AssessmentRow key={a.id} assessment={a} />
                    ))}
                  </div>
                )}
              </CardBody>
            </Card>
          </div>

          {editOpen && (
            <EditDriverModal
              open={editOpen}
              onClose={() => setEditOpen(false)}
              driver={driver}
            />
          )}
        </>
      )}
    </div>
  );
}
