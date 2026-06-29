import { Route, Routes } from "react-router-dom";
import { ProtectedRoute } from "@/features/auth/ProtectedRoute";
import { AppLayout } from "@/components/layout/AppLayout";
import { LandingPage } from "@/features/marketing/LandingPage";
import { LoginPage } from "@/features/auth/LoginPage";
import { DashboardPage } from "@/features/dashboard/DashboardPage";
import { DriversPage } from "@/features/drivers/DriversPage";
import { DriverDetailsPage } from "@/features/drivers/DriverDetailsPage";
import { PredictionPage } from "@/features/prediction/PredictionPage";
import { AnalyticsPage } from "@/features/analytics/AnalyticsPage";
import { ModelsPage } from "@/features/models/ModelsPage";
import { SettingsPage } from "@/features/settings/SettingsPage";
import { ProfilePage } from "@/features/settings/ProfilePage";
import { NotFoundPage } from "@/features/marketing/NotFoundPage";

export function App() {
  return (
    <Routes>
      {/* Public */}
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />

      {/* Authenticated app */}
      <Route element={<ProtectedRoute />}>
        <Route path="/app" element={<AppLayout />}>
          <Route index element={<DashboardPage />} />
          <Route path="drivers" element={<DriversPage />} />
          <Route path="drivers/:driverId" element={<DriverDetailsPage />} />
          <Route path="predict" element={<PredictionPage />} />
          <Route path="analytics" element={<AnalyticsPage />} />
          <Route path="models" element={<ModelsPage />} />
          <Route path="settings" element={<SettingsPage />} />
          <Route path="profile" element={<ProfilePage />} />
        </Route>
      </Route>

      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
