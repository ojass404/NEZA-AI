import React, { createContext, useContext, useState, useEffect } from 'react';
import { Detection, SonarScan, Report, UserProfile, SystemStatus, VerificationStatus } from '../models/types';
import { api, request } from '../api/client';
import { scanFromApi, detectionFromApi } from '../api/adapters';
import type { ApiScanResponse, ApiDetectionDto } from '../api/types';

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
  refresh: () => Promise<void>;
  error: string;
  geojson: any;
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
  generateReport: (scanId: string, title?: string) => Promise<Report>;
}

const AppStateContext = createContext<AppStateContextType | undefined>(undefined);

export const AppStateProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user] = useState<UserProfile>({ name: 'Local analyst', role: 'Reviewer', organization: 'NEZA AI', department: '', email: '', avatar: '', lastActive: '', surveysCompleted: 0, verificationsLogged: 0 });
  const [systemStatus, setSystemStatus] = useState<SystemStatus>({ engineStatus: 'OFFLINE', latencyMs: 0, activeSurveys: 0, storageUsedGb: 0, apiVersion: '1.0.0', modelIdentifier: 'YOLOv8n shipwreck' });
  const [scans, setScans] = useState<SonarScan[]>([]);
  const [detections, setDetections] = useState<Detection[]>([]);
  const [reports, setReports] = useState<Report[]>([]);
  const [selectedScanId, setSelectedScanId] = useState('');
  const [selectedDetectionId, setSelectedDetectionId] = useState<string | null>(null);
  const [toasts, setToasts] = useState<ToastMessage[]>([]);
  const [mapFilters, setMapFilters] = useState<MapFilters>({ survey: 'ALL', classification: 'ALL', priority: 'ALL', verification: 'ALL' });
  const [analyticsFilters, setAnalyticsFilters] = useState<AnalyticsFilters>({ survey: 'ALL', timeRange: '30D', classification: 'ALL', priority: 'ALL' });

  const addToast = (type: ToastMessage['type'], title: string, description?: string) => {
    const id = Math.random().toString(36).substring(2, 9);
    setToasts((prev) => [...prev, { id, type, title, description, timestamp: Date.now() }]);
    setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== id)), 4500);
  };

  const removeToast = (id: string) => setToasts((prev) => prev.filter((t) => t.id !== id));

  const [error, setError] = useState('');
  const [geojson, setGeojson] = useState<any>({ type: 'FeatureCollection', features: [] });
  const refresh = async () => {
    try {
      const rows = await api<ApiScanResponse[]>('/scans');
      const nextScans = rows.map(s => scanFromApi(s));
      const all = await Promise.all(nextScans.map(async scan => {
        const result = await api<{ detections: ApiDetectionDto[] }>(`/scans/${scan.id}/detections`);
        return result.detections.map(d => detectionFromApi(d, scan));
      }));
      setScans(previous => nextScans.map(scan => ({...scan, imageUrl: previous.find(s => s.id === scan.id)?.imageUrl || ''})));
      setDetections(all.flat());
      setSelectedScanId(current => current || nextScans[0]?.id || '');
      setGeojson(await api('/map/detections'));
      const deps = await api('/health/dependencies');
      setSystemStatus(prev => ({...prev, engineStatus: deps.database === 'healthy' && deps.ai_provider === 'configured' ? 'ONLINE' : 'DEGRADED', activeSurveys: rows.length}));
      setError('');
    } catch (e) { setError((e as Error).message); setSystemStatus(prev => ({...prev, engineStatus: 'OFFLINE'})); }
  };
  useEffect(() => { void refresh(); }, []);
  useEffect(() => {
    if (!selectedScanId) return;
    let active = true;
    let objectUrl = '';
    request(`/scans/${selectedScanId}/image`).then(response => response.blob()).then(blob => {
      objectUrl = URL.createObjectURL(blob);
      if (!active) { URL.revokeObjectURL(objectUrl); return; }
      setScans(prev => prev.map(scan => scan.id === selectedScanId ? {...scan, imageUrl: objectUrl} : scan));
      setDetections(prev => prev.map(d => d.scanId === selectedScanId ? {...d, cropUrl: objectUrl} : d));
    }).catch(e => { if (active) setError(e.message); });
    return () => { active = false; if (objectUrl) URL.revokeObjectURL(objectUrl); };
  }, [selectedScanId]);
  const verifyDetection = async (id: string, status: VerificationStatus, note?: string) => {
    try {
      await api(`/detections/${id}/verification`, {method: 'PATCH', body: JSON.stringify({verification_status: status, notes: note, verified_by: user.name})});
      await refresh();
      addToast('success', 'Verification saved', status);
    } catch (e) { addToast('error', 'Verification failed', (e as Error).message); }
  };

  const addNewScan = (newScan: SonarScan, newDetections: Detection[]) => {
    setScans((prev) => [newScan, ...prev]);
    setDetections((prev) => [...newDetections, ...prev]);
    setSelectedScanId(newScan.id);
    if (newDetections.length > 0) setSelectedDetectionId(newDetections[0].id);
    addToast('success', 'Survey Processed', `Generated ${newDetections.length} detections for ${newScan.id}.`);
  };

  const generateReport = async (scanId: string, title?: string): Promise<Report> => {
    const persisted = await api(`/scans/${scanId}/report/json`);
    const scan = scans.find((s) => s.id === scanId) ?? scans[0];
    const scanDets: Detection[] = persisted.detections.map((d: ApiDetectionDto) => detectionFromApi(d, scan));
    const now = new Date().toISOString().replace('T', ' ').substring(0, 19) + ' UTC';

    const newReport: Report = {
      id: `RPT-${String(reports.length + 1).padStart(3, '0')}`,
      scanId: scan.id,
      title: title ?? `Operational Anomaly Report — ${scan.surveyName}`,
      surveyName: scan.surveyName,
      organization: 'NEZA AI',
      department: 'Human review',
      generatedAt: now,
      generatedBy: user.name,
      detectionCount: scanDets.length,
      highPriorityCount: scanDets.filter((d) => d.priority === 'HIGH').length,
      verifiedCount: scanDets.filter((d) => d.verificationStatus === 'CONFIRMED').length,
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
      refresh, error, geojson, user, systemStatus, scans, detections, reports,
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
