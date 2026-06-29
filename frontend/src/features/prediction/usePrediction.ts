import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  getFeatureContract,
  predict,
  type PredictRequest,
} from "@/services";
import { queryKeys } from "@/lib/queryKeys";

/** Active model's feature contract — drives the prediction form. */
export function useFeatureContract() {
  return useQuery({
    queryKey: queryKeys.contract,
    queryFn: ({ signal }) => getFeatureContract(signal),
    staleTime: 5 * 60_000,
  });
}

export function usePredict() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: PredictRequest) => predict(payload),
    onSuccess: (_data, variables) => {
      // A new assessment affects dashboard aggregates and the driver's history.
      queryClient.invalidateQueries({ queryKey: queryKeys.dashboard });
      if (variables.driver_id != null) {
        queryClient.invalidateQueries({
          queryKey: queryKeys.driverRisk(variables.driver_id),
        });
      }
    },
  });
}
