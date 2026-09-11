import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Detection } from '../../../models/types';
import { PriorityBadge, VerificationBadge, ConfidenceBadge } from '../../../components/common/Badges';
import { ArrowRight, ChevronRight } from 'lucide-react';
import { useAppState } from '../../../context/AppStateContext';

interface PriorityReviewQueueProps {
  detections: Detection[];
}

export const PriorityReviewQueue: React.FC<PriorityReviewQueueProps> = ({ detections }) => {
  const navigate = useNavigate();
  const { setSelectedDetectionId, setSelectedScanId } = useAppState();

  const handleReview = (detection: Detection) => {
    setSelectedScanId(detection.scanId);
    setSelectedDetectionId(detection.id);
    navigate(`/detection/${detection.id}`);
  };

  return (
    <div className="bg-[#161616] border border-white/8 rounded-xl p-5">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-sm font-bold text-white flex items-center gap-2">
            Priority Review Queue
          </h2>
        </div>
        <button
          onClick={() => navigate('/detection/DET-001')}
          className="text-xs font-semibold text-white/50 hover:text-white flex items-center gap-1 transition-colors"
        >
          View all <ChevronRight className="w-3.5 h-3.5" />
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs font-sans">
          <thead>
            <tr className="border-b border-white/8 text-[10px] font-mono uppercase text-white/35">
              <th className="pb-2.5 font-semibold">Anomaly ID / Class</th>
              <th className="pb-2.5 font-semibold">Survey Source</th>
              <th className="pb-2.5 font-semibold">Confidence</th>
              <th className="pb-2.5 font-semibold">Priority</th>
              <th className="pb-2.5 font-semibold">Status</th>
              <th className="pb-2.5 font-semibold text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {detections.map((det) => (
              <tr
                key={det.id}
                onClick={() => handleReview(det)}
                className="hover:bg-white/4 transition-colors cursor-pointer group"
              >
                <td className="py-3">
                  <div className="flex flex-col">
                    <span className="font-mono font-bold text-white/70 group-hover:text-white transition-colors">
                      {det.id}
                    </span>
                    <span className="text-white/45 font-medium">
                      {det.classification}
                    </span>
                  </div>
                </td>
                <td className="py-3 text-white/45 max-w-[180px] truncate">
                  {det.surveyName}
                </td>
                <td className="py-3">
                  <ConfidenceBadge confidence={det.confidence} />
                </td>
                <td className="py-3">
                  <PriorityBadge priority={det.priority} />
                </td>
                <td className="py-3">
                  <VerificationBadge status={det.verificationStatus} />
                </td>
                <td className="py-3 text-right">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleReview(det);
                    }}
                    className="inline-flex items-center gap-1.5 px-3 py-1 bg-white text-black rounded-lg text-xs font-semibold hover:bg-white/90 transition-all"
                  >
                    <span>Review</span>
                    <ArrowRight className="w-3 h-3" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
