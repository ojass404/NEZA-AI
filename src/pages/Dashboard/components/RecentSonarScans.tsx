import React from 'react';
import { useNavigate } from 'react-router-dom';
import { SonarScan } from '../../../models/types';
import { ScanLine, ChevronRight, AlertTriangle, Layers } from 'lucide-react';
import { useAppState } from '../../../context/AppStateContext';

interface RecentSonarScansProps {
  scans: SonarScan[];
}

export const RecentSonarScans: React.FC<RecentSonarScansProps> = ({ scans }) => {
  const navigate = useNavigate();
  const { setSelectedScanId } = useAppState();

  const handleSelectScan = (scan: SonarScan) => {
    setSelectedScanId(scan.id);
    navigate('/sonar-analysis');
  };

  return (
    <div className="bg-[#161616] border border-white/8 rounded-xl p-5">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-sm font-bold text-white flex items-center gap-2">
            Recent Sonar Surveys
            <span className="text-xs text-white/35 font-normal">
              ({scans.length} Logged)
            </span>
          </h2>
        </div>
        <button
          onClick={() => navigate('/sonar-analysis')}
          className="text-xs font-semibold text-white/50 hover:text-white flex items-center gap-1 transition-colors"
        >
          View all <ChevronRight className="w-3.5 h-3.5" />
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
        {scans.map((scan) => (
          <div
            key={scan.id}
            onClick={() => handleSelectScan(scan)}
            className="p-3.5 bg-[#1a1a1a] border border-white/8 rounded-xl hover:border-white/20 hover:bg-[#1e1e1e] transition-all duration-150 cursor-pointer group"
          >
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center gap-2">
                <div className="p-1.5 rounded-lg bg-white/5 text-white/60 border border-white/10">
                  <ScanLine className="w-4 h-4" />
                </div>
                <div>
                  <span className="font-mono text-xs font-bold text-white/70 block group-hover:text-white transition-colors">
                    {scan.id}
                  </span>
                  <span className="text-[10px] text-white/35 font-mono">
                    {scan.uploadedAt}
                  </span>
                </div>
              </div>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-white/10 text-white/60 border border-white/10">
                {scan.status}
              </span>
            </div>

            <h3 className="text-xs font-bold text-white/80 mb-1.5 truncate">
              {scan.surveyName}
            </h3>

            <div className="flex items-center justify-between text-[11px] font-mono text-white/40 pt-2 border-t border-white/8">
              <span className="flex items-center gap-1">
                <Layers className="w-3 h-3 text-white/50" />
                {scan.detectionCount} detections
              </span>
              {scan.highPriorityCount > 0 && (
                <span className="flex items-center gap-1 text-white/60 font-semibold">
                  <AlertTriangle className="w-3 h-3 text-white/50" />
                  {scan.highPriorityCount} high priority
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
