import React from 'react';
import { LucideIcon } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: LucideIcon;
  accentColor?: 'buttercup' | 'cobalt' | 'gold' | 'royal';
  trend?: {
    label: string;
    isPositive?: boolean;
  };
  onClick?: () => void;
  className?: string;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  accentColor = 'cobalt',
  trend,
  onClick,
  className = '',
}) => {
  const borderClasses = {
    buttercup: 'border-t-2 border-t-white/50',
    cobalt: 'border-t-2 border-t-white/30',
    gold: 'border-t-2 border-t-white/40',
    royal: 'border-t-2 border-t-white/20',
  };

  const iconBgClasses = {
    buttercup: 'bg-white/8 text-white/70 border border-white/15',
    cobalt: 'bg-white/5 text-white/60 border border-white/10',
    gold: 'bg-white/8 text-white/60 border border-white/12',
    royal: 'bg-white/5 text-white/40 border border-white/10',
  };

  return (
    <div
      onClick={onClick}
      className={`bg-[#161616] border border-white/8 rounded-xl p-4 hover:border-white/15 transition-all duration-200 hover:-translate-y-0.5 ${borderClasses[accentColor]} ${
        onClick ? 'cursor-pointer' : ''
      } ${className}`}
    >
      <div className="flex items-start justify-between">
        <div>
          <span className="text-[11px] font-semibold uppercase tracking-wider text-white/30 block mb-1">
            {title}
          </span>
          <div className="text-2xl font-extrabold text-white font-mono tracking-tight">
            {value}
          </div>
          {subtitle && (
            <p className="text-xs text-white/30 mt-1">{subtitle}</p>
          )}
          {trend && (
            <div className="mt-2 flex items-center text-xs font-mono">
              <span className={trend.isPositive ? 'text-emerald-400 font-semibold' : 'text-white/30'}>
                {trend.label}
              </span>
            </div>
          )}
        </div>
        {Icon && (
          <div className={`p-2.5 rounded-lg ${iconBgClasses[accentColor]}`}>
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>
    </div>
  );
};
