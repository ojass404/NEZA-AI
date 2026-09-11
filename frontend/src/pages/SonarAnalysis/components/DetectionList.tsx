import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Detection } from '../../../models/types';
import { PriorityBadge, VerificationBadge, ConfidenceBadge } from '../../../components/common/Badges';
import { ArrowRight, Target } from 'lucide-react';
import { useAppState } from '../../../context/AppStateContext';

interface DetectionListProps {
  detections: Detection[];
  selectedDetectionId: string | null;
  onSelectDetection: (id: string) => void;
}

export const DetectionList: React.FC<DetectionListProps> = ({
  detections,
  selectedDetectionId,
  onSelectDetection,
}) => {
  const navigate = useNavigate();
  const { setSelectedDetectionId } = useAppState();

  const handleInspect = (det: Detection) => {
    setSelectedDetectionId(det.id);
    navigate(`/detection/${det.id}`);
  };

  return (
    <div className="bg-[#161616] border border-white/8 rounded-2xl p-4 flex flex-col h-[580px]">
      <div className="flex items-center justify-between pb-3 border-b border-white/8 shrink-0">
        <div>
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            Detected Objects
            <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-white/10 text-white/60 font-bold">
              {detections.length} TARGETS
            </span>
          </h3>
          <p className="text-[11px] text-white/40 mt-0.5">
            Click anomaly to highlight bounding box.
          </p>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto space-y-2 py-3 pr-1">
        {detections.map((det) => {
          const isSelected = det.id === selectedDetectionId;

          return (
            <div
              key={det.id}
              onClick={() => onSelectDetection(det.id)}
              className={`p-3 rounded-xl border transition-all duration-150 cursor-pointer ${
                isSelected
                  ? 'bg-white/8 border-white/30 scale-101'
                  : 'bg-white/3 border-white/8 hover:border-white/20 hover:bg-white/5'
              }`}
            >
              <div className="flex items-start justify-between gap-2 mb-1.5">
                <div className="flex items-center gap-1.5">
                  <Target className={`w-3.5 h-3.5 ${isSelected ? 'text-white' : 'text-white/30'}`} />
                  <span className="font-mono text-xs font-bold text-white/70">
                    {det.id}
                  </span>
                </div>
                <PriorityBadge priority={det.priority} />
              </div>

              <h4 className="text-xs font-bold text-white/80 mb-2">
                {det.classification}
              </h4>

              <div className="grid grid-cols-2 gap-2 text-[11px] font-mono text-white/40 mb-2.5">
                <div>
                  <span className="text-white/25 block text-[9px] uppercase">Confidence</span>
                  <ConfidenceBadge confidence={det.confidence} />
                </div>
                <div>
                  <span className="text-white/25 block text-[9px] uppercase">Status</span>
                  <VerificationBadge status={det.verificationStatus} />
                </div>
              </div>

              <div className="pt-2 border-t border-white/8 flex items-center justify-between">
                <span className="text-[10px] font-mono text-white/35">
                  {Math.round(det.bbox[2])} × {Math.round(det.bbox[3])} px
                </span>
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleInspect(det);
                  }}
                  className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-white text-black text-[11px] font-semibold hover:bg-white/90 transition-all"
                >
                  <span>Inspect</span>
                  <ArrowRight className="w-3 h-3" />
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
