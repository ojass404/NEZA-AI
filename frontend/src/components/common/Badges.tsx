import React from 'react';
import { PriorityLevel, VerificationStatus } from '../../models/types';
import { AlertCircle, CheckCircle2, Clock, XCircle, ShieldAlert } from 'lucide-react';

export const PriorityBadge: React.FC<{ priority: PriorityLevel; showIcon?: boolean }> = ({
  priority,
  showIcon = true,
}) => {
  const styles = {
    HIGH: 'bg-amber-500/15 text-amber-400 border-amber-500/30',
    MEDIUM: 'bg-amber-500/10 text-amber-300/80 border-amber-500/20',
    LOW: 'bg-white/5 text-white/50 border-white/10',
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-md text-xs font-mono font-semibold border ${styles[priority]}`}
    >
      {showIcon && priority === 'HIGH' && <AlertCircle className="w-3.5 h-3.5 text-amber-400" />}
      {priority}
    </span>
  );
};

export const VerificationBadge: React.FC<{ status: VerificationStatus }> = ({ status }) => {
  if (status === 'VERIFIED') {
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md text-xs font-mono font-semibold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
        VERIFIED
      </span>
    );
  }
  if (status === 'REJECTED') {
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md text-xs font-mono font-semibold bg-red-500/15 text-red-400 border border-red-500/30">
        <XCircle className="w-3.5 h-3.5 text-red-400" />
        REJECTED
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md text-xs font-mono font-semibold bg-amber-500/10 text-amber-300 border border-amber-500/20">
      <Clock className="w-3.5 h-3.5 text-amber-400" />
      PENDING
    </span>
  );
};

export const ConfidenceBadge: React.FC<{ confidence: number }> = ({ confidence }) => {
  const pct = Math.round(confidence * 100);
  const barColor = pct >= 90 ? 'bg-white' : pct >= 80 ? 'bg-white/70' : 'bg-white/40';
  const textColor = pct >= 90 ? 'text-white' : pct >= 80 ? 'text-white/70' : 'text-white/50';

  return (
    <div className="inline-flex items-center gap-2 font-mono text-xs">
      <div className="w-16 h-2 bg-white/10 rounded-full overflow-hidden">
        <div className={`h-full ${barColor} rounded-full`} style={{ width: `${pct}%` }} />
      </div>
      <span className={`font-bold ${textColor}`}>{pct}%</span>
    </div>
  );
};

export const DemoBadge: React.FC<{ text?: string }> = ({ text = 'SIMULATED PROCESSING' }) => (
  <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-white/5 text-white/40 border border-white/10 text-[10px] font-mono tracking-wider font-semibold uppercase">
    <ShieldAlert className="w-3 h-3 text-amber-400" />
    {text}
  </span>
);
