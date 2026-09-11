import React, { useState } from 'react';
import { useAppState } from '../../context/AppStateContext';
import { UploadZone } from './components/UploadZone';
import { ProcessingTimeline } from './components/ProcessingTimeline';
import { SonarViewer } from './components/SonarViewer';
import { DetectionList } from './components/DetectionList';
import { sonarService } from '../../services/sonarService';
import { ProcessingStage, Detection } from '../../models/types';
import { DemoBadge } from '../../components/common/Badges';

export const SonarAnalysisPage: React.FC = () => {
  const {
    scans,
    selectedScanId,
    detections,
    selectedDetectionId,
    setSelectedDetectionId,
    addNewScan,
  } = useAppState();

  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [stages, setStages] = useState<ProcessingStage[]>([
    { id: 'stg-1', name: 'Sonar Swath Data Ingestion', status: 'pending', detail: 'Validating acoustic file headers...' },
    { id: 'stg-2', name: 'Nadir & Slant-Range Correction', status: 'pending', detail: 'Equalizing water-column backscatter...' },
    { id: 'stg-3', name: 'Deep Learning Anomaly Inference', status: 'pending', detail: 'Running NEZA YOLOv9-SSS model...' },
    { id: 'stg-4', name: 'Acoustic Shadow & Dimension Analysis', status: 'pending', detail: 'Extrapolating shadow length...' },
    { id: 'stg-5', name: 'WGS84 Georeferencing & Bathymetry Link', status: 'pending', detail: 'Linking GNSS coordinates...' },
  ]);
  const [progress, setProgress] = useState<number>(0);
  const [elapsed, setElapsed] = useState<number>(0);

  const activeScan = scans.find((s) => s.id === selectedScanId) || scans[0];
  const activeDetections = detections.filter((d) => d.scanId === activeScan.id);

  const handleStartAnalysis = async (file: { name: string; size: number; type: string }) => {
    setIsProcessing(true);
    setProgress(0);
    setElapsed(0);

    const timer = setInterval(() => {
      setElapsed((prev) => prev + 1);
    }, 1000);

    try {
      const resultScan = await sonarService.simulateProcessing(
        file.name,
        file.size,
        (currentStage, overallPct) => {
          setStages((prev) =>
            prev.map((s) => (s.id === currentStage.id ? { ...s, status: currentStage.status, detail: currentStage.detail } : s))
          );
          setProgress(overallPct);
        }
      );

      const newDetections: Detection[] = [
        {
          id: `DET-${Math.floor(100 + Math.random() * 900)}`,
          scanId: resultScan.id,
          surveyName: resultScan.surveyName,
          classification: 'Ghost Net / Nylon Gillnet',
          confidence: 0.94,
          priority: 'HIGH',
          bbox: [350, 220, 260, 170],
          latitude: 9.1721,
          longitude: 79.2084,
          depth: 21.0,
          dimensions: { length: 4.6, width: 2.3, height: 1.1 },
          estimatedArea: 10.58,
          acousticShadowLength: 2.8,
          verificationStatus: 'PENDING',
          timestamp: new Date().toISOString().replace('T', ' ').substring(0, 19) + ' UTC',
        },
        {
          id: `DET-${Math.floor(100 + Math.random() * 900)}`,
          scanId: resultScan.id,
          surveyName: resultScan.surveyName,
          classification: 'Metal Debris / Industrial Container',
          confidence: 0.88,
          priority: 'HIGH',
          bbox: [820, 360, 200, 140],
          latitude: 9.1765,
          longitude: 79.2132,
          depth: 23.4,
          dimensions: { length: 3.1, width: 1.8, height: 1.2 },
          estimatedArea: 5.58,
          acousticShadowLength: 3.2,
          verificationStatus: 'PENDING',
          timestamp: new Date().toISOString().replace('T', ' ').substring(0, 19) + ' UTC',
        },
      ];

      addNewScan(resultScan, newDetections);
    } finally {
      clearInterval(timer);
      setIsProcessing(false);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-white/10">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl md:text-2xl font-extrabold text-white tracking-tight">
              Sonar Analysis & Inspection
            </h1>

          </div>
          <p className="text-xs md:text-sm text-white/40 mt-0.5">
            Upload Side-Scan Sonar imagery or survey logs for automated anomaly detection
          </p>
        </div>
      </div>

      <UploadZone onStartAnalysis={handleStartAnalysis} isProcessing={isProcessing} />

      {(isProcessing || progress > 0) && (
        <ProcessingTimeline
          stages={stages}
          currentProgress={progress}
          elapsedSeconds={elapsed}
          onCancel={() => setIsProcessing(false)}
        />
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <SonarViewer
            scan={activeScan}
            detections={activeDetections}
            selectedDetectionId={selectedDetectionId}
            onSelectDetection={setSelectedDetectionId}
          />
        </div>
        <div className="lg:col-span-1">
          <DetectionList
            detections={activeDetections}
            selectedDetectionId={selectedDetectionId}
            onSelectDetection={setSelectedDetectionId}
          />
        </div>
      </div>
    </div>
  );
};
