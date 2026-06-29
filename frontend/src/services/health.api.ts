import { apiRequest } from "./apiClient";
import type { HealthResponse } from "./types";

export function getHealth(signal?: AbortSignal): Promise<HealthResponse> {
  return apiRequest<HealthResponse>("/health", { auth: false, signal });
}
