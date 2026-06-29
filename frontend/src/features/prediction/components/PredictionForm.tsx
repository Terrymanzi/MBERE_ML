import { useMemo, useState } from "react";
import type { FormEvent } from "react";
import type { ContractFeature, DriverRead } from "@/services";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import {
  buildFeaturePayload,
  initialValues,
  isNumericFeature,
  type FormValues,
} from "../featureForm";

interface PredictionFormProps {
  features: ContractFeature[];
  drivers: DriverRead[];
  initialDriverId?: number | null;
  isSubmitting: boolean;
  onSubmit: (features: Record<string, unknown>, driverId: number | null) => void;
}

function FeatureField({
  feature,
  value,
  error,
  onChange,
}: {
  feature: ContractFeature;
  value: string;
  error?: string;
  onChange: (v: string) => void;
}) {
  if (!isNumericFeature(feature) && feature.categories?.length) {
    return (
      <Select
        label={feature.name}
        value={value}
        error={error}
        onChange={(e) => onChange(e.target.value)}
      >
        {feature.categories.map((c) => (
          <option key={String(c)} value={String(c)}>
            {String(c)}
          </option>
        ))}
      </Select>
    );
  }
  return (
    <Input
      label={feature.name}
      type="number"
      step="any"
      value={value}
      error={error}
      onChange={(e) => onChange(e.target.value)}
    />
  );
}

export function PredictionForm({
  features,
  drivers,
  initialDriverId,
  isSubmitting,
  onSubmit,
}: PredictionFormProps) {
  const [values, setValues] = useState<FormValues>(() => initialValues(features));
  const [driverId, setDriverId] = useState<string>(
    initialDriverId != null ? String(initialDriverId) : "",
  );
  const [errors, setErrors] = useState<Record<string, string>>({});

  const { categorical, numeric } = useMemo(() => {
    return {
      categorical: features.filter(
        (f) => !isNumericFeature(f) && f.categories?.length,
      ),
      numeric: features.filter(
        (f) => isNumericFeature(f) || !f.categories?.length,
      ),
    };
  }, [features]);

  function setField(name: string, v: string) {
    setValues((prev) => ({ ...prev, [name]: v }));
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const { features: payload, errors: fieldErrors } = buildFeaturePayload(
      features,
      values,
    );
    setErrors(fieldErrors);
    if (Object.keys(fieldErrors).length > 0) return;
    onSubmit(payload, driverId ? Number(driverId) : null);
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-8">
      <div>
        <Select
          label="Driver (optional)"
          hint="Attach this assessment to a driver to store it in their history."
          value={driverId}
          onChange={(e) => setDriverId(e.target.value)}
        >
          <option value="">No driver — one-off prediction</option>
          {drivers.map((d) => (
            <option key={d.id} value={d.id}>
              {d.full_name} ({d.license_number})
            </option>
          ))}
        </Select>
      </div>

      {categorical.length > 0 && (
        <fieldset>
          <legend className="mb-3 text-sm font-semibold text-slate-700">
            Categorical features
          </legend>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
            {categorical.map((f) => (
              <FeatureField
                key={f.name}
                feature={f}
                value={values[f.name] ?? ""}
                error={errors[f.name]}
                onChange={(v) => setField(f.name, v)}
              />
            ))}
          </div>
        </fieldset>
      )}

      {numeric.length > 0 && (
        <fieldset>
          <legend className="mb-3 text-sm font-semibold text-slate-700">
            Numeric features
          </legend>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
            {numeric.map((f) => (
              <FeatureField
                key={f.name}
                feature={f}
                value={values[f.name] ?? ""}
                error={errors[f.name]}
                onChange={(v) => setField(f.name, v)}
              />
            ))}
          </div>
        </fieldset>
      )}

      <div className="flex flex-wrap items-center gap-3 border-t border-slate-100 pt-5">
        <Button type="submit" size="lg" loading={isSubmitting}>
          Run prediction
        </Button>
        <Button
          type="button"
          variant="secondary"
          onClick={() => {
            setValues(initialValues(features));
            setErrors({});
          }}
        >
          Reset to defaults
        </Button>
      </div>
    </form>
  );
}
