/**
 * API types — mirror the backend Pydantic schemas 1:1.
 *
 * Source of truth: backend/schemas/{auth,driver,prediction}.py. Keep these in
 * sync with the FastAPI response_model definitions; nothing here is invented.
 */

// ---------------------------------------------------------------- auth --------
export interface UserRead {
  id: number;
  email: string;
  full_name: string | null;
  is_active: boolean;
  created_at: string; // ISO datetime
}

export interface UserCreate {
  email: string;
  password: string;
  full_name?: string | null;
}

export interface Token {
  access_token: string;
  token_type: string;
}

// --------------------------------------------------------------- drivers ------
export interface DriverRead {
  id: number;
  license_number: string;
  full_name: string;
  date_of_birth: string | null; // ISO date
  notes: string | null;
  created_by_user_id: number | null;
  created_at: string;
}

export interface DriverCreate {
  license_number: string;
  full_name: string;
  date_of_birth?: string | null;
  notes?: string | null;
}

// ----------------------------------------------------------- model / contract -
export type ModelKind = "binary" | "multiclass" | string;

export interface ModelInfo {
  name: string;
  version: string;
  dataset: string;
  kind: ModelKind;
  classes: string[];
}

export type FeatureKind = "categorical" | "numeric";

export interface ContractFeature {
  name: string;
  kind: FeatureKind;
  encoding: string; // ordinal | onehot | numeric
  dtype: string;
  categories?: Array<string | number> | null;
}

export interface FeatureContractResponse {
  model: ModelInfo;
  input_features: ContractFeature[];
}

export interface ModelVersionRead {
  id: number;
  name: string;
  version: string;
  dataset_name: string;
  kind: ModelKind;
  target_classes: string[];
  git_commit: string | null;
  metrics: Record<string, number | string | null>;
  is_active: boolean;
  created_at: string;
}

// ------------------------------------------------------------- prediction -----
export type RiskBand = "Low" | "Medium" | "High";

export interface FeatureContribution {
  feature: string;
  value: unknown | null;
  contribution: number;
  abs_contribution: number;
}

export interface Explanation {
  method: string; // shap | linear | none
  base_value: number | null;
  top_features: FeatureContribution[];
}

export interface PredictRequest {
  driver_id?: number | null;
  features: Record<string, unknown>;
}

export interface PredictResponse {
  risk_assessment_id: number;
  prediction_id: number;
  driver_id: number | null;
  model: ModelInfo;
  predicted_class: string;
  risk_band: RiskBand;
  risk_score: number; // [0,1]
  probabilities: Record<string, number>;
  explanation: Explanation;
  created_at: string;
}

export interface PredictionRead {
  id: number;
  predicted_class: string;
  risk_band: RiskBand;
  risk_score: number;
  probabilities: Record<string, number>;
  explanation: Explanation; // persisted as JSON of the Explanation shape
  model_version_id: number;
  created_at: string;
}

export interface RiskAssessmentRead {
  id: number;
  driver_id: number | null;
  status: string;
  created_at: string;
  prediction: PredictionRead | null;
}

// ------------------------------------------------------------- system ---------
export interface HealthResponse {
  status: string; // ok | degraded
  db_ok: boolean;
  model_loaded: boolean;
  model: ModelInfo | null;
  n_input_features: number | null;
}

/** Shape of FastAPI/Starlette error bodies ({ detail: ... }). */
export interface ApiErrorBody {
  detail?: unknown;
}
