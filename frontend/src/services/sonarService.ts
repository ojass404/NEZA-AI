import { api } from '../api/client';
export const sonarService = { getScans: () => api('/scans'), getScanById: (id: string) => api(`/scans/${id}`) };
