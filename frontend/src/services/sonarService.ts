import { SonarScan, ProcessingStage } from '../models/types';
import { INITIAL_SCANS } from '../data/mockData';

export interface SonarServiceInterface {
  getScans(): Promise<SonarScan[]>;
  getScanById(id: string): Promise<SonarScan | null>;
  simulateProcessing(
    filename: string,
    fileSize: number,
    imageUrl: string | undefined,
    imageSize: { width: number; height: number } | undefined,
    onProgress: (stage: ProcessingStage, overallProgress: number) => void
  ): Promise<SonarScan>;
}

export class MockSonarService implements SonarServiceInterface {
  private scans: SonarScan[] = [...INITIAL_SCANS];

  async getScans(): Promise<SonarScan[]> {
    // Simulated network delay
    return new Promise((resolve) => setTimeout(() => resolve([...this.scans]), 150));
  }

  async getScanById(id: string): Promise<SonarScan | null> {
    const scan = this.scans.find((s) => s.id === id);
    return scan ? { ...scan } : null;
  }

  async simulateProcessing(
    filename: string,
    fileSize: number,
    imageUrl: string | undefined,
    imageSize: { width: number; height: number } | undefined,
    onProgress: (stage: ProcessingStage, overallProgress: number) => void
  ): Promise<SonarScan> {
    const stages: Omit<ProcessingStage, 'status'>[] = [
      { id: 'stg-1', name: 'Sonar Swath Data Ingestion', detail: `Validating acoustic file headers (${(fileSize / (1024 * 1024)).toFixed(1)} MB)...` },
      { id: 'stg-2', name: 'Nadir & Slant-Range Correction', detail: 'Equalizing water-column acoustic backscatter & time-varied gain...' },
      { id: 'stg-3', name: 'Deep Learning Anomaly Inference', detail: 'Running NEZA shipwreck detector weights...' },
      { id: 'stg-4', name: 'Acoustic Shadow & Dimension Analysis', detail: 'Calculating object elevation, length, and shadow extrapolation...' },
      { id: 'stg-5', name: 'WGS84 Georeferencing & Bathymetry Link', detail: 'Linking GNSS towfish position and sounding depth coordinates...' },
    ];

    for (let i = 0; i < stages.length; i++) {
      const stage = stages[i];
      // Set stage active
      onProgress({ ...stage, status: 'active' }, Math.round(((i) / stages.length) * 100));
      await new Promise((res) => setTimeout(res, 600));

      // Set stage completed
      onProgress({ ...stage, status: 'completed' }, Math.round(((i + 1) / stages.length) * 100));
      await new Promise((res) => setTimeout(res, 150));
    }

    const newScan: SonarScan = {
      id: `SCAN-${String(this.scans.length + 1).padStart(3, '0')}`,
      filename,
      surveyName: `Live Analysis: ${filename.replace(/\.[^/.]+$/, '')}`,
      locationName: 'Simulated Survey Transect (MoES / NIOT Protocol)',
      vesselName: 'CRV Sagar Nidhi (Virtual)',
      instrument: 'EdgeTech 4200 Dual-Frequency Sonar',
      frequencyKhz: 410,
      altitudeMeters: 14.0,
      rangeMeters: 80,
      uploadedAt: new Date().toISOString().replace('T', ' ').substring(0, 19) + ' UTC',
      status: 'COMPLETED',
      progress: 100,
      detectionCount: 2,
      highPriorityCount: 2,
      imageUrl: imageUrl || '/sonar-samples/scan-coastal-alpha.png',
      imageWidth: imageSize?.width || 1600,
      imageHeight: imageSize?.height || 900,
    };

    this.scans.unshift(newScan);
    return newScan;
  }
}

export const sonarService = new MockSonarService();
