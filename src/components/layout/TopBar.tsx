import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAppState } from '../../context/AppStateContext';
import { Compass, ChevronRight } from 'lucide-react';

export const TopBar: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { systemStatus } = useAppState();

  const getPageInfo = () => {
    const path = location.pathname;
    if (path.includes('/dashboard')) return { title: 'Dashboard', category: 'Operations' };
    if (path.includes('/sonar-analysis')) return { title: 'Sonar Analysis', category: 'Acoustics' };
    if (path.includes('/detection')) return { title: 'Detection Review', category: 'Review' };
    if (path.includes('/marine-map')) return { title: 'Marine Map', category: 'Hydrography' };
    if (path.includes('/analytics')) return { title: 'Analytics', category: 'Intelligence' };
    if (path.includes('/reports')) return { title: 'Reports', category: 'Docs' };
    if (path.includes('/settings')) return { title: 'Settings', category: 'Config' };
    return { title: 'NEZA AI', category: 'Marine Intelligence' };
  };

  const pageInfo = getPageInfo();

  return (
    <header className="h-14 bg-[#111]/95 backdrop-blur-md border-b border-white/10 px-5 flex items-center justify-between shrink-0 sticky top-0 z-30">
      {/* Brand & Breadcrumbs */}
      <div className="flex items-center gap-4">
        <div onClick={() => navigate('/dashboard')} className="flex items-center gap-2.5 cursor-pointer group">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-white/20 to-white/5 border border-white/10 flex items-center justify-center group-hover:border-white/30 transition-colors">
            <Compass className="w-4 h-4 text-white" />
          </div>
          <span className="font-bold text-sm tracking-widest text-white font-mono">
            NEZA<span className="text-white/40">.AI</span>
          </span>
        </div>

        <div className="hidden md:flex items-center gap-1.5 text-xs font-mono text-white/30 pl-3 border-l border-white/10">
          <span>{pageInfo.category}</span>
          <ChevronRight className="w-3 h-3 text-white/20" />
          <span className="text-white/60">{pageInfo.title}</span>
        </div>
      </div>

      
    </header>
  );
};
