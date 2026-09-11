import React from 'react';
import { AlertTriangle, X } from 'lucide-react';

interface ConfirmModalProps {
  isOpen: boolean;
  title: string;
  description: string;
  confirmLabel?: string;
  confirmVariant?: 'danger' | 'primary' | 'warning';
  onConfirm: () => void;
  onCancel: () => void;
  children?: React.ReactNode;
}

export const ConfirmModal: React.FC<ConfirmModalProps> = ({
  isOpen,
  title,
  description,
  confirmLabel = 'Confirm',
  confirmVariant = 'danger',
  onConfirm,
  onCancel,
  children,
}) => {
  if (!isOpen) return null;

  const btnColors = {
    danger: 'bg-red-600 hover:bg-red-700 text-white',
    warning: 'bg-white hover:bg-white/90 text-black font-bold',
    primary: 'bg-white hover:bg-white/90 text-black',
  }[confirmVariant];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-xs animate-fade-in">
      <div className="bg-[#161616] border border-white/10 rounded-xl max-w-md w-full p-5 shadow-2xl text-white relative">
        <button
          onClick={onCancel}
          className="absolute top-4 right-4 text-white/30 hover:text-white transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-3 mb-3">
          <div className="p-2 rounded-lg bg-red-500/10 text-red-400">
            <AlertTriangle className="w-5 h-5" />
          </div>
          <h3 className="text-base font-semibold text-white">{title}</h3>
        </div>

        <p className="text-xs text-white/50 leading-relaxed mb-4">
          {description}
        </p>

        {children && <div className="mb-4">{children}</div>}

        <div className="flex justify-end gap-2.5 pt-3 border-t border-white/8">
          <button
            type="button"
            onClick={onCancel}
            className="px-3.5 py-1.5 rounded-lg text-xs font-medium text-white/60 hover:bg-white/5 transition-colors border border-white/10"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={onConfirm}
            className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition-colors ${btnColors}`}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
};
