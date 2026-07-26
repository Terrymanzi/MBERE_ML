import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { Modal } from "@/components/ui/Modal";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { ApiError, type UserRead } from "@/services";
import { toErrorMessage } from "@/components/feedback/states";
import { useUpdateUser } from "../useUsers";

export function EditUserModal({
  open,
  onClose,
  user,
}: {
  open: boolean;
  onClose: () => void;
  user: UserRead;
}) {
  const updateUser = useUpdateUser();
  const [email, setEmail] = useState(user.email);
  const [fullName, setFullName] = useState(user.full_name ?? "");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (open) {
      setEmail(user.email);
      setFullName(user.full_name ?? "");
      setError(null);
    }
  }, [open, user]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      await updateUser.mutateAsync({
        id: user.id,
        payload: { email: email.trim(), full_name: fullName.trim() || null },
      });
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
    <Modal open={open} onClose={onClose} title="Edit user">
      <form onSubmit={onSubmit} className="space-y-4">
        <Input
          label="Email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <Input
          label="Full name"
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
          placeholder="Optional"
        />

        {error && (
          <div role="alert" className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        )}

        <div className="flex justify-end gap-3 pt-2">
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" loading={updateUser.isPending}>
            Save changes
          </Button>
        </div>
      </form>
    </Modal>
  );
}
