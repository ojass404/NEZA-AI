import React from 'react';
import { ProcessingStage } from '../../../models/types';
import { CheckCircle2, RefreshCw, Clock, XCircle } from 'lucide-react';
import { DemoBadge } from '../../../components/common/Badges';

interface ProcessingTimelineProps {
  stages: ProcessingStage[];
  currentProgress: number;
  elapsedSeconds: number;
  onCancel?: () => void;
  onRetry?: () => void;
}

export const ProcessingTimeline: React.FC<ProcessingTimelineProps> = ({
  stages,
  currentProgress,
  elapsedSeconds,
  onCancel,
  onRetry,
}) => {
  return (
    <div className="bg-[#161616] border border-white/8 rounded-2xl p-5 space-y-4 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-white/8">
        <div className="flex items-center gap-2">
          <h3 className="text-sm font-bold text-white">
            Acoustic Processing Pipeline
          </h3>
          <DemoBadge text="SIMULATED PROCESSING" />
        </div>
        <div className="flex items-center gap-3 text-xs font-mono text-white/40">
          <span>Elapsed: {elapsedSeconds}s</span>
          <span>•</span>
          <span className="font-bold text-white">{currentProgress}%</span>
        </div>
      </div>

      <div className="w-full h-2.5 bg-white/8 rounded-full overflow-hidden border border-white/8">
        <div
          className="h-full bg-gradient-to-r from-white/60 to-white transition-all duration-300 ease-out"
          style={{ width: `${currentProgress}%` }}
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-5 gap-3 pt-2">
        {stages.map((stg, index) => {
          const isCompleted = stg.status === 'completed';
          const isActive = stg.status === 'active';
          const isPending = stg.status === 'pending';
          const isError = stg.status === 'error';

          return (
            <div
              key={stg.id}
              className={`p-3 rounded-xl border transition-all ${
                isActive
                  ? 'bg-white/8 border-white/30'
                  : isCompleted
                  ? 'bg-white/5 border-white/15'
                  : 'bg-white/3 border-white/8 opacity-60'
              }`}
            >
              <div className="flex items-center gap-2 mb-1.5">
                {isCompleted && <CheckCircle2 className="w-4 h-4 text-white/70 shrink-0" />}
                {isActive && <RefreshCw className="w-4 h-4 text-white animate-spin shrink-0" />}
                {isPending && <Clock className="w-4 h-4 text-white/30 shrink-0" />}
                {isError && <XCircle className="w-4 h-4 text-red-400 shrink-0" />}

                <span className="text-[10px] font-mono font-bold text-white/30 uppercase">
                  Stage 0{index + 1}
                </span>
              </div>

              <h4 className={`text-xs font-bold leading-snug mb-1 ${
                isActive ? 'text-white' : isCompleted ? 'text-white/70' : 'text-white/35'
              }`}>
                {stg.name}
              </h4>

              <p className="text-[10px] text-white/35 leading-tight">
                {stg.detail}
              </p>
            </div>
          );
        })}
      </div>

      <div className="flex items-center justify-between pt-2 border-t border-white/8 text-xs font-mono">
        <span className="text-[11px] text-white/30">
          Inference Engine: YOLOv8n shipwreck
        </span>
        <div className="flex items-center gap-2">
          {onRetry && (
            <button onClick={onRetry} className="px-2.5 py-1 text-xs text-white/50 font-semibold hover:text-white transition-colors">
              Retry
            </button>
          )}
          {onCancel && (
            <button onClick={onCancel} className="px-2.5 py-1 text-xs text-red-400 font-semibold hover:underline">
              Cancel
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
