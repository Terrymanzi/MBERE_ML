/**
 * JWT persistence. The token lives in localStorage so a refresh keeps the
 * session; the API client reads it here to attach the Authorization header.
 *
 * Kept deliberately tiny and dependency-free so both the API client and the
 * auth context can share it without a circular import.
 */
const STORAGE_KEY = "mbere.jwt";

/** Dispatched when an authed request gets a 401 — the auth layer logs out. */
export const UNAUTHORIZED_EVENT = "mbere:unauthorized";

export function getToken(): string | null {
  try {
    return localStorage.getItem(STORAGE_KEY);
  } catch {
    return null;
  }
}

export function setToken(token: string): void {
  try {
    localStorage.setItem(STORAGE_KEY, token);
  } catch {
    /* storage unavailable (private mode) — session is in-memory only */
  }
}

export function clearToken(): void {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch {
    /* ignore */
  }
}

export function notifyUnauthorized(): void {
  if (typeof window !== "undefined") {
    window.dispatchEvent(new Event(UNAUTHORIZED_EVENT));
  }
}
