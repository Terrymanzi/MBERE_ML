import { useState } from "react";
import type { FormEvent } from "react";
import { Modal } from "@/components/ui/Modal";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { Button } from "@/components/ui/Button";
import { ApiError, type UserRole } from "@/services";
import { toErrorMessage } from "@/components/feedback/states";
import { useCreateUser } from "../useUsers";

export function CreateUserModal({
  open,
  onClose,
}: {
  open: boolean;
  onClose: () => void;
}) {
  const createUser = useCreateUser();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [role, setRole] = useState<UserRole>("FLEET_MANAGER");
  const [error, setError] = useState<string | null>(null);

  function reset() {
    setEmail("");
    setPassword("");
    setFullName("");
    setRole("FLEET_MANAGER");
    setError(null);
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      await createUser.mutateAsync({
        email: email.trim(),
        password,
        full_name: fullName.trim() || null,
        role,
      });
      reset();
      onClose();
    } catch (err) {
      if (err instanceof ApiError && err.status === 409) {
        setError("A user with that email already exists.");
      } else {
        setError(toErrorMessage(err));
      }
    }
  }

  return (
    <Modal
      open={open}
      onClose={onClose}
      title="Add user"
      description="Create an account for a team member and assign their role."
    >
      <form onSubmit={onSubmit} className="space-y-4">
        <Input
          label="Email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="you@example.com"
          required
        />
        <Input
          label="Full name"
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
          placeholder="Optional"
        />
        <Input
          label="Password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          minLength={8}
          hint="At least 8 characters."
          required
        />
        <Select
          label="Role"
          value={role}
          onChange={(e) => setRole(e.target.value as UserRole)}
        >
          <option value="FLEET_MANAGER">Fleet Manager</option>
          <option value="INSURER">Insurer</option>
          <option value="ADMIN">Administrator</option>
        </Select>

        {error && (
          <div role="alert" className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        )}

        <div className="flex justify-end gap-3 pt-2">
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" loading={createUser.isPending}>
            Add user
          </Button>
        </div>
      </form>
    </Modal>
  );
}
