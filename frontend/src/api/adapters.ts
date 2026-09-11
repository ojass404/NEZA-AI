import type { ApiDetectionDto, ApiScanResponse } from './types';
import type { SonarScan, Detection } from '../models/types';
export function scanFromApi(s: ApiScanResponse, imageUrl = ''): SonarScan {
  return { id: s.scan_id, filename: s.filename, surveyName: s.survey_name || s.filename,
    status: s.status, uploadedAt: s.created_at, detectionCount: s.detection_count,
    progress: s.status === 'COMPLETED' ? 100 : 0, highPriorityCount: 0,
    locationName: s.metadata?.latitude != null ? 'Frame GPS (approximate target location)' : 'Location unavailable',
    vesselName: s.metadata?.vehicle_id || 'Not supplied', instrument: 'Not supplied',
    frequencyKhz: null, altitudeMeters: s.metadata?.altitude_m ?? null,
    rangeMeters: s.metadata?.sonar_range_m ?? null,
    imageUrl, imageWidth: s.image_width || 1, imageHeight: s.image_height || 1 };
}
export function detectionFromApi(d: ApiDetectionDto, scan: SonarScan): Detection {
  return { id: d.id, scanId: d.scan_id, surveyName: scan.surveyName,
    classification: d.classification, confidence: d.confidence, priority: d.severity,
    bbox: [d.bbox.x_min, d.bbox.y_min, d.bbox.width, d.bbox.height],
    latitude: d.latitude, longitude: d.longitude, geotagMethod: d.geotagging_method,
    modelName: d.model_name, depth: null, dimensions: { length: null, width: null, height: null },
    estimatedArea: null, acousticShadowLength: null, verificationStatus: d.verification_status,
    verificationNote: d.verification_notes || undefined, verifiedBy: d.verified_by || undefined,
    verifiedAt: d.verified_at || undefined, timestamp: d.created_at, cropUrl: scan.imageUrl };
}
