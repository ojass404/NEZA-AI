import React from 'react';
import { LucideIcon, Compass } from 'lucide-react';

interface EmptyStateProps {
  title: string;
  description: string;
  icon?: LucideIcon;
  actionLabel?: string;
  onAction?: () => void;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title,
  description,
  icon: Icon = Compass,
  actionLabel,
  onAction,
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-10 text-center bg-white/3 border border-dashed border-white/10 rounded-xl">
      <div className="p-3 rounded-full bg-white/8 text-white/50 mb-3">
        <Icon className="w-7 h-7" />
      </div>
      <h3 className="text-sm font-semibold text-white mb-1">{title}</h3>
      <p className="text-xs text-white/40 max-w-sm mb-4 leading-relaxed">
        {description}
      </p>
      {actionLabel && onAction && (
        <button
          onClick={onAction}
          className="px-3.5 py-1.5 rounded-lg bg-white hover:bg-white/90 text-black text-xs font-medium transition-colors"
        >
          {actionLabel}
        </button>
      )}
    </div>
  );
};
