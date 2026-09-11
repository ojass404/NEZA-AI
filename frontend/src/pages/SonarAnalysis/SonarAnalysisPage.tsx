import React, { useState } from 'react';
import { useAppState } from '../../context/AppStateContext';
import { UploadZone } from './components/UploadZone';
import { SonarViewer } from './components/SonarViewer';
import { DetectionList } from './components/DetectionList';
import { api } from '../../api/client';

const DEMO_OCEAN_POSITION = {
  latitude: '9.1558',
  longitude: '79.1891',
  label: 'Gulf of Mannar demo sector',
};

export const SonarAnalysisPage: React.FC = () => {
  const { scans, selectedScanId, detections, selectedDetectionId, setSelectedDetectionId,
    setSelectedScanId, refresh } = useAppState();
  const [isProcessing, setIsProcessing] = useState(false);
  const [latitude, setLatitude] = useState('');
  const [longitude, setLongitude] = useState('');
  const [mode, setMode] = useState('auto');
  const [metadataSource, setMetadataSource] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const activeScan = scans.find(s => s.id === selectedScanId);
  const activeDetections = detections.filter(d => d.scanId === activeScan?.id);
  const start = async (file: File) => {
    setError('');
    if ((latitude === '') !== (longitude === '')) { setError('Supply both GPS coordinates or leave both blank.'); return; }
    if (latitude && (!Number.isFinite(Number(latitude)) || Math.abs(Number(latitude)) > 90 || !Number.isFinite(Number(longitude)) || Math.abs(Number(longitude)) > 180)) { setError('Enter valid WGS84 coordinates.'); return; }
    setIsProcessing(true);
    try {
      setMessage('Uploading sonar image...');
      const data = new FormData(); data.append('file', file); data.append('survey_name', file.name);
      const uploaded = await api('/scans/upload', {method: 'POST', body: data});
      setSelectedScanId(uploaded.scan_id);
      const metadata = latitude === '' ? {} : {
        latitude: Number(latitude),
        longitude: Number(longitude),
        source: metadataSource || 'MANUAL_ENTRY',
      };
      await api(`/scans/${uploaded.scan_id}/metadata`, {method: 'POST', body: JSON.stringify(metadata)});
      setMessage('Processing sonar scan...');
      const result = await api(`/scans/${uploaded.scan_id}/process`, {method: 'POST', body: JSON.stringify({mode})});
      setMessage(result.detection_count ? `Processing complete — ${result.detection_count} detections found.` : 'No candidate anomalies detected.');
    } catch (e) { setError((e as Error).message); setMessage(''); }
    finally { await refresh(); setIsProcessing(false); }
  };
  return <div className="space-y-6 text-white">
    <h1 className="text-2xl font-bold">Sonar Analysis & Inspection</h1>
    <p className="text-white/60">Raw side-scan imagery · YOLOv8n · candidates require human review.</p>
    <div className="flex flex-wrap gap-4 p-4 bg-[#161616] rounded-xl">
      <label>Latitude (optional)<input aria-label="Latitude" type="number" min="-90" max="90" step="any" value={latitude} onChange={e => { setLatitude(e.target.value); setMetadataSource(e.target.value === DEMO_OCEAN_POSITION.latitude && longitude === DEMO_OCEAN_POSITION.longitude ? 'DEMO_OCEAN_COORDINATES' : ''); }} className="block bg-[#242424] p-2" disabled={isProcessing}/></label>
      <label>Longitude (optional)<input aria-label="Longitude" type="number" min="-180" max="180" step="any" value={longitude} onChange={e => { setLongitude(e.target.value); setMetadataSource(latitude === DEMO_OCEAN_POSITION.latitude && e.target.value === DEMO_OCEAN_POSITION.longitude ? 'DEMO_OCEAN_COORDINATES' : ''); }} className="block bg-[#242424] p-2" disabled={isProcessing}/></label>
      <button type="button" onClick={() => { setLatitude(DEMO_OCEAN_POSITION.latitude); setLongitude(DEMO_OCEAN_POSITION.longitude); setMetadataSource('DEMO_OCEAN_COORDINATES'); }} disabled={isProcessing} className="self-end bg-[#242424] px-3 py-2 rounded-lg border border-white/10 hover:border-white/30">
        Use ocean demo GPS
      </button>
      <label>Inference mode<select value={mode} onChange={e => setMode(e.target.value)} disabled={isProcessing} className="block bg-[#242424] p-2"><option value="auto">Auto (strip-aware)</option><option value="full_strip">Full sonar strip (0.05, tiled)</option><option value="standard">Object-centred crop (0.20)</option></select></label>
      {metadataSource === 'DEMO_OCEAN_COORDINATES' && <p className="basis-full text-xs text-white/50">Using {DEMO_OCEAN_POSITION.label}: {DEMO_OCEAN_POSITION.latitude}, {DEMO_OCEAN_POSITION.longitude}</p>}
    </div>
    <UploadZone onStartAnalysis={start} isProcessing={isProcessing}/>
    {message && <p role="status">{message}</p>}
    {error && <p role="alert" className="text-red-400">{error}</p>}
    {activeScan && <><select aria-label="Scan" value={selectedScanId} onChange={e => setSelectedScanId(e.target.value)} className="bg-[#242424] p-2">{scans.map(s => <option key={s.id} value={s.id}>{s.filename} — {s.status}</option>)}</select>
      {activeDetections.some(d => d.latitude === null) && <p>Detections generated, but geographic coordinates are unavailable for this scan.</p>}
      {activeDetections.some(d => d.latitude !== null) && <p>FRAME_LEVEL GPS associates candidates with the scan position; it is not an exact target location.</p>}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6"><div className="lg:col-span-2"><SonarViewer scan={activeScan} detections={activeDetections} selectedDetectionId={selectedDetectionId} onSelectDetection={setSelectedDetectionId}/></div><DetectionList detections={activeDetections} selectedDetectionId={selectedDetectionId} onSelectDetection={setSelectedDetectionId}/></div>
    </>}
  </div>;
};
