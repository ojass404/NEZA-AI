import React from 'react';
import { useAppState } from '../../context/AppStateContext';
import { DemoBadge } from '../../components/common/Badges';
import {
  Mail,
  Building,
  Anchor,
} from 'lucide-react';

export const ProfilePage: React.FC = () => {
  const { user, detections } = useAppState();

  const verifiedCount = detections.filter((d) => d.verificationStatus === 'VERIFIED').length;

  return (
    <div className="space-y-6 max-w-4xl mx-auto animate-fade-in">
      {/* Header */}
      <div className="pb-4 border-b border-white/8">
        <div className="flex items-center gap-2">
          <h1 className="text-xl md:text-2xl font-bold text-white tracking-tight">
            Analyst Profile & Operational Credentials
          </h1>
          <DemoBadge text="AUTHORIZED ANALYST" />
        </div>
      </div>

      {/* Main Profile Card */}
      <div className="bg-[#161616] border border-white/8 rounded-2xl p-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-5 pb-6 border-b border-white/8">
          <div className="w-16 h-16 rounded-full bg-white/10 border border-white/20 text-white flex items-center justify-center text-xl font-bold font-mono">
            {user.avatar}
          </div>
          <div className="space-y-1">
            <h2 className="text-lg font-bold text-white">{user.name}</h2>
            <div className="text-xs font-mono text-white/50 font-medium">{user.role}</div>
            <div className="flex flex-wrap items-center gap-3 text-xs text-white/40 pt-1">
              <span className="flex items-center gap-1">
                <Building className="w-3.5 h-3.5 text-white/30" />
                {user.department}
              </span>
              <span>•</span>
              <span className="flex items-center gap-1">
                <Mail className="w-3.5 h-3.5 text-white/30" />
                {user.email}
              </span>
            </div>
          </div>
        </div>

        {/* Operational Statistics */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 py-6 border-b border-white/8 text-xs font-mono">
          <div className="p-3.5 bg-white/4 border border-white/8 rounded-xl">
            <span className="text-[10px] text-white/35 uppercase block">Surveys Logged</span>
            <span className="text-xl font-bold text-white font-mono">{user.surveysCompleted}</span>
          </div>
          <div className="p-3.5 bg-white/4 border border-white/8 rounded-xl">
            <span className="text-[10px] text-white/35 uppercase block">Anomalies Verified</span>
            <span className="text-xl font-bold text-white font-mono">{verifiedCount + 76}</span>
          </div>
          <div className="p-3.5 bg-white/4 border border-white/8 rounded-xl">
            <span className="text-[10px] text-white/35 uppercase block">Vessel Sea Days</span>
            <span className="text-xl font-bold text-white font-mono">142</span>
          </div>
          <div className="p-3.5 bg-white/4 border border-white/8 rounded-xl">
            <span className="text-[10px] text-white/35 uppercase block">Active Clearance</span>
            <span className="text-sm font-bold text-white font-mono mt-1 block">MoES Level-3</span>
          </div>
        </div>

        {/* Vessel Deployment History */}
        <div className="pt-5 space-y-3">
          <h3 className="text-xs font-mono font-bold text-white/50 uppercase flex items-center gap-1.5">
            <Anchor className="w-4 h-4" />
            Active Research Vessel Deployments
          </h3>
          <div className="space-y-2 text-xs font-mono">
            <div className="p-3 rounded-xl bg-white/4 border border-white/8 flex justify-between items-center">
              <div>
                <span className="font-bold text-white">CRV Sagar Nidhi</span>
                <span className="text-white/40 ml-2">Gulf of Mannar Ecological Survey</span>
              </div>
              <span className="text-white/50">Lead Sonar Specialist</span>
            </div>
            <div className="p-3 rounded-xl bg-white/4 border border-white/8 flex justify-between items-center">
              <div>
                <span className="font-bold text-white">ORV Sagar Manjusha</span>
                <span className="text-white/40 ml-2">Chennai Coastal Deep Towfish Mission</span>
              </div>
              <span className="text-white/40">Co-Investigator</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
