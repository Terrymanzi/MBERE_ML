import { useMemo, useState } from "react";
import type { FormEvent } from "react";
import type { ContractFeature, DriverRead, ModelCatalogEntry } from "@/services";
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
  models: ModelCatalogEntry[];
  activeModelName: string | null;
  initialDriverId?: number | null;
  isSubmitting: boolean;
  onSubmit: (
    features: Record<string, unknown>,
    driverId: number | null,
    modelName: string | null,
  ) => void;
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
  models,
  activeModelName,
  initialDriverId,
  isSubmitting,
  onSubmit,
}: PredictionFormProps) {
  const [values, setValues] = useState<FormValues>(() => initialValues(features));
  const [driverId, setDriverId] = useState<string>(
    initialDriverId != null ? String(initialDriverId) : "",
  );
  const [modelName, setModelName] = useState<string>("");
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
    onSubmit(payload, driverId ? Number(driverId) : null, modelName || null);
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-8">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
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

        <Select
          label="Model"
          hint="Defaults to the active model; pick a different one to score just this prediction."
          value={modelName}
          onChange={(e) => setModelName(e.target.value)}
        >
          <option value="">
            Active model{activeModelName ? ` (${activeModelName})` : ""}
          </option>
          {models.map((m) => (
            <option key={m.name} value={m.name}>
              {m.name}
              {m.metrics_test ? ` — F1 ${(m.metrics_test.f1_macro * 100).toFixed(0)}%` : ""}
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
