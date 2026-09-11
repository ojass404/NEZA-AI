import React, { createContext, useContext, useState } from 'react';
import { Detection, SonarScan, Report, UserProfile, SystemStatus, VerificationStatus } from '../models/types';
import { INITIAL_USER, INITIAL_SYSTEM_STATUS, INITIAL_SCANS, INITIAL_DETECTIONS, INITIAL_REPORTS } from '../data/mockData';

export interface ToastMessage {
  id: string;
  type: 'success' | 'info' | 'warning' | 'error';
  title: string;
  description?: string;
  timestamp: number;
}

type MapFilters = { survey: string; classification: string; priority: string; verification: string };
type AnalyticsFilters = { survey: string; timeRange: string; classification: string; priority: string };

interface AppStateContextType {
  user: UserProfile;
  systemStatus: SystemStatus;
  scans: SonarScan[];
  detections: Detection[];
  reports: Report[];
  selectedScanId: string;
  selectedDetectionId: string | null;
  toasts: ToastMessage[];
  mapFilters: MapFilters;
  analyticsFilters: AnalyticsFilters;
  setSelectedScanId: (id: string) => void;
  setSelectedDetectionId: (id: string | null) => void;
  setMapFilters: React.Dispatch<React.SetStateAction<MapFilters>>;
  setAnalyticsFilters: React.Dispatch<React.SetStateAction<AnalyticsFilters>>;
  addToast: (type: ToastMessage['type'], title: string, description?: string) => void;
  removeToast: (id: string) => void;
  verifyDetection: (id: string, status: VerificationStatus, note?: string) => void;
  addNewScan: (scan: SonarScan, newDetections: Detection[]) => void;
  generateReport: (scanId: string, title?: string) => Report;
}

const AppStateContext = createContext<AppStateContextType | undefined>(undefined);

export const AppStateProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user] = useState<UserProfile>(INITIAL_USER);
  const [systemStatus] = useState<SystemStatus>(INITIAL_SYSTEM_STATUS);
  const [scans, setScans] = useState<SonarScan[]>(INITIAL_SCANS);
  const [detections, setDetections] = useState<Detection[]>(INITIAL_DETECTIONS);
  const [reports, setReports] = useState<Report[]>(INITIAL_REPORTS);
  const [selectedScanId, setSelectedScanId] = useState('SCAN-001');
  const [selectedDetectionId, setSelectedDetectionId] = useState<string | null>('DET-001');
  const [toasts, setToasts] = useState<ToastMessage[]>([]);
  const [mapFilters, setMapFilters] = useState<MapFilters>({ survey: 'ALL', classification: 'ALL', priority: 'ALL', verification: 'ALL' });
  const [analyticsFilters, setAnalyticsFilters] = useState<AnalyticsFilters>({ survey: 'ALL', timeRange: '30D', classification: 'ALL', priority: 'ALL' });

  const addToast = (type: ToastMessage['type'], title: string, description?: string) => {
    const id = Math.random().toString(36).substring(2, 9);
    setToasts((prev) => [...prev, { id, type, title, description, timestamp: Date.now() }]);
    setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== id)), 4500);
  };

  const removeToast = (id: string) => setToasts((prev) => prev.filter((t) => t.id !== id));

  const verifyDetection = (id: string, status: VerificationStatus, note?: string) => {
    setDetections((prev) =>
      prev.map((det) =>
        det.id !== id ? det : {
          ...det,
          verificationStatus: status,
          verificationNote: note ?? det.verificationNote,
          verifiedBy: status !== 'PENDING' ? user.name : undefined,
          verifiedAt: status !== 'PENDING' ? new Date().toISOString().replace('T', ' ').substring(0, 19) + ' UTC' : undefined,
        }
      )
    );

    // Update reports that reference the same scan
    const targetDet = detections.find((d) => d.id === id);
    if (targetDet) {
      setReports((prev) =>
        prev.map((r) => {
          if (r.scanId !== targetDet.scanId) return r;
          const scanDets = detections
            .map((d) => (d.id === id ? { ...d, verificationStatus: status } : d))
            .filter((d) => d.scanId === r.scanId);
          return {
            ...r,
            verifiedCount: scanDets.filter((d) => d.verificationStatus === 'VERIFIED').length,
            rejectedCount: scanDets.filter((d) => d.verificationStatus === 'REJECTED').length,
            pendingCount: scanDets.filter((d) => d.verificationStatus === 'PENDING').length,
          };
        })
      );
    }

    if (status === 'VERIFIED') addToast('success', 'Detection Verified', `Anomaly ${id} confirmed by ${user.name}.`);
    else if (status === 'REJECTED') addToast('warning', 'Detection Rejected', `Anomaly ${id} rejected (${note || 'Acoustic artifact'}).`);
    else addToast('info', 'Verification Reset', `Anomaly ${id} reset to pending.`);
  };

  const addNewScan = (newScan: SonarScan, newDetections: Detection[]) => {
    setScans((prev) => [newScan, ...prev]);
    setDetections((prev) => [...newDetections, ...prev]);
    setSelectedScanId(newScan.id);
    if (newDetections.length > 0) setSelectedDetectionId(newDetections[0].id);
    addToast('success', 'Survey Processed', `Generated ${newDetections.length} detections for ${newScan.id}.`);
  };

  const generateReport = (scanId: string, title?: string): Report => {
    const scan = scans.find((s) => s.id === scanId) ?? scans[0];
    const scanDets = detections.filter((d) => d.scanId === scanId);
    const now = new Date().toISOString().replace('T', ' ').substring(0, 19) + ' UTC';

    const newReport: Report = {
      id: `RPT-${String(reports.length + 1).padStart(3, '0')}`,
      scanId: scan.id,
      title: title ?? `Operational Anomaly Report — ${scan.surveyName}`,
      surveyName: scan.surveyName,
      organization: 'Ministry of Earth Sciences (MoES)',
      department: 'National Institute of Ocean Technology (NIOT)',
      generatedAt: now,
      generatedBy: user.name,
      detectionCount: scanDets.length,
      highPriorityCount: scanDets.filter((d) => d.priority === 'HIGH').length,
      verifiedCount: scanDets.filter((d) => d.verificationStatus === 'VERIFIED').length,
      rejectedCount: scanDets.filter((d) => d.verificationStatus === 'REJECTED').length,
      pendingCount: scanDets.filter((d) => d.verificationStatus === 'PENDING').length,
      status: 'READY',
      executiveSummary: `Automated hydrographic inspection for ${scan.surveyName}. Identified ${scanDets.length} seabed targets.`,
      targetDetections: scanDets.map((d) => d.id),
    };

    setReports((prev) => [newReport, ...prev]);
    addToast('success', 'Report Created', `Dossier ${newReport.id} generated.`);
    return newReport;
  };

  return (
    <AppStateContext.Provider value={{
      user, systemStatus, scans, detections, reports,
      selectedScanId, selectedDetectionId, toasts,
      mapFilters, analyticsFilters,
      setSelectedScanId, setSelectedDetectionId,
      setMapFilters, setAnalyticsFilters,
      addToast, removeToast,
      verifyDetection, addNewScan, generateReport,
    }}>
      {children}
    </AppStateContext.Provider>
  );
};

export const useAppState = () => {
  const context = useContext(AppStateContext);
  if (!context) throw new Error('useAppState must be used within an AppStateProvider');
  return context;
};
