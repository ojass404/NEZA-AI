export type PriorityLevel = 'HIGH' | 'MEDIUM' | 'LOW';
export type VerificationStatus = 'PENDING' | 'VERIFIED' | 'REJECTED';
export type ScanStatus = 'UPLOADING' | 'PROCESSING' | 'COMPLETED' | 'FAILED';

export interface Detection {
  id: string;
  scanId: string;
  surveyName: string;
  classification: string;
  modelName?: string;
  confidence: number; // 0 to 1, e.g. 0.92
  priority: PriorityLevel;
  bbox: [number, number, number, number]; // [x, y, width, height] in pixel coordinates
  latitude: number | null; // Demo coordinates
  longitude: number | null; // Demo coordinates
  depth: number | null; // meters
  dimensions: {
    length: number; // meters
    width: number; // meters
    height: number; // acoustic shadow height in meters
  };
  estimatedArea: number | null; // sq meters
  acousticShadowLength: number | null; // meters
  verificationStatus: VerificationStatus;
  verificationNote?: string;
  verifiedBy?: string;
  verifiedAt?: string;
  timestamp: string;
  cropUrl?: string;
  sensorMetadata?: {
    slantRangeMeters?: number;
    beamFrequencyKhz?: number;
    altitudeMeters?: number;
    towfishHeading?: number;
  };
}

export interface SonarScan {
  id: string;
  filename: string;
  surveyName: string;
  locationName: string;
  vesselName: string;
  instrument: string;
  frequencyKhz: number;
  altitudeMeters: number;
  rangeMeters: number;
  uploadedAt: string;
  status: ScanStatus;
  progress: number;
  detectionCount: number;
  highPriorityCount: number;
  imageUrl: string;
  imageWidth: number;
  imageHeight: number;
}

export interface Report {
  id: string;
  scanId: string;
  title: string;
  surveyName: string;
  organization: string;
  department: string;
  generatedAt: string;
  generatedBy: string;
  detectionCount: number;
  highPriorityCount: number;
  verifiedCount: number;
  rejectedCount: number;
  pendingCount: number;
  status: 'READY' | 'DRAFT' | 'ARCHIVED';
  executiveSummary: string;
  targetDetections: string[]; // Detection IDs
}

export interface ProcessingStage {
  id: string;
  name: string;
  status: 'pending' | 'active' | 'completed' | 'error';
  detail: string;
  durationMs?: number;
}

export interface UserProfile {
  name: string;
  role: string;
  organization: string;
  department: string;
  email: string;
  avatar: string;
  lastActive: string;
  surveysCompleted: number;
  verificationsLogged: number;
}

export interface SystemStatus {
  engineStatus: 'ONLINE' | 'DEGRADED' | 'OFFLINE';
  latencyMs: number;
  activeSurveys: number;
  storageUsedGb: number;
  apiVersion: string;
  modelIdentifier: string;
}
