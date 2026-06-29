import { apiRequest } from "./apiClient";
import type { PredictRequest, PredictResponse } from "./types";

export function predict(payload: PredictRequest): Promise<PredictResponse> {
  return apiRequest<PredictResponse>("/predict", {
    method: "POST",
    json: payload,
  });
}
