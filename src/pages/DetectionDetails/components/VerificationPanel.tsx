import React, { useState } from 'react';
import { Detection } from '../../../models/types';
import { useAppState } from '../../../context/AppStateContext';
import { VerificationBadge } from '../../../components/common/Badges';
import { ConfirmModal } from '../../../components/common/ConfirmModal';
import {
  CheckCircle2,
  XCircle,
  Clock,
  RotateCcw,
  UserCheck,
} from 'lucide-react';

interface VerificationPanelProps {
  detection: Detection;
}

export const VerificationPanel: React.FC<VerificationPanelProps> = ({ detection }) => {
  const { verifyDetection, user } = useAppState();
  const [isRejectModalOpen, setIsRejectModalOpen] = useState(false);
  const [rejectReason, setRejectReason] = useState('Acoustic artifact');
  const [customNote, setCustomNote] = useState('');

  const handleAccept = () => {
    verifyDetection(detection.id, 'VERIFIED');
  };

  const handleConfirmReject = () => {
    const finalNote = customNote ? `${rejectReason}: ${customNote}` : rejectReason;
    verifyDetection(detection.id, 'REJECTED', finalNote);
    setIsRejectModalOpen(false);
    setCustomNote('');
  };

  const handleReset = () => {
    verifyDetection(detection.id, 'PENDING');
  };

  const isVerified = detection.verificationStatus === 'VERIFIED';
  const isRejected = detection.verificationStatus === 'REJECTED';
  const isPending = detection.verificationStatus === 'PENDING';

  return (
    <div className="bg-[#161616] border border-white/8 rounded-2xl p-5 space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-white/8">
        <div>
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <UserCheck className="w-4 h-4 text-white/60" />
            Human Verification
          </h3>
          <p className="text-xs text-white/40 mt-0.5">
            Confirm whether this represents a real underwater object/anomaly.
          </p>
        </div>
        <VerificationBadge status={detection.verificationStatus} />
      </div>

      {isVerified && (
        <div className="p-3.5 bg-white/5 border border-white/15 rounded-xl flex items-start gap-3 text-xs animate-fade-in">
          <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
          <div className="flex-1">
            <span className="font-bold text-white block font-mono">
              VERIFIED BY HUMAN REVIEWER
            </span>
            <p className="text-white/50 mt-0.5 leading-relaxed">
              Target confirmed by <strong className="text-white/80">{detection.verifiedBy || user.name}</strong> on {detection.verifiedAt || 'today'}.
            </p>
            {detection.verificationNote && (
              <div className="mt-2 pt-2 border-t border-white/10 text-white/40 font-mono text-[11px]">
                Note: {detection.verificationNote}
              </div>
            )}
          </div>
        </div>
      )}

      {isRejected && (
        <div className="p-3.5 bg-red-500/8 border border-red-500/20 rounded-xl flex items-start gap-3 text-xs animate-fade-in">
          <XCircle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
          <div className="flex-1">
            <span className="font-bold text-white block font-mono">
              REJECTED BY HUMAN REVIEWER
            </span>
            <p className="text-white/50 mt-0.5 leading-relaxed">
              Classified as false positive by {detection.verifiedBy || user.name}.
            </p>
            {detection.verificationNote && (
              <div className="mt-2 pt-2 border-t border-white/10 text-white/40 font-mono text-[11px]">
                Reason: {detection.verificationNote}
              </div>
            )}
          </div>
        </div>
      )}

      {isPending && (
        <div className="p-3.5 bg-white/4 border border-white/10 rounded-xl flex items-start gap-3 text-xs">
          <Clock className="w-5 h-5 text-white/40 shrink-0 mt-0.5" />
          <div>
            <span className="font-bold text-white block font-mono">
              PENDING VERIFICATION
            </span>
            <p className="text-white/50 mt-0.5 leading-relaxed">
              This detection has not yet been audited. Confirm or reject to update survey intelligence.
            </p>
          </div>
        </div>
      )}

      <div className="flex flex-wrap items-center gap-3 pt-2">
        <button
          type="button"
          onClick={handleAccept}
          className={`flex-1 py-2.5 px-4 rounded-xl text-xs font-bold font-mono flex items-center justify-center gap-2 transition-all shadow-sm hover:scale-102 ${
            isVerified
              ? 'bg-emerald-600 text-white cursor-default'
              : 'bg-emerald-600 hover:bg-emerald-700 text-white'
          }`}
        >
          <CheckCircle2 className="w-4 h-4" />
          <span>Accept Detection</span>
        </button>

        <button
          type="button"
          onClick={() => setIsRejectModalOpen(true)}
          className={`flex-1 py-2.5 px-4 rounded-xl text-xs font-bold font-mono flex items-center justify-center gap-2 transition-all shadow-sm hover:scale-102 ${
            isRejected
              ? 'bg-red-600 text-white cursor-default'
              : 'bg-red-600 hover:bg-red-700 text-white'
          }`}
        >
          <XCircle className="w-4 h-4" />
          <span>Reject Detection</span>
        </button>

        {!isPending && (
          <button
            type="button"
            onClick={handleReset}
            className="px-3 py-2.5 rounded-xl text-xs font-mono text-white/50 hover:bg-white/5 border border-white/10 transition-colors flex items-center gap-1.5"
            title="Reset to Pending"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset</span>
          </button>
        )}
      </div>

      <ConfirmModal
        isOpen={isRejectModalOpen}
        title="Reject AI Detection"
        description="Mark this AI detection as a false positive in survey telemetry and exclude it from hazardous target recovery queues."
        confirmLabel="Reject Anomaly"
        confirmVariant="danger"
        onConfirm={handleConfirmReject}
        onCancel={() => setIsRejectModalOpen(false)}
      >
        <div className="space-y-3 text-left">
          <label className="block text-xs font-medium text-white/50 font-mono">
            Rejection Classification:
          </label>
          <select
            value={rejectReason}
            onChange={(e) => setRejectReason(e.target.value)}
            className="w-full bg-[#1e1e1e] border border-white/10 rounded-lg p-2 text-xs text-white/80 focus:outline-hidden focus:border-white/20"
          >
            <option value="Acoustic artifact">Acoustic backscatter artifact / speckle</option>
            <option value="Natural rock formation">Natural rock formation / coral reef</option>
            <option value="Towfish surface reflection">Towfish surface reflection</option>
            <option value="Biological school">Biological school</option>
            <option value="Other">Other reason</option>
          </select>

          <label className="block text-xs font-medium text-white/50 font-mono">
            Analyst Audit Note (Optional):
          </label>
          <textarea
            value={customNote}
            onChange={(e) => setCustomNote(e.target.value)}
            placeholder="Add detailed observation rationale..."
            rows={2}
            className="w-full bg-[#1e1e1e] border border-white/10 rounded-lg p-2 text-xs text-white/80 placeholder-white/20 focus:outline-hidden focus:border-white/20"
          />
        </div>
      </ConfirmModal>
    </div>
  );
};
