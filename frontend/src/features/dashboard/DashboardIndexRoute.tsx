import { useAuth } from "@/features/auth/AuthContext";
import { DashboardPage } from "./DashboardPage";
import { AdminDashboardPage } from "./AdminDashboardPage";

/** Same "Dashboard" nav destination for everyone -- Admin sees a different
 * view there, not a different URL (Insurer/Fleet Manager have identical
 * dashboard needs per the RBAC matrix, so they keep sharing DashboardPage). */
export function DashboardIndexRoute() {
  const { user } = useAuth();
  return user?.role === "ADMIN" ? <AdminDashboardPage /> : <DashboardPage />;
}
