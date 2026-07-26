import { useEffect, useState } from "react";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { Badge } from "@/components/ui/Badge";
import { PlusIcon, SearchIcon } from "@/components/icons";
import {
  EmptyState,
  ErrorState,
  LoadingState,
  toErrorMessage,
} from "@/components/feedback/states";
import { formatDateTime } from "@/lib/format";
import type { UserRead, UserRole } from "@/services";
import { useAuth } from "@/features/auth/AuthContext";
import {
  useDeleteUser,
  useUpdateUserActive,
  useUpdateUserRole,
  useUsers,
} from "./useUsers";
import { CreateUserModal } from "./components/CreateUserModal";
import { EditUserModal } from "./components/EditUserModal";
import { ResetPasswordModal } from "./components/ResetPasswordModal";

const ROLE_LABEL: Record<UserRole, string> = {
  ADMIN: "Administrator",
  INSURER: "Insurer",
  FLEET_MANAGER: "Fleet Manager",
};

export function UsersPage() {
  const { user: me } = useAuth();
  const [query, setQuery] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");
  const [createOpen, setCreateOpen] = useState(false);
  const [editTarget, setEditTarget] = useState<UserRead | null>(null);
  const [resetTarget, setResetTarget] = useState<UserRead | null>(null);
  const [rowError, setRowError] = useState<string | null>(null);

  useEffect(() => {
    const id = setTimeout(() => setDebouncedQuery(query.trim()), 300);
    return () => clearTimeout(id);
  }, [query]);

  const { data, isLoading, isError, error, refetch } = useUsers(debouncedQuery);
  const users = data ?? [];

  const updateRole = useUpdateUserRole();
  const updateActive = useUpdateUserActive();
  const deleteUser = useDeleteUser();

  function handleRoleChange(user: UserRead, role: UserRole) {
    setRowError(null);
    updateRole.mutate(
      { id: user.id, role },
      { onError: (err) => setRowError(toErrorMessage(err)) },
    );
  }

  function handleActiveToggle(user: UserRead) {
    setRowError(null);
    updateActive.mutate(
      { id: user.id, isActive: !user.is_active },
      { onError: (err) => setRowError(toErrorMessage(err)) },
    );
  }

  function handleDelete(user: UserRead) {
    if (!confirm(`Delete user "${user.email}"? This cannot be undone.`)) return;
    setRowError(null);
    deleteUser.mutate(user.id, { onError: (err) => setRowError(toErrorMessage(err)) });
  }

  return (
    <div>
      <PageHeader
        title="Users"
        description="Manage team accounts, roles, and access."
        actions={
          <Button onClick={() => setCreateOpen(true)}>
            <PlusIcon className="h-4 w-4" />
            Add user
          </Button>
        }
      />

      {rowError && (
        <div role="alert" className="mb-6 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">
          {rowError}
        </div>
      )}

      <Card>
        <div className="border-b border-slate-100 p-4">
          <div className="relative max-w-sm">
            <SearchIcon className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <Input
              className="pl-9"
              placeholder="Search by email or name…"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              aria-label="Search users"
            />
          </div>
        </div>

        {isLoading ? (
          <LoadingState label="Loading users…" />
        ) : isError ? (
          <ErrorState error={error} onRetry={() => refetch()} className="m-4" />
        ) : users.length === 0 ? (
          <EmptyState
            className="m-4"
            title={query ? "No users match your search" : "No users yet"}
            description={
              query ? "Try a different name or email." : "Add your first team member."
            }
          />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-slate-100 text-xs uppercase tracking-wide text-slate-400">
                  <th className="px-6 py-3 font-medium">User</th>
                  <th className="px-6 py-3 font-medium">Role</th>
                  <th className="px-6 py-3 font-medium">Status</th>
                  <th className="px-6 py-3 font-medium">Added</th>
                  <th className="px-6 py-3 font-medium" />
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {users.map((u) => {
                  const isSelf = u.id === me?.id;
                  return (
                    <tr key={u.id}>
                      <td className="px-6 py-4">
                        <p className="font-medium text-slate-900">{u.full_name || "—"}</p>
                        <p className="font-mono text-xs text-slate-500">{u.email}</p>
                      </td>
                      <td className="px-6 py-4">
                        <Select
                          aria-label={`Role for ${u.email}`}
                          value={u.role}
                          disabled={isSelf}
                          onChange={(e) => handleRoleChange(u, e.target.value as UserRole)}
                          className="w-40"
                        >
                          {Object.entries(ROLE_LABEL).map(([value, label]) => (
                            <option key={value} value={value}>
                              {label}
                            </option>
                          ))}
                        </Select>
                      </td>
                      <td className="px-6 py-4">
                        <button
                          type="button"
                          disabled={isSelf}
                          onClick={() => handleActiveToggle(u)}
                          className="disabled:cursor-not-allowed disabled:opacity-60"
                        >
                          {u.is_active ? (
                            <Badge tone="green">Active</Badge>
                          ) : (
                            <Badge tone="amber">Inactive</Badge>
                          )}
                        </button>
                      </td>
                      <td className="px-6 py-4 text-slate-600">
                        {formatDateTime(u.created_at)}
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center justify-end gap-3">
                          <button
                            className="font-medium text-slate-500 hover:text-slate-900"
                            onClick={() => setEditTarget(u)}
                          >
                            Edit
                          </button>
                          <button
                            className="font-medium text-slate-500 hover:text-slate-900"
                            onClick={() => setResetTarget(u)}
                          >
                            Reset password
                          </button>
                          <button
                            disabled={isSelf}
                            className="font-medium text-red-600 hover:text-red-800 disabled:cursor-not-allowed disabled:opacity-60"
                            onClick={() => handleDelete(u)}
                          >
                            Delete
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      <CreateUserModal open={createOpen} onClose={() => setCreateOpen(false)} />

      {editTarget && (
        <EditUserModal
          open={editTarget !== null}
          onClose={() => setEditTarget(null)}
          user={editTarget}
        />
      )}

      {resetTarget && (
        <ResetPasswordModal
          open={resetTarget !== null}
          onClose={() => setResetTarget(null)}
          user={resetTarget}
        />
      )}
    </div>
  );
}
