import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  activateModel,
  getModelCatalog,
  listModels,
  type ModelVersionRead,
} from "@/services";
import { queryKeys } from "@/lib/queryKeys";

export function useModels() {
  return useQuery({
    queryKey: queryKeys.models,
    queryFn: ({ signal }) => listModels(signal),
  });
}

export function useModelCatalog() {
  return useQuery({
    queryKey: queryKeys.modelCatalog,
    queryFn: ({ signal }) => getModelCatalog(signal),
  });
}

export function useActivateModel() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (name: string) => activateModel(name),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.models });
      queryClient.invalidateQueries({ queryKey: queryKeys.modelCatalog });
      queryClient.invalidateQueries({ queryKey: queryKeys.contract });
    },
  });
}

export function activeModel(
  models: ModelVersionRead[] | undefined,
): ModelVersionRead | null {
  if (!models || models.length === 0) return null;
  return models.find((m) => m.is_active) ?? models[0];
}
