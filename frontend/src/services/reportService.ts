import { api, downloadReport } from '../api/client';
export const reportService = { getReportById: (id: string) => api(`/scans/${id}/report/json`), downloadReport };
