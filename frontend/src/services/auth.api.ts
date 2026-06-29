import { apiRequest } from "./apiClient";
import type { Token, UserCreate, UserRead } from "./types";

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
