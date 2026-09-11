import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppState } from '../../context/AppStateContext';
import { PriorityReviewQueue } from './components/PriorityReviewQueue';
import { RecentSonarScans } from './components/RecentSonarScans';
import { DashboardActivityChart } from './components/DashboardActivityChart';
import { DashboardVerificationChart } from './components/DashboardVerificationChart';
import { Scan, Target, AlertTriangle, Clock, Plus, Map as MapIcon } from 'lucide-react';

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const { scans, detections } = useAppState();

  const pendingVerification = detections.filter((d) => d.verificationStatus === 'PENDING').length;

  const stats = [
    { label: 'Total Scans', value: 24, sub: 'acoustic swaths', icon: Scan, onClick: () => navigate('/sonar-analysis') },
    { label: 'AI Detections', value: 87, sub: 'seabed anomalies', icon: Target, onClick: () => navigate('/analytics') },
    { label: 'High Priority', value: 12, sub: 'hazardous debris', icon: AlertTriangle, onClick: () => navigate('/marine-map') },
    { label: 'Pending Review', value: pendingVerification, sub: 'awaiting analyst', icon: Clock, onClick: () => navigate('/detection/DET-001') },
  ];

  const priorityDetections = detections
    .filter((d) => d.priority === 'HIGH' || d.verificationStatus === 'PENDING')
    .slice(0, 5);

  const verifiedPct = Math.round(
    (detections.filter((d) => d.verificationStatus === 'VERIFIED').length /
      Math.max(1, detections.filter((d) => d.verificationStatus !== 'PENDING').length)) * 100
  );

  return (
    <div className="space-y-5">
      {/* Hero */}
      <div className="relative rounded-2xl overflow-hidden bg-gradient-to-br from-[#1a1a1a] via-[#222] to-[#111] border border-white/10 p-6 md:p-8">
        {/* subtle grain overlay */}
        <div className="absolute inset-0 opacity-[0.03] bg-[radial-gradient(circle_at_1px_1px,white_1px,transparent_0)] bg-[size:24px_24px] pointer-events-none" />
        <div className="relative z-10 flex flex-col md:flex-row md:items-center md:justify-between gap-5">
          <div>

            <h1 className="text-2xl md:text-3xl font-bold text-white tracking-tight">NEZA AI</h1>

          </div>
          <div className="flex items-center gap-2 shrink-0">
            <button
              onClick={() => navigate('/marine-map')}
              className="flex items-center gap-2 px-4 py-2 rounded-xl border border-white/15 text-white/70 text-sm font-medium hover:bg-white/5 transition-colors"
            >
              <MapIcon className="w-4 h-4" />
              Map
            </button>
            <button
              onClick={() => navigate('/sonar-analysis')}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white text-black text-sm font-semibold hover:bg-white/90 transition-colors"
            >
              <Plus className="w-4 h-4" />
              New Analysis
            </button>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {stats.map((s) => {
          const Icon = s.icon;
          return (
            <button
              key={s.label}
              onClick={s.onClick}
              className="text-left p-4 rounded-xl bg-[#161616] border border-white/8 hover:border-white/15 transition-colors group"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="w-8 h-8 rounded-lg bg-white/5 border border-white/10 flex items-center justify-center group-hover:bg-white/10 transition-colors">
                  <Icon className="w-4 h-4 text-white/60" />
                </div>
              </div>
              <div className="text-2xl font-bold text-white">{s.value}</div>
              <div className="text-xs text-white/40 mt-0.5">{s.label}</div>
              <div className="text-[11px] text-white/20 mt-0.5">{s.sub}</div>
            </button>
          );
        })}
      </div>

      {/* Priority Queue */}
      <PriorityReviewQueue detections={priorityDetections} />

      {/* Scans + Verification */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2">
          <RecentSonarScans scans={scans} />
        </div>
        <div className="bg-[#161616] border border-white/8 rounded-xl p-4 flex flex-col gap-3">
          <div>
            <h3 className="text-sm font-semibold text-white">Verification Audit</h3>
            <p className="text-xs text-white/30 mt-0.5">Analyst validation breakdown.</p>
          </div>
          <div className="flex-1">
            <DashboardVerificationChart />
          </div>
          <div className="pt-3 border-t border-white/8 flex items-center justify-between text-xs">
            <span className="text-white/30 font-mono">Acceptance rate</span>
            <span className="font-bold text-white">{verifiedPct}% verified</span>
          </div>
        </div>
      </div>

      {/* Activity Chart */}
      <div className="bg-[#161616] border border-white/8 rounded-xl p-4">
        <div className="flex items-center justify-between mb-3">
          <div>
            <h3 className="text-sm font-semibold text-white">Detection Activity</h3>
            <p className="text-xs text-white/30 mt-0.5">Daily inference yield from vessel deployments.</p>
          </div>
          <button onClick={() => navigate('/analytics')} className="text-xs text-white/40 hover:text-white transition-colors">
            Full Analytics →
          </button>
        </div>
        <DashboardActivityChart />
      </div>
    </div>
  );
};

