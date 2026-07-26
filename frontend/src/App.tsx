import { Route, Routes } from "react-router-dom";
import { ProtectedRoute } from "@/features/auth/ProtectedRoute";
import { RequireAdmin } from "@/features/auth/RequireAdmin";
import { AppLayout } from "@/components/layout/AppLayout";
import { LandingPage } from "@/features/marketing/LandingPage";
import { LoginPage } from "@/features/auth/LoginPage";
import { DashboardIndexRoute } from "@/features/dashboard/DashboardIndexRoute";
import { DriversPage } from "@/features/drivers/DriversPage";
import { DriverDetailsPage } from "@/features/drivers/DriverDetailsPage";
import { PredictionPage } from "@/features/prediction/PredictionPage";
import { AnalyticsPage } from "@/features/analytics/AnalyticsPage";
import { ModelsPage } from "@/features/models/ModelsPage";
import { SettingsPage } from "@/features/settings/SettingsPage";
import { ProfilePage } from "@/features/settings/ProfilePage";
import { UsersPage } from "@/features/admin/UsersPage";
import { NotFoundPage } from "@/features/marketing/NotFoundPage";
import { LegalIndexPage } from "@/features/legal/pages/LegalIndexPage";
import { TermsPage } from "@/features/legal/pages/TermsPage";
import { PrivacyPage } from "@/features/legal/pages/PrivacyPage";
import { DisclaimerPage } from "@/features/legal/pages/DisclaimerPage";

export function App() {
  return (
    <Routes>
      {/* Public */}
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/legal" element={<LegalIndexPage />} />
      <Route path="/legal/terms" element={<TermsPage />} />
      <Route path="/legal/privacy" element={<PrivacyPage />} />
      <Route path="/legal/disclaimer" element={<DisclaimerPage />} />

      {/* Authenticated app */}
      <Route element={<ProtectedRoute />}>
        <Route path="/app" element={<AppLayout />}>
          <Route index element={<DashboardIndexRoute />} />
          <Route path="drivers" element={<DriversPage />} />
          <Route path="drivers/:driverId" element={<DriverDetailsPage />} />
          <Route path="predict" element={<PredictionPage />} />
          <Route path="analytics" element={<AnalyticsPage />} />
          <Route path="models" element={<ModelsPage />} />
          <Route path="settings" element={<SettingsPage />} />
          <Route path="profile" element={<ProfilePage />} />
          <Route element={<RequireAdmin />}>
            <Route path="admin/users" element={<UsersPage />} />
          </Route>
        </Route>
      </Route>

      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
