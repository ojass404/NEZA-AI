import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAppState } from '../../context/AppStateContext';
import { PriorityBadge, DemoBadge } from '../../components/common/Badges';
import { VerificationPanel } from './components/VerificationPanel';
import {
  MapPin,
  Ruler,
  Maximize,
  FileText,
  Map as MapIcon,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';

export const DetectionDetailsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { detections, setSelectedDetectionId } = useAppState();

  const currentId = id || 'DET-001';
  const detection = detections.find((d) => d.id === currentId) || detections[0];

  const currentIndex = detections.findIndex((d) => d.id === detection.id);
  const prevDetection = currentIndex > 0 ? detections[currentIndex - 1] : null;
  const nextDetection = currentIndex < detections.length - 1 ? detections[currentIndex + 1] : null;

  const navigateTo = (detId: string) => {
    setSelectedDetectionId(detId);
    navigate(`/detection/${detId}`);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-white/10">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/sonar-analysis')}
            className="p-1.5 rounded-lg text-white/40 hover:text-white hover:bg-white/8 border border-white/10 transition-colors"
            title="Back to Sonar Analysis"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl md:text-2xl font-extrabold text-white font-mono">
                {detection.id}
              </h1>
              <span className="text-base font-bold text-white/40">
                • {detection.classification}
              </span>
              <PriorityBadge priority={detection.priority} />
            </div>
            <p className="text-xs text-white/30 mt-0.5">
              Survey: <span className="text-white/60 font-medium">{detection.surveyName}</span>
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => prevDetection && navigateTo(prevDetection.id)}
            disabled={!prevDetection}
            className="px-3 py-1.5 rounded-lg text-xs font-mono text-white/60 bg-[#1e1e1e] border border-white/10 hover:border-white/20 disabled:opacity-40 transition-colors flex items-center gap-1"
          >
            <ChevronLeft className="w-3.5 h-3.5" /> Prev
          </button>
          <span className="text-xs font-mono text-white/30">
            {currentIndex + 1} / {detections.length}
          </span>
          <button
            onClick={() => nextDetection && navigateTo(nextDetection.id)}
            disabled={!nextDetection}
            className="px-3 py-1.5 rounded-lg text-xs font-mono text-white/60 bg-[#1e1e1e] border border-white/10 hover:border-white/20 disabled:opacity-40 transition-colors flex items-center gap-1"
          >
            Next <ChevronRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-7 space-y-4">
          <div className="bg-[#161616] border border-white/8 rounded-2xl p-4">
            <div className="flex items-center justify-between pb-3 border-b border-white/8 text-xs font-mono">
              <div className="flex items-center gap-2 text-white/50">
                <Maximize className="w-4 h-4 text-white/30" />
                <span className="font-bold">ACOUSTIC HIGH-RES CROP</span>
              </div>
              <span className="text-white/30">
                BOX: [{detection.bbox.join(', ')}] px
              </span>
            </div>

            <div className="relative rounded-xl overflow-hidden border border-white/10 bg-[#070D1D] my-3">
              <img
                src={detection.cropUrl || '/sonar-samples/crop-ghostnet.png'}
                alt={detection.classification}
                className="w-full h-[360px] object-cover"
              />

              <div className="absolute top-3 left-3 bg-black/70 backdrop-blur-xs border border-white/10 rounded-lg px-2.5 py-1 text-[11px] font-mono text-white/70 font-semibold">
                CLASSIFICATION: <strong className="text-white">{detection.classification}</strong>
              </div>

              <div className="absolute bottom-3 left-3 bg-black/70 backdrop-blur-xs border border-white/10 rounded-lg px-2.5 py-1 text-[11px] font-mono text-emerald-400 font-bold">
                AI CONFIDENCE: {Math.round(detection.confidence * 100)}%
              </div>

              <div className="absolute bottom-3 right-3 bg-black/70 backdrop-blur-xs border border-white/10 rounded-lg px-2.5 py-1 text-[11px] font-mono text-amber-400 font-semibold">
                SHADOW: {detection.acousticShadowLength || '2.1'} m
              </div>
            </div>

            <div className="flex items-center justify-between text-xs font-mono text-white/30 pt-1">
              <span>Sensor: EdgeTech 4200 (410 kHz)</span>
              <span>Slant-Range: {detection.sensorMetadata?.slantRangeMeters || 38.2} m</span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate('/marine-map')}
              className="flex-1 py-2.5 px-3 rounded-xl bg-[#161616] border border-white/10 hover:border-white/20 text-xs font-mono font-semibold text-white/60 flex items-center justify-center gap-2 transition-all"
            >
              <MapIcon className="w-4 h-4 text-white/40" />
              <span>Locate on Marine Map</span>
            </button>
            <button
              onClick={() => navigate('/reports')}
              className="flex-1 py-2.5 px-3 rounded-xl bg-[#161616] border border-white/10 hover:border-white/20 text-xs font-mono font-semibold text-white/60 flex items-center justify-center gap-2 transition-all"
            >
              <FileText className="w-4 h-4 text-amber-400" />
              <span>Generate Anomaly Dossier</span>
            </button>
          </div>
        </div>

        <div className="lg:col-span-5 space-y-5">
          <VerificationPanel detection={detection} />

          <div className="bg-[#161616] border border-white/8 rounded-2xl p-5 space-y-4">
            <div className="flex items-center justify-between pb-2.5 border-b border-white/8">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Ruler className="w-4 h-4 text-white/40" />
                Physical & Spatial Dimensions
              </h3>
              <DemoBadge text="PROTOTYPE METRICS" />
            </div>

            <div className="grid grid-cols-2 gap-3 text-xs font-mono">
              <div className="p-3 rounded-xl bg-[#1e1e1e] border border-white/8">
                <span className="text-[10px] text-white/30 uppercase block">Length × Width</span>
                <span className="font-bold text-white text-sm">
                  {detection.dimensions.length} m × {detection.dimensions.width} m
                </span>
              </div>

              <div className="p-3 rounded-xl bg-[#1e1e1e] border border-white/8">
                <span className="text-[10px] text-white/30 uppercase block">Acoustic Elevation (H)</span>
                <span className="font-bold text-amber-400 text-sm">
                  {detection.dimensions.height} m
                </span>
              </div>

              <div className="p-3 rounded-xl bg-[#1e1e1e] border border-white/8">
                <span className="text-[10px] text-white/30 uppercase block">Estimated Area</span>
                <span className="font-bold text-white text-sm">
                  {detection.estimatedArea || (detection.dimensions.length * detection.dimensions.width).toFixed(2)} m²
                </span>
              </div>

              <div className="p-3 rounded-xl bg-[#1e1e1e] border border-white/8">
                <span className="text-[10px] text-white/30 uppercase block">Sounding Depth</span>
                <span className="font-bold text-white text-sm">
                  {detection.depth || 18.4} m
                </span>
              </div>
            </div>

            <div className="pt-2 border-t border-white/8 space-y-2">
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="text-white/40 flex items-center gap-1.5">
                  <MapPin className="w-3.5 h-3.5 text-white/30" />
                  WGS84 Coordinates:
                </span>
                <DemoBadge text="DEMO COORDINATES" />
              </div>

              <div className="p-3 rounded-xl bg-[#1e1e1e] border border-white/8 font-mono text-xs flex justify-between">
                <span className="text-white/50">Lat: <strong className="text-white">{detection.latitude?.toFixed(4) || '9.1524'}° N</strong></span>
                <span className="text-white/50">Long: <strong className="text-white">{detection.longitude?.toFixed(4) || '79.1843'}° E</strong></span>
              </div>
            </div>

            <div className="pt-2 border-t border-white/8 space-y-1 text-[11px] font-mono text-white/30">
              <div className="flex justify-between">
                <span>Scan Parent:</span>
                <span className="text-white/60 font-bold">{detection.scanId}</span>
              </div>
              <div className="flex justify-between">
                <span>Detection Timestamp:</span>
                <span className="text-white/50">{detection.timestamp}</span>
              </div>
              <div className="flex justify-between">
                <span>Inference Pipeline:</span>
                <span className="text-white/60 font-semibold">YOLOv9-SSS (Dual-Band)</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
