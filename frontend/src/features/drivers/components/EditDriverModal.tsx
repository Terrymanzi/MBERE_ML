import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { Modal } from "@/components/ui/Modal";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { ApiError, type DriverRead } from "@/services";
import { toErrorMessage } from "@/components/feedback/states";
import { useUpdateDriver } from "../useDrivers";

export function EditDriverModal({
  open,
  onClose,
  driver,
}: {
  open: boolean;
  onClose: () => void;
  driver: DriverRead;
}) {
  const updateDriver = useUpdateDriver();
  const [licenseNumber, setLicenseNumber] = useState(driver.license_number);
  const [fullName, setFullName] = useState(driver.full_name);
  const [dob, setDob] = useState(driver.date_of_birth ?? "");
  const [notes, setNotes] = useState(driver.notes ?? "");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (open) {
      setLicenseNumber(driver.license_number);
      setFullName(driver.full_name);
      setDob(driver.date_of_birth ?? "");
      setNotes(driver.notes ?? "");
      setError(null);
    }
  }, [open, driver]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      await updateDriver.mutateAsync({
        id: driver.id,
        payload: {
          license_number: licenseNumber.trim(),
          full_name: fullName.trim(),
          date_of_birth: dob || null,
          notes: notes.trim() || null,
        },
      });
      onClose();
    } catch (err) {
      if (err instanceof ApiError && err.status === 409) {
        setError("A driver with that license number already exists.");
      } else {
        setError(toErrorMessage(err));
      }
    }
  }

  return (
    <Modal open={open} onClose={onClose} title="Edit driver">
      <form onSubmit={onSubmit} className="space-y-4">
        <Input
          label="License number"
          value={licenseNumber}
          onChange={(e) => setLicenseNumber(e.target.value)}
          required
        />
        <Input
          label="Full name"
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
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
          <Button type="submit" loading={updateDriver.isPending}>
            Save changes
          </Button>
        </div>
      </form>
    </Modal>
  );
}
