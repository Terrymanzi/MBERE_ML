import { afterEach, describe, expect, it, vi } from "vitest";
import {
  clearToken,
  getRefreshToken,
  getToken,
  notifyUnauthorized,
  setRefreshToken,
  setToken,
  UNAUTHORIZED_EVENT,
} from "./tokenStore";

afterEach(() => {
  localStorage.clear();
});

describe("tokenStore", () => {
  it("returns null when no token has been set", () => {
    expect(getToken()).toBeNull();
  });

  it("round-trips a token through set/get", () => {
    setToken("abc.def.ghi");
    expect(getToken()).toBe("abc.def.ghi");
  });

  it("clears a stored token", () => {
    setToken("abc.def.ghi");
    clearToken();
    expect(getToken()).toBeNull();
  });

  it("round-trips a refresh token, cleared alongside the access token", () => {
    setToken("abc.def.ghi");
    setRefreshToken("refresh.abc.def");
    expect(getRefreshToken()).toBe("refresh.abc.def");
    clearToken();
    expect(getRefreshToken()).toBeNull();
  });

  it("does not throw when localStorage access fails", () => {
    const spy = vi
      .spyOn(Storage.prototype, "getItem")
      .mockImplementation(() => {
        throw new Error("storage disabled");
      });
    expect(getToken()).toBeNull();
    spy.mockRestore();
  });

  it("dispatches the unauthorized event", () => {
    const handler = vi.fn();
    window.addEventListener(UNAUTHORIZED_EVENT, handler);
    notifyUnauthorized();
    expect(handler).toHaveBeenCalledTimes(1);
    window.removeEventListener(UNAUTHORIZED_EVENT, handler);
  });
});
