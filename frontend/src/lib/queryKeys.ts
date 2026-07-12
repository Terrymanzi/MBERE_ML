/** Centralised TanStack Query keys so invalidation stays consistent. */
export const queryKeys = {
  me: ["me"] as const,
  health: ["health"] as const,
  models: ["models"] as const,
  modelCatalog: ["models", "catalog"] as const,
  contract: ["contract"] as const,
  drivers: (params?: { limit?: number; offset?: number }) =>
    ["drivers", params ?? {}] as const,
  driverRisk: (driverId: number) => ["risk", driverId] as const,
  dashboard: ["dashboard"] as const,
};
