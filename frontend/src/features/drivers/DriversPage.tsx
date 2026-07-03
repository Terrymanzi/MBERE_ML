import { useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { PlusIcon, SearchIcon } from "@/components/icons";
import {
  EmptyState,
  ErrorState,
  LoadingState,
} from "@/components/feedback/states";
import { formatDate } from "@/lib/format";
import type { DriverRead } from "@/services";
import { useDeleteDriver, useDrivers } from "./useDrivers";
import { CreateDriverModal } from "./components/CreateDriverModal";
import { EditDriverModal } from "./components/EditDriverModal";

export function DriversPage() {
  const { data, isLoading, isError, error, refetch } = useDrivers();
  const deleteDriver = useDeleteDriver();
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const [createOpen, setCreateOpen] = useState(false);
  const [editTarget, setEditTarget] = useState<DriverRead | null>(null);

  const filtered = useMemo(() => {
    if (!data) return [];
    const q = query.trim().toLowerCase();
    if (!q) return data;
    return data.filter(
      (d) =>
        d.full_name.toLowerCase().includes(q) ||
        d.license_number.toLowerCase().includes(q),
    );
  }, [data, query]);

  function handleDelete(e: React.MouseEvent, driver: DriverRead) {
    e.stopPropagation();
    if (!confirm(`Delete driver "${driver.full_name}"? This cannot be undone.`)) return;
    deleteDriver.mutate(driver.id);
  }

  return (
    <div>
      <PageHeader
        title="Drivers"
        description="Registered drivers in your fleet. Select one to view risk history."
        actions={
          <Button onClick={() => setCreateOpen(true)}>
            <PlusIcon className="h-4 w-4" />
            Add driver
          </Button>
        }
      />

      <Card>
        <div className="border-b border-slate-100 p-4">
          <div className="relative max-w-sm">
            <SearchIcon className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <Input
              className="pl-9"
              placeholder="Search by name or license…"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              aria-label="Search drivers"
            />
          </div>
        </div>

        {isLoading ? (
          <LoadingState label="Loading drivers…" />
        ) : isError ? (
          <ErrorState error={error} onRetry={() => refetch()} className="m-4" />
        ) : filtered.length === 0 ? (
          <EmptyState
            className="m-4"
            title={query ? "No drivers match your search" : "No drivers yet"}
            description={
              query
                ? "Try a different name or license number."
                : "Add your first driver to start running risk assessments."
            }
            action={
              !query ? (
                <Button onClick={() => setCreateOpen(true)} size="sm">
                  <PlusIcon className="h-4 w-4" />
                  Add driver
                </Button>
              ) : undefined
            }
          />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-slate-100 text-xs uppercase tracking-wide text-slate-400">
                  <th className="px-6 py-3 font-medium">Driver</th>
                  <th className="px-6 py-3 font-medium">License</th>
                  <th className="px-6 py-3 font-medium">Date of birth</th>
                  <th className="px-6 py-3 font-medium">Added</th>
                  <th className="px-6 py-3 font-medium" />
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filtered.map((d) => (
                  <tr
                    key={d.id}
                    className="cursor-pointer transition-colors hover:bg-slate-50"
                    onClick={() => navigate(`/app/drivers/${d.id}`)}
                  >
                    <td className="px-6 py-4 font-medium text-slate-900">
                      {d.full_name}
                    </td>
                    <td className="px-6 py-4 font-mono text-xs text-slate-600">
                      {d.license_number}
                    </td>
                    <td className="px-6 py-4 text-slate-600">
                      {formatDate(d.date_of_birth)}
                    </td>
                    <td className="px-6 py-4 text-slate-600">
                      {formatDate(d.created_at)}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center justify-end gap-2">
                        <Link
                          to={`/app/drivers/${d.id}`}
                          className="font-medium text-brand-700 hover:underline"
                          onClick={(e) => e.stopPropagation()}
                        >
                          View
                        </Link>
                        <button
                          className="font-medium text-slate-500 hover:text-slate-900"
                          onClick={(e) => { e.stopPropagation(); setEditTarget(d); }}
                        >
                          Edit
                        </button>
                        <button
                          className="font-medium text-red-600 hover:text-red-800"
                          onClick={(e) => handleDelete(e, d)}
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      <CreateDriverModal
        open={createOpen}
        onClose={() => setCreateOpen(false)}
        onCreated={(id) => navigate(`/app/drivers/${id}`)}
      />

      {editTarget && (
        <EditDriverModal
          open={editTarget !== null}
          onClose={() => setEditTarget(null)}
          driver={editTarget}
        />
      )}
    </div>
  );
}
