import { describe, expect, it } from "vitest";
import {
  formatDate,
  formatDateTime,
  formatNumber,
  formatPercent,
  relativeTime,
  riskBadgeClasses,
} from "./format";

describe("formatDate", () => {
  it("returns an em dash for missing input", () => {
    expect(formatDate(null)).toBe("—");
    expect(formatDate(undefined)).toBe("—");
  });

  it("returns an em dash for an unparseable string", () => {
    expect(formatDate("not-a-date")).toBe("—");
  });

  it("formats a valid ISO date", () => {
    expect(formatDate("2026-01-15T10:00:00Z")).toContain("2026");
  });
});

describe("formatDateTime", () => {
  it("returns an em dash for missing/invalid input", () => {
    expect(formatDateTime(null)).toBe("—");
    expect(formatDateTime("garbage")).toBe("—");
  });
});

describe("relativeTime", () => {
  it("returns an em dash for missing input", () => {
    expect(relativeTime(null)).toBe("—");
  });

  it("reports 'just now' for the current instant", () => {
    expect(relativeTime(new Date().toISOString())).toBe("just now");
  });

  it("reports minutes ago for a recent timestamp", () => {
    const fiveMinAgo = new Date(Date.now() - 5 * 60_000).toISOString();
    expect(relativeTime(fiveMinAgo)).toBe("5 min ago");
  });
});

describe("formatPercent", () => {
  it("formats a fraction as a percentage string", () => {
    expect(formatPercent(0.5)).toBe("50.0%");
    expect(formatPercent(0.3473, 2)).toBe("34.73%");
  });

  it("returns an em dash for non-finite input", () => {
    expect(formatPercent(NaN)).toBe("—");
  });
});

describe("formatNumber", () => {
  it("returns an em dash for null/undefined", () => {
    expect(formatNumber(null)).toBe("—");
    expect(formatNumber(undefined)).toBe("—");
  });

  it("formats numeric strings", () => {
    expect(formatNumber("1234")).toBe("1,234");
  });

  it("passes through a non-numeric string unchanged", () => {
    expect(formatNumber("n/a")).toBe("n/a");
  });
});

describe("riskBadgeClasses", () => {
  it("maps each risk band to a distinct class string", () => {
    const low = riskBadgeClasses("Low");
    const medium = riskBadgeClasses("Medium");
    const high = riskBadgeClasses("High");
    expect(new Set([low, medium, high]).size).toBe(3);
    expect(high).toContain("red");
    expect(medium).toContain("amber");
    expect(low).toContain("green");
  });
});
