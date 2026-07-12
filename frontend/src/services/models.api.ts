import { apiRequest } from "./apiClient";
import type {
  FeatureContractResponse,
  ModelCatalogResponse,
  ModelVersionRead,
} from "./types";

/** Registry of served/known model versions (public endpoint). */
export function listModels(signal?: AbortSignal): Promise<ModelVersionRead[]> {
  return apiRequest<ModelVersionRead[]>("/models", { auth: false, signal });
}

/** All selectable models on disk with performance highlights (public endpoint). */
export function getModelCatalog(
  signal?: AbortSignal,
): Promise<ModelCatalogResponse> {
  return apiRequest<ModelCatalogResponse>("/models/catalog", {
    auth: false,
    signal,
  });
}

/** Set the org-wide active model used by default for predictions. */
export function activateModel(name: string): Promise<ModelVersionRead> {
  return apiRequest<ModelVersionRead>(
    `/models/${encodeURIComponent(name)}/activate`,
    { method: "POST" },
  );
}

/** Feature contract of the active model — drives the prediction form. */
export function getFeatureContract(
  signal?: AbortSignal,
): Promise<FeatureContractResponse> {
  return apiRequest<FeatureContractResponse>("/models/contract", {
    auth: false,
    signal,
  });
}
