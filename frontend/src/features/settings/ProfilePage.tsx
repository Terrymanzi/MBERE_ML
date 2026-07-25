import { PageHeader } from "@/components/layout/PageHeader";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { LegalNav } from "@/features/legal/components/LegalNav";
import { useAuth } from "@/features/auth/AuthContext";
import { formatDateTime } from "@/lib/format";

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
