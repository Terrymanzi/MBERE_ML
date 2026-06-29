import type { ContractFeature } from "@/services";

/**
 * Helpers that turn the model's feature contract into a submittable form.
 *
 * The DOM always yields string values; the backend expects native types
 * (numeric -> float, categorical -> the category's native type). These helpers
 * keep that conversion in one place so the form stays generic across datasets.
 */

export type FormValues = Record<string, string>;

export function isNumericFeature(f: ContractFeature): boolean {
  return f.kind === "numeric" || f.encoding === "numeric";
}

/** Sensible default so the form is immediately submittable for a demo. */
export function defaultValueFor(f: ContractFeature): string {
  if (!isNumericFeature(f) && f.categories && f.categories.length > 0) {
    return String(f.categories[0]);
  }
  return "0";
}

export function initialValues(features: ContractFeature[]): FormValues {
  const values: FormValues = {};
  for (const f of features) values[f.name] = defaultValueFor(f);
  return values;
}

export interface BuildResult {
  features: Record<string, unknown>;
  errors: Record<string, string>;
}

/** Convert string form values to the typed feature map the API expects. */
export function buildFeaturePayload(
  features: ContractFeature[],
  values: FormValues,
): BuildResult {
  const out: Record<string, unknown> = {};
  const errors: Record<string, string> = {};

  for (const f of features) {
    const raw = values[f.name] ?? "";
    if (isNumericFeature(f)) {
      if (raw.trim() === "") {
        errors[f.name] = "Required";
        continue;
      }
      const n = Number(raw);
      if (!Number.isFinite(n)) {
        errors[f.name] = "Must be a number";
        continue;
      }
      out[f.name] = n;
    } else {
      // Recover the category's native type (numbers stay numbers).
      const match = f.categories?.find((c) => String(c) === raw);
      out[f.name] = match ?? raw;
    }
  }

  return { features: out, errors };
}
