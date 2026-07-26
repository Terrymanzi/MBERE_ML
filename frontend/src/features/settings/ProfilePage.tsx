import { useState } from "react";
import type { FormEvent } from "react";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Input } from "@/components/ui/Input";
import { LegalNav } from "@/features/legal/components/LegalNav";
import { useAuth } from "@/features/auth/AuthContext";
import { formatDateTime } from "@/lib/format";
import { ApiError, changePassword } from "@/services";
import { toErrorMessage } from "@/components/feedback/states";

const ROLE_LABEL: Record<string, string> = {
  ADMIN: "Administrator",
  INSURER: "Insurer",
  FLEET_MANAGER: "Fleet Manager",
};

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-xs font-medium uppercase tracking-wide text-slate-400">
        {label}
      </dt>
      <dd className="mt-1 text-sm text-slate-900">{value}</dd>
    </div>
  );
}

export function ProfilePage() {
  const { user, logout } = useAuth();

  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [pwError, setPwError] = useState<string | null>(null);
  const [pwSuccess, setPwSuccess] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  async function onChangePassword(e: FormEvent) {
    e.preventDefault();
    setPwError(null);
    setPwSuccess(false);
    setSubmitting(true);
    try {
      await changePassword({ current_password: currentPassword, new_password: newPassword });
      setPwSuccess(true);
      setCurrentPassword("");
      setNewPassword("");
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        setPwError("Current password is incorrect.");
      } else {
        setPwError(toErrorMessage(err));
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div>
      <PageHeader title="Profile" description="Your full account details." />

      <Card className="max-w-2xl">
        <CardHeader
          title={user?.full_name || "Fleet operator"}
          description={user?.email}
          action={
            user?.is_active ? (
              <Badge tone="green">Active</Badge>
            ) : (
              <Badge tone="amber">Inactive</Badge>
            )
          }
        />
        <CardBody>
          <dl className="grid grid-cols-2 gap-6">
            <Field label="User ID" value={user ? `#${user.id}` : "—"} />
            <Field label="Email" value={user?.email ?? "—"} />
            <Field label="Full name" value={user?.full_name ?? "—"} />
            <Field label="Role" value={user ? ROLE_LABEL[user.role] ?? user.role : "—"} />
            <Field
              label="Member since"
              value={user ? formatDateTime(user.created_at) : "—"}
            />
          </dl>

          <div className="mt-8 border-t border-slate-100 pt-6">
            <Button variant="secondary" onClick={logout}>
              Log out
            </Button>
          </div>
        </CardBody>
      </Card>

      <Card className="mt-6 max-w-2xl">
        <CardHeader title="Change password" />
        <CardBody>
          <form onSubmit={onChangePassword} className="max-w-sm space-y-4" noValidate>
            <Input
              label="Current password"
              type="password"
              autoComplete="current-password"
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              required
            />
            <Input
              label="New password"
              type="password"
              autoComplete="new-password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              required
              minLength={8}
              hint="At least 8 characters."
            />
            {pwError && (
              <div role="alert" className="bg-red-50 px-4 py-3 text-sm text-red-600">
                {pwError}
              </div>
            )}
            {pwSuccess && (
              <div className="bg-green-50 px-4 py-3 text-sm text-green-700">
                Password updated.
              </div>
            )}
            <Button type="submit" loading={submitting}>
              Update password
            </Button>
          </form>
        </CardBody>
      </Card>

      <Card className="mt-6 max-w-2xl">
        <CardHeader
          title="Legal"
          description="Terms, privacy, and disclaimer documentation for MBERE ML."
        />
        <CardBody>
          <LegalNav variant="stacked" />
        </CardBody>
      </Card>
    </div>
  );
}
