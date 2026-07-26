import { apiRequest } from "./apiClient";
import type { AuditLogRead } from "./types";

export function listAuditLogs(
  params: { limit?: number; offset?: number } = {},
  signal?: AbortSignal,
): Promise<AuditLogRead[]> {
  const search = new URLSearchParams();
  if (params.limit != null) search.set("limit", String(params.limit));
  if (params.offset != null) search.set("offset", String(params.offset));
  const qs = search.toString();
  return apiRequest<AuditLogRead[]>(`/audit-logs${qs ? `?${qs}` : ""}`, { signal });
}
