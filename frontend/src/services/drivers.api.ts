import { apiRequest } from "./apiClient";
import type {
  DriverCreate,
  DriverRead,
  RiskAssessmentRead,
} from "./types";

export interface ListDriversParams {
  limit?: number;
  offset?: number;
}

export function listDrivers(
  params: ListDriversParams = {},
  signal?: AbortSignal,
): Promise<DriverRead[]> {
  const search = new URLSearchParams();
  if (params.limit != null) search.set("limit", String(params.limit));
  if (params.offset != null) search.set("offset", String(params.offset));
  const qs = search.toString();
  return apiRequest<DriverRead[]>(`/drivers${qs ? `?${qs}` : ""}`, { signal });
}

export function createDriver(payload: DriverCreate): Promise<DriverRead> {
  return apiRequest<DriverRead>("/drivers", { method: "POST", json: payload });
}

export function getDriverRiskHistory(
  driverId: number,
  signal?: AbortSignal,
): Promise<RiskAssessmentRead[]> {
  return apiRequest<RiskAssessmentRead[]>(`/risk/${driverId}`, { signal });
}
