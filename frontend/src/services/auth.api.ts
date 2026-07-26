import { apiRequest } from "./apiClient";
import type { ChangePasswordRequest, Token, UserCreate, UserRead } from "./types";

/** OAuth2 password flow — the backend expects form-encoded username/password. */
export function login(email: string, password: string): Promise<Token> {
  return apiRequest<Token>("/auth/token", {
    method: "POST",
    form: { username: email, password },
    auth: false,
  });
}

export function register(payload: UserCreate): Promise<UserRead> {
  return apiRequest<UserRead>("/auth/register", {
    method: "POST",
    json: payload,
    auth: false,
  });
}

export function getCurrentUser(signal?: AbortSignal): Promise<UserRead> {
  return apiRequest<UserRead>("/auth/me", { signal });
}

export function refreshToken(refresh_token: string): Promise<Token> {
  return apiRequest<Token>("/auth/refresh", {
    method: "POST",
    json: { refresh_token },
    auth: false,
  });
}

/** Best-effort: tokens are stateless today, so this doesn't invalidate
 * anything server-side yet — callers should still clear local storage. */
export function logout(): Promise<void> {
  return apiRequest<void>("/auth/logout", { method: "POST" });
}

export function changePassword(payload: ChangePasswordRequest): Promise<void> {
  return apiRequest<void>("/auth/change-password", { method: "POST", json: payload });
}
