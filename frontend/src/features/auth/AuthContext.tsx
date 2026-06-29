import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import type { ReactNode } from "react";
import { useQueryClient } from "@tanstack/react-query";
import {
  getCurrentUser,
  login as loginRequest,
  type UserRead,
} from "@/services";
import {
  clearToken,
  getToken,
  setToken,
  UNAUTHORIZED_EVENT,
} from "@/services/tokenStore";
import { queryKeys } from "@/lib/queryKeys";

interface AuthContextValue {
  user: UserRead | null;
  isAuthenticated: boolean;
  /** True while we validate an existing token on first load. */
  isInitialising: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient();
  const [user, setUser] = useState<UserRead | null>(null);
  const [hasToken, setHasToken] = useState<boolean>(() => getToken() != null);
  const [isInitialising, setIsInitialising] = useState<boolean>(
    () => getToken() != null,
  );

  const logout = useCallback(() => {
    clearToken();
    setHasToken(false);
    setUser(null);
    queryClient.clear();
  }, [queryClient]);

  // Validate a persisted token on mount (and whenever a token appears).
  useEffect(() => {
    if (!hasToken) {
      setIsInitialising(false);
      return;
    }
    let cancelled = false;
    const controller = new AbortController();
    setIsInitialising(true);
    getCurrentUser(controller.signal)
      .then((me) => {
        if (!cancelled) setUser(me);
      })
      .catch(() => {
        // invalid/expired token -> drop it silently
        if (!cancelled) {
          clearToken();
          setHasToken(false);
          setUser(null);
        }
      })
      .finally(() => {
        if (!cancelled) setIsInitialising(false);
      });
    return () => {
      cancelled = true;
      controller.abort();
    };
  }, [hasToken]);

  // Global 401 handler: any authed request that 401s forces a logout.
  useEffect(() => {
    const handler = () => logout();
    window.addEventListener(UNAUTHORIZED_EVENT, handler);
    return () => window.removeEventListener(UNAUTHORIZED_EVENT, handler);
  }, [logout]);

  const login = useCallback(
    async (email: string, password: string) => {
      const token = await loginRequest(email, password);
      setToken(token.access_token);
      const me = await getCurrentUser();
      setUser(me);
      setHasToken(true);
      queryClient.setQueryData(queryKeys.me, me);
    },
    [queryClient],
  );

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isAuthenticated: hasToken && user != null,
      isInitialising,
      login,
      logout,
    }),
    [user, hasToken, isInitialising, login, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within <AuthProvider>");
  return ctx;
}
