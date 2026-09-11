import React from 'react';
import { NavLink, useLocation, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  ScanLine,
  Target,
  Map as MapIcon,
  BarChart3,
  FileText,
  Settings,
} from 'lucide-react';
import { useAppState } from '../../context/AppStateContext';

export const BottomNav: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { detections } = useAppState();

  const pendingCount = detections.filter((d) => d.verificationStatus === 'PENDING').length;

  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Sonar', path: '/sonar-analysis', icon: ScanLine },
    { name: 'Detections', path: '/detection/DET-001', icon: Target },
    { name: 'Map', path: '/marine-map', icon: MapIcon },
    { name: 'Analytics', path: '/analytics', icon: BarChart3 },
    { name: 'Reports', path: '/reports', icon: FileText },
  ];

  const isNavActive = (path: string) => {
    if (path.startsWith('/detection/')) return location.pathname.startsWith('/detection');
    return location.pathname === path;
  };

  return (
    <nav className="fixed bottom-4 left-1/2 -translate-x-1/2 z-40 max-w-2xl w-[94%] sm:w-auto bg-[#111]/95 backdrop-blur-md border border-white/10 rounded-2xl shadow-2xl px-3 py-2 flex items-center justify-between sm:justify-center gap-1 sm:gap-1.5">
      {navItems.map((item) => {
        const active = isNavActive(item.path);
        const Icon = item.icon;

        return (
          <NavLink
            key={item.name}
            to={item.path}
            className={`flex flex-col sm:flex-row items-center gap-1 sm:gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold transition-all duration-200 relative ${
              active
                ? 'bg-white text-black shadow-md'
                : 'text-white/40 hover:text-white/70 hover:bg-white/5'
            }`}
          >
            <Icon className={`w-4 h-4 ${active ? 'text-black' : 'text-white/40'}`} />
            <span className="text-[11px] sm:text-xs tracking-tight">{item.name}</span>

            {item.name === 'Dashboard' && pendingCount > 0 && (
              <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-white text-black text-[10px] font-bold font-mono flex items-center justify-center shadow-xs">
                {pendingCount}
              </span>
            )}
          </NavLink>
        );
      })}

      <div className="h-6 w-px bg-white/10 mx-1 hidden sm:block" />

      <button
        onClick={() => navigate('/settings')}
        className={`p-2 rounded-xl text-xs transition-colors ${
          location.pathname === '/settings'
            ? 'bg-white/10 text-white'
            : 'text-white/30 hover:text-white/60 hover:bg-white/5'
        }`}
        title="Settings"
      >
        <Settings className="w-4 h-4" />
      </button>
    </nav>
  );
};


