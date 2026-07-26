import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "./AuthContext";
import { LoadingState } from "@/components/feedback/states";

/** Gate for admin-only areas. Redirects non-admins back to the dashboard
 * rather than a broken page -- mirrors ProtectedRoute's loading/redirect
 * structure. */
export function RequireAdmin() {
  const { user, isInitialising } = useAuth();

  if (isInitialising) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <LoadingState label="Loading…" />
      </div>
    );
  }

  if (user?.role !== "ADMIN") {
    return <Navigate to="/app" replace />;
  }

  return <Outlet />;
}
