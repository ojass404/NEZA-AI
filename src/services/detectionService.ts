import { Detection, VerificationStatus } from '../models/types';
import { INITIAL_DETECTIONS } from '../data/mockData';

export interface DetectionServiceInterface {
  getDetections(): Promise<Detection[]>;
  getDetectionsByScanId(scanId: string): Promise<Detection[]>;
  getDetectionById(id: string): Promise<Detection | null>;
  verifyDetection(
    id: string,
    status: VerificationStatus,
    note?: string,
    verifiedBy?: string
  ): Promise<Detection>;
}

export class MockDetectionService implements DetectionServiceInterface {
  private detections: Detection[] = [...INITIAL_DETECTIONS];

  async getDetections(): Promise<Detection[]> {
    return new Promise((resolve) => setTimeout(() => resolve([...this.detections]), 100));
  }

  async getDetectionsByScanId(scanId: string): Promise<Detection[]> {
    const list = this.detections.filter((d) => d.scanId === scanId);
    return [...list];
  }

  async getDetectionById(id: string): Promise<Detection | null> {
    const d = this.detections.find((item) => item.id === id);
    return d ? { ...d } : null;
  }

  async verifyDetection(
    id: string,
    status: VerificationStatus,
    note?: string,
    verifiedBy: string = 'Dr. R. Ramanathan'
  ): Promise<Detection> {
    const idx = this.detections.findIndex((d) => d.id === id);
    if (idx === -1) {
      throw new Error(`Detection with id ${id} not found`);
    }

    const updated: Detection = {
      ...this.detections[idx],
      verificationStatus: status,
      verificationNote: note || this.detections[idx].verificationNote,
      verifiedBy: status !== 'PENDING' ? verifiedBy : undefined,
      verifiedAt: status !== 'PENDING' ? new Date().toISOString().replace('T', ' ').substring(0, 19) + ' UTC' : undefined,
    };

    this.detections[idx] = updated;
    return { ...updated };
  }
}

export const detectionService = new MockDetectionService();
