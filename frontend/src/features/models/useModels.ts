import { useQuery } from "@tanstack/react-query";
import { listModels, type ModelVersionRead } from "@/services";
import { queryKeys } from "@/lib/queryKeys";

export function useModels() {
  return useQuery({
    queryKey: queryKeys.models,
    queryFn: ({ signal }) => listModels(signal),
  });
}

export function activeModel(
  models: ModelVersionRead[] | undefined,
): ModelVersionRead | null {
  if (!models || models.length === 0) return null;
  return models.find((m) => m.is_active) ?? models[0];
}
