import { useState } from "react";
import type { FormEvent } from "react";
import { Modal } from "@/components/ui/Modal";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { ApiError } from "@/services";
import { toErrorMessage } from "@/components/feedback/states";
import { useCreateDriver } from "../useDrivers";

export function CreateDriverModal({
  open,
  onClose,
  onCreated,
}: {
  open: boolean;
  onClose: () => void;
  onCreated?: (driverId: number) => void;
}) {
  const createDriver = useCreateDriver();
  const [licenseNumber, setLicenseNumber] = useState("");
  const [fullName, setFullName] = useState("");
  const [dob, setDob] = useState("");
  const [notes, setNotes] = useState("");
  const [error, setError] = useState<string | null>(null);

  function reset() {
    setLicenseNumber("");
    setFullName("");
    setDob("");
    setNotes("");
    setError(null);
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      const driver = await createDriver.mutateAsync({
        license_number: licenseNumber.trim(),
        full_name: fullName.trim(),
        date_of_birth: dob || null,
        notes: notes.trim() || null,
      });
      reset();
      onClose();
      onCreated?.(driver.id);
    } catch (err) {
      if (err instanceof ApiError && err.status === 409) {
        setError("A driver with that license number already exists.");
      } else {
        setError(toErrorMessage(err));
      }
    }
  }

  return (
    <Modal
      open={open}
      onClose={onClose}
      title="Add driver"
      description="Register a driver to run and store risk assessments."
    >
      <form onSubmit={onSubmit} className="space-y-4">
        <Input
          label="License number"
          value={licenseNumber}
          onChange={(e) => setLicenseNumber(e.target.value)}
          placeholder="RW-DRV-0006"
          required
        />
        <Input
          label="Full name"
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
          placeholder="Driver name"
          required
        />
        <Input
          label="Date of birth"
          type="date"
          value={dob}
          onChange={(e) => setDob(e.target.value)}
        />
        <Input
          label="Notes"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
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
          <Button type="submit" loading={createDriver.isPending}>
            Add driver
          </Button>
        </div>
      </form>
    </Modal>
  );
}
