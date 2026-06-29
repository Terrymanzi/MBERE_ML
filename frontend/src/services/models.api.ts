import { apiRequest } from "./apiClient";
import type { FeatureContractResponse, ModelVersionRead } from "./types";

/** Registry of served/known model versions (public endpoint). */
export function listModels(signal?: AbortSignal): Promise<ModelVersionRead[]> {
  return apiRequest<ModelVersionRead[]>("/models", { auth: false, signal });
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
