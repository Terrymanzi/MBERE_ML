import { apiRequest } from "./apiClient";
import type {
  AdminResetPasswordRequest,
  UserAdminCreate,
  UserAdminUpdate,
  UserRead,
  UserRole,
} from "./types";

export interface ListUsersParams {
  limit?: number;
  offset?: number;
  q?: string;
}

export function listUsers(
  params: ListUsersParams = {},
  signal?: AbortSignal,
): Promise<UserRead[]> {
  const search = new URLSearchParams();
  if (params.limit != null) search.set("limit", String(params.limit));
  if (params.offset != null) search.set("offset", String(params.offset));
  if (params.q) search.set("q", params.q);
  const qs = search.toString();
  return apiRequest<UserRead[]>(`/users${qs ? `?${qs}` : ""}`, { signal });
}

export function createUser(payload: UserAdminCreate): Promise<UserRead> {
  return apiRequest<UserRead>("/users", { method: "POST", json: payload });
}

export function updateUser(userId: number, payload: UserAdminUpdate): Promise<UserRead> {
  return apiRequest<UserRead>(`/users/${userId}`, { method: "PUT", json: payload });
}

export function deleteUser(userId: number): Promise<void> {
  return apiRequest<void>(`/users/${userId}`, { method: "DELETE" });
}

export function updateUserRole(userId: number, role: UserRole): Promise<UserRead> {
  return apiRequest<UserRead>(`/users/${userId}/role`, { method: "PATCH", json: { role } });
}

export function updateUserActive(userId: number, is_active: boolean): Promise<UserRead> {
  return apiRequest<UserRead>(`/users/${userId}/active`, {
    method: "PATCH",
    json: { is_active },
  });
}

export function resetUserPassword(
  userId: number,
  payload: AdminResetPasswordRequest,
): Promise<void> {
  return apiRequest<void>(`/users/${userId}/reset-password`, { method: "POST", json: payload });
}
