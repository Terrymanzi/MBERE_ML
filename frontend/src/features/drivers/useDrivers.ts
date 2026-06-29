import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  createDriver,
  getDriverRiskHistory,
  listDrivers,
  type DriverCreate,
} from "@/services";
import { queryKeys } from "@/lib/queryKeys";

const DRIVERS_PAGE = { limit: 200, offset: 0 } as const;

export function useDrivers() {
  return useQuery({
    queryKey: queryKeys.drivers(DRIVERS_PAGE),
    queryFn: ({ signal }) => listDrivers(DRIVERS_PAGE, signal),
  });
}

export function useDriverRiskHistory(driverId: number | undefined) {
  return useQuery({
    queryKey: driverId != null ? queryKeys.driverRisk(driverId) : ["risk", "none"],
    queryFn: ({ signal }) => getDriverRiskHistory(driverId as number, signal),
    enabled: driverId != null,
  });
}

export function useCreateDriver() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: DriverCreate) => createDriver(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["drivers"] });
      queryClient.invalidateQueries({ queryKey: queryKeys.dashboard });
    },
  });
}
