import { useQuery } from "@tanstack/react-query";
import { getHealth } from "@/services";
import { queryKeys } from "@/lib/queryKeys";

/** Polls backend liveness + which model is loaded. */
export function useHealth() {
  return useQuery({
    queryKey: queryKeys.health,
    queryFn: ({ signal }) => getHealth(signal),
    refetchInterval: 60_000,
    staleTime: 30_000,
  });
}
