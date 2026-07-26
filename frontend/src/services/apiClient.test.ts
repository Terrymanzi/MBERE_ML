import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { apiRequest, ApiError } from "./apiClient";
import {
  UNAUTHORIZED_EVENT,
  clearToken,
  getToken,
  setRefreshToken,
  setToken,
} from "./tokenStore";

describe("apiRequest", () => {
  beforeEach(() => {
    clearToken();
    vi.restoreAllMocks();
  });
  afterEach(() => {
    clearToken();
  });

  it("attaches the bearer token when one is stored", async () => {
    setToken("test-token");
    const fetchMock = vi.fn(
      async (_url: string, _init?: RequestInit) =>
        new Response(JSON.stringify({ ok: true }), {
          status: 200,
          headers: { "content-type": "application/json" },
        }),
    );
    vi.stubGlobal("fetch", fetchMock);

    await apiRequest("/health");

    const [, init] = fetchMock.mock.calls[0];
    expect((init!.headers as Record<string, string>).Authorization).toBe(
      "Bearer test-token",
    );
  });

  it("omits the Authorization header when auth: false", async () => {
    setToken("test-token");
    const fetchMock = vi.fn(
      async (_url: string, _init?: RequestInit) =>
        new Response(JSON.stringify({}), { status: 200 }),
    );
    vi.stubGlobal("fetch", fetchMock);

    await apiRequest("/auth/token", { auth: false });

    const [, init] = fetchMock.mock.calls[0];
    expect((init!.headers as Record<string, string>).Authorization).toBeUndefined();
  });

  it("throws ApiError with a message extracted from a FastAPI detail string", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(
        async () =>
          new Response(JSON.stringify({ detail: "Invalid credentials" }), {
            status: 401,
          }),
      ),
    );

    await expect(apiRequest("/auth/token", { auth: false })).rejects.toMatchObject({
      name: "ApiError",
      status: 401,
      message: "Invalid credentials",
    });
  });

  it("extracts the first message from a 422 validation error array", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(
        async () =>
          new Response(
            JSON.stringify({ detail: [{ msg: "field required" }] }),
            { status: 422 },
          ),
      ),
    );

    await expect(apiRequest("/predict", { auth: false })).rejects.toMatchObject({
      status: 422,
      message: "field required",
    });
  });

  it("dispatches the unauthorized event on a 401 for an authed request", async () => {
    setToken("expired-token");
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => new Response(JSON.stringify({ detail: "expired" }), { status: 401 })),
    );
    const handler = vi.fn();
    window.addEventListener(UNAUTHORIZED_EVENT, handler);

    await expect(apiRequest("/drivers")).rejects.toBeInstanceOf(ApiError);
    expect(handler).toHaveBeenCalledTimes(1);

    window.removeEventListener(UNAUTHORIZED_EVENT, handler);
  });

  it("silently refreshes and retries once on a 401 when a refresh token exists", async () => {
    setToken("expired-token");
    setRefreshToken("valid-refresh-token");
    const fetchMock = vi.fn(async (url: string) => {
      if (url.endsWith("/auth/refresh")) {
        return new Response(
          JSON.stringify({ access_token: "new-token", refresh_token: "new-refresh", token_type: "bearer" }),
          { status: 200, headers: { "content-type": "application/json" } },
        );
      }
      if (url.endsWith("/drivers")) {
        const isRetry = fetchMock.mock.calls.filter((c) => (c[0] as string).endsWith("/drivers")).length > 1;
        return new Response(JSON.stringify(isRetry ? [{ id: 1 }] : { detail: "expired" }), {
          status: isRetry ? 200 : 401,
        });
      }
      throw new Error(`unexpected url ${url}`);
    });
    vi.stubGlobal("fetch", fetchMock);

    const result = await apiRequest("/drivers");
    expect(result).toEqual([{ id: 1 }]);
    expect(getToken()).toBe("new-token");
  });

  it("logs out without retrying if the refresh itself fails", async () => {
    setToken("expired-token");
    setRefreshToken("stale-refresh-token");
    vi.stubGlobal(
      "fetch",
      vi.fn(async (url: string) => {
        if (url.endsWith("/auth/refresh")) {
          return new Response(JSON.stringify({ detail: "invalid refresh" }), { status: 401 });
        }
        return new Response(JSON.stringify({ detail: "expired" }), { status: 401 });
      }),
    );
    const handler = vi.fn();
    window.addEventListener(UNAUTHORIZED_EVENT, handler);

    await expect(apiRequest("/drivers")).rejects.toBeInstanceOf(ApiError);
    expect(handler).toHaveBeenCalledTimes(1);
    expect(getToken()).toBeNull();

    window.removeEventListener(UNAUTHORIZED_EVENT, handler);
  });

  it("wraps a network failure in an ApiError with status 0", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => {
        throw new TypeError("Failed to fetch");
      }),
    );

    await expect(apiRequest("/health")).rejects.toMatchObject({ status: 0 });
  });

  it("returns undefined for a 204 No Content response", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => new Response(null, { status: 204 })),
    );

    await expect(apiRequest("/drivers/1")).resolves.toBeUndefined();
  });
});
