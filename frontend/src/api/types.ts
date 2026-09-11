// FastAPI contract types for prospective backend integration
export interface ApiDetectionDto {
  id: string;
  scan_id: string;
  classification: string;
  confidence: number;
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
  bbox: [number, number, number, number];
  latitude: number | null;
  longitude: number | null;
  depth?: number | null;
  dimensions?: {
    length?: number;
    width?: number;
    height?: number;
  };
  estimated_area?: number | null;
  verification_status: 'PENDING' | 'VERIFIED' | 'REJECTED';
  verification_note?: string;
}

export interface ApiScanResponse {
  scan_id: string;
  status: 'uploading' | 'processing' | 'completed' | 'failed';
  survey_name: string;
  detections: ApiDetectionDto[];
  progress?: number;
}

export interface ApiVerificationRequest {
  detection_id: string;
  status: 'VERIFIED' | 'REJECTED';
  note?: string;
  reviewer_name: string;
}
