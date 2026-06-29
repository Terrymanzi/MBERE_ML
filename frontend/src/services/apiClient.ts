/**
 * Typed fetch wrapper for the FastAPI backend.
 *
 * Responsibilities:
 *  - resolve the base URL from the environment (no host hardcoded);
 *  - attach the JWT bearer token to every request when present;
 *  - parse JSON responses and normalise FastAPI error bodies into ApiError;
 *  - support form-encoded posts (the OAuth2 /auth/token endpoint).
 */
import type { ApiErrorBody } from "./types";
import { getToken, notifyUnauthorized } from "./tokenStore";

const BASE_URL = (
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000"
).replace(/\/$/, "");

export class ApiError extends Error {
  readonly status: number;
  readonly detail: unknown;

  constructor(status: number, message: string, detail?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

/** Pull a human-readable message out of FastAPI's many error body shapes. */
function messageFromBody(status: number, body: unknown): string {
  if (body && typeof body === "object" && "detail" in body) {
    const detail = (body as ApiErrorBody).detail;
    if (typeof detail === "string") return detail;
    if (detail && typeof detail === "object" && "message" in detail) {
      return String((detail as { message: unknown }).message);
    }
    // 422 validation error array
    if (Array.isArray(detail) && detail.length > 0) {
      const first = detail[0] as { msg?: string };
      if (first?.msg) return first.msg;
    }
  }
  return `Request failed (${status})`;
}

interface RequestOptions {
  method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
  /** JSON body — serialised with the application/json content type. */
  json?: unknown;
  /** Form body — serialised as application/x-www-form-urlencoded. */
  form?: Record<string, string>;
  /** Whether to attach the bearer token (default true). */
  auth?: boolean;
  signal?: AbortSignal;
}

export async function apiRequest<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const { method = "GET", json, form, auth = true, signal } = options;

  const headers: Record<string, string> = {};
  let body: BodyInit | undefined;

  if (json !== undefined) {
    headers["Content-Type"] = "application/json";
    body = JSON.stringify(json);
  } else if (form !== undefined) {
    headers["Content-Type"] = "application/x-www-form-urlencoded";
    body = new URLSearchParams(form).toString();
  }

  if (auth) {
    const token = getToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;
  }

  let response: Response;
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      method,
      headers,
      body,
      signal,
    });
  } catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") throw err;
    throw new ApiError(0, "Cannot reach the server. try again!", err);
  }

  if (response.status === 401 && auth) {
    notifyUnauthorized();
  }

  // 204 / empty body
  if (response.status === 204) {
    return undefined as T;
  }

  const text = await response.text();
  const parsed: unknown = text ? safeJsonParse(text) : undefined;

  if (!response.ok) {
    throw new ApiError(
      response.status,
      messageFromBody(response.status, parsed),
      parsed,
    );
  }

  return parsed as T;
}

function safeJsonParse(text: string): unknown {
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

export { BASE_URL as API_BASE_URL };
