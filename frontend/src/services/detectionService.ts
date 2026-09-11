import { api } from '../api/client';
export const detectionService = { getDetectionsByScanId: (id: string) => api(`/scans/${id}/detections`) };
