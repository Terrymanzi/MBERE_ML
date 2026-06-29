import type { RiskBand } from "@/services";

export function formatDate(iso: string | null | undefined): string {
  if (!iso) return "—";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "—";
  return d.toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export function formatDateTime(iso: string | null | undefined): string {
  if (!iso) return "—";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "—";
  return d.toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function relativeTime(iso: string | null | undefined): string {
  if (!iso) return "—";
  const d = new Date(iso).getTime();
  if (Number.isNaN(d)) return "—";
  const diffMs = Date.now() - d;
  const mins = Math.round(diffMs / 60_000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins} min ago`;
  const hours = Math.round(mins / 60);
  if (hours < 24) return `${hours} h ago`;
  const days = Math.round(hours / 24);
  return `${days} d ago`;
}

export function formatPercent(value: number, digits = 1): string {
  if (!Number.isFinite(value)) return "—";
  return `${(value * 100).toFixed(digits)}%`;
}

export function formatNumber(value: number | string | null | undefined): string {
  if (value == null) return "—";
  const n = typeof value === "string" ? Number(value) : value;
  if (!Number.isFinite(n)) return String(value);
  return n.toLocaleString();
}

/** Tailwind colour tokens per risk band (single source of truth for charts/badges). */
export const RISK_COLORS: Record<RiskBand, string> = {
  Low: "#16a34a",
  Medium: "#d97706",
  High: "#dc2626",
};

export const RISK_BANDS: RiskBand[] = ["Low", "Medium", "High"];

export function riskBadgeClasses(band: RiskBand): string {
  switch (band) {
    case "High":
      return "bg-red-50 text-red-700 ring-red-600/20";
    case "Medium":
      return "bg-amber-50 text-amber-700 ring-amber-600/20";
    case "Low":
    default:
      return "bg-green-50 text-green-700 ring-green-600/20";
  }
}
