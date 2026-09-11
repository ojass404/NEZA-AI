export interface ApiDetectionDto {
  id: string; scan_id: string; classification: 'possible_shipwreck'; model_class: 'shipwreck';
  class_id: number; confidence: number; confidence_percent: number;
  bbox: { x_min: number; y_min: number; x_max: number; y_max: number; width: number; height: number };
  image_width: number; image_height: number;
  latitude: number | null; longitude: number | null;
  geotagging_method: 'FRAME_LEVEL' | 'UNAVAILABLE';
  severity: 'HIGH' | 'MEDIUM' | 'LOW';
  verification_status: 'PENDING' | 'CONFIRMED' | 'REJECTED';
  verification_notes: string | null; verified_by: string | null; verified_at: string | null;
  model_name: string; model_version: string | null; created_at: string;
}
export interface ApiScanResponse {
  scan_id: string; filename: string; status: 'UPLOADED' | 'PROCESSING' | 'COMPLETED' | 'FAILED';
  survey_name: string | null; image_width: number | null; image_height: number | null;
  detection_count: number; created_at: string; error_message: string | null;
  metadata: { latitude: number | null; longitude: number | null; depth_m?: number; altitude_m?: number; sonar_range_m?: number; vehicle_id?: string } | null;
}
