import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AppShell } from './layouts/AppShell';
import { DashboardPage } from './pages/Dashboard/DashboardPage';
import { SonarAnalysisPage } from './pages/SonarAnalysis/SonarAnalysisPage';
import { DetectionDetailsPage } from './pages/DetectionDetails/DetectionDetailsPage';
import { MarineMapPage } from './pages/MarineMap/MarineMapPage';
import { AnalyticsPage } from './pages/Analytics/AnalyticsPage';
import { ReportsPage } from './pages/Reports/ReportsPage';
import { ProfilePage } from './pages/Profile/ProfilePage';
import { SettingsPage } from './pages/Settings/SettingsPage';
import { LoginPage } from './pages/Login/LoginPage';

export const AppRoutes: React.FC = () => {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />

      {/* Main Core 6-Screen Architecture wrapped in AppShell */}
      <Route element={<AppShell />}>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/sonar-analysis" element={<SonarAnalysisPage />} />
        <Route path="/detection/:id" element={<DetectionDetailsPage />} />
        <Route path="/detection" element={<Navigate to="/detection/DET-001" replace />} />
        <Route path="/marine-map" element={<MarineMapPage />} />
        <Route path="/analytics" element={<AnalyticsPage />} />
        <Route path="/reports" element={<ReportsPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Route>

      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
};
