const BASE = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000').replace(/\/$/, '');
let key = '';
export function setApiKey(value: string) { key = value; }
export async function request(path: string, options: RequestInit = {}): Promise<Response> {
  const headers = new Headers(options.headers);
  if (key) headers.set('Authorization', `Bearer ${key}`);
  if (options.body && !(options.body instanceof FormData)) headers.set('Content-Type', 'application/json');
  const response = await fetch(`${BASE}/api/v1${path}`, { ...options, headers, signal: options.signal || AbortSignal.timeout(600000) });
  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    throw new Error(payload?.detail?.message || payload?.detail || `API request failed (${response.status})`);
  }
  return response;
}
export async function api<T = any>(path: string, options: RequestInit = {}): Promise<T> {
  return (await request(path, options)).json();
}
export async function downloadReport(id: string, kind: 'json' | 'csv' | 'geojson') {
  const path = kind === 'json' ? `/scans/${id}/report/download.json` : `/scans/${id}/report/${kind}`;
  const blob = await (await request(path)).blob();
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url; anchor.download = `neza-${id}.${kind}`;
  document.body.appendChild(anchor); anchor.click(); anchor.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
