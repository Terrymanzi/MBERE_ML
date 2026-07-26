import { useState } from "react";
import type { FormEvent } from "react";
import { Modal } from "@/components/ui/Modal";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { type UserRead } from "@/services";
import { toErrorMessage } from "@/components/feedback/states";
import { useResetUserPassword } from "../useUsers";

export function ResetPasswordModal({
  open,
  onClose,
  user,
}: {
  open: boolean;
  onClose: () => void;
  user: UserRead;
}) {
  const resetPassword = useResetUserPassword();
  const [newPassword, setNewPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      await resetPassword.mutateAsync({ id: user.id, payload: { new_password: newPassword } });
      setSuccess(true);
      setNewPassword("");
    } catch (err) {
      setError(toErrorMessage(err));
    }
  }

  function handleClose() {
    setSuccess(false);
    setNewPassword("");
    setError(null);
    onClose();
  }

  return (
    <Modal
      open={open}
      onClose={handleClose}
      title="Reset password"
      description={`Set a new password for ${user.email}.`}
    >
      {success ? (
        <div className="space-y-4">
          <div className="bg-green-50 px-4 py-3 text-sm text-green-700">
            Password updated. Share the new password with {user.email} securely.
          </div>
          <div className="flex justify-end">
            <Button type="button" onClick={handleClose}>
              Done
            </Button>
          </div>
        </div>
      ) : (
        <form onSubmit={onSubmit} className="space-y-4">
          <Input
            label="New password"
            type="password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            minLength={8}
            hint="At least 8 characters."
            required
          />

          {error && (
            <div role="alert" className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">
              {error}
            </div>
          )}

          <div className="flex justify-end gap-3 pt-2">
            <Button type="button" variant="secondary" onClick={handleClose}>
              Cancel
            </Button>
            <Button type="submit" loading={resetPassword.isPending}>
              Reset password
            </Button>
          </div>
        </form>
      )}
    </Modal>
  );
}
