import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  ScanLine,
  Target,
  Map as MapIcon,
  BarChart3,
  FileText,
  Settings,
  UserCheck,
  Compass,
  Radio,
} from 'lucide-react';
import { useAppState } from '../../context/AppStateContext';

export const Sidebar: React.FC = () => {
  const location = useLocation();
  const { detections } = useAppState();
  const pendingCount = detections.filter((d) => d.verificationStatus === 'PENDING').length;

  const mainNav = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Sonar Analysis', path: '/sonar-analysis', icon: ScanLine },
    { name: 'Detection Details', path: '/detection/DET-001', icon: Target },
    { name: 'Marine Map', path: '/marine-map', icon: MapIcon },
    { name: 'Analytics', path: '/analytics', icon: BarChart3 },
    { name: 'Reports', path: '/reports', icon: FileText },
  ];

  const secondaryNav = [
    { name: 'Profile', path: '/profile', icon: UserCheck },
    { name: 'Settings', path: '/settings', icon: Settings },
  ];

  const isNavActive = (path: string) => {
    if (path.startsWith('/detection/')) {
      return location.pathname.startsWith('/detection');
    }
    return location.pathname === path;
  };

  return (
    <aside className="w-64 bg-[#111] border-r border-white/8 flex flex-col shrink-0 h-screen sticky top-0 select-none z-30">
      {/* Brand Header */}
      <div className="h-16 border-b border-white/8 flex items-center px-5 gap-3">
        <div className="w-9 h-9 rounded-xl bg-white/10 border border-white/15 flex items-center justify-center text-white">
          <Compass className="w-5 h-5 stroke-[2.2]" />
        </div>
        <div className="flex flex-col">
          <div className="flex items-center gap-1.5">
            <span className="font-bold text-base tracking-wider text-white font-mono">
              NEZA<span className="text-white/40">.AI</span>
            </span>
            <span className="px-1.5 py-0.5 text-[9px] font-mono font-bold bg-white/8 text-white/50 rounded border border-white/10">
              SIH-2026
            </span>
          </div>
          <span className="text-[10px] text-white/30 tracking-tight">
            Marine Sonar Intelligence
          </span>
        </div>
      </div>

      {/* MoES / NIOT Subtext Banner */}
      <div className="px-5 py-2.5 bg-white/3 border-b border-white/5 flex items-center justify-between">
        <span className="text-[10px] font-mono text-white/40 uppercase">MoES / NIOT</span>
        <span className="flex items-center gap-1 text-[10px] font-mono text-white/50">
          <Radio className="w-2.5 h-2.5 animate-pulse" />
          ONLINE
        </span>
      </div>

      {/* Navigation Sections */}
      <div className="flex-1 px-3 py-4 space-y-6 overflow-y-auto">
        {/* Main Section */}
        <div>
          <span className="px-3 text-[11px] font-mono uppercase tracking-wider text-white/25 font-semibold block mb-2">
            Main Operations
          </span>
          <nav className="space-y-1">
            {mainNav.map((item) => {
              const active = isNavActive(item.path);
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.name}
                  to={item.path}
                  className={`flex items-center justify-between px-3 py-2 rounded-xl text-xs font-medium transition-colors duration-150 ${
                    active
                      ? 'bg-white text-black font-semibold'
                      : 'text-white/60 hover:bg-white/8 hover:text-white'
                  }`}
                >
                  <div className="flex items-center gap-2.5">
                    <Icon className={`w-4 h-4 ${active ? 'text-black' : 'text-white/40'}`} />
                    <span>{item.name}</span>
                  </div>
                  {item.name === 'Dashboard' && pendingCount > 0 && (
                    <span className="px-1.5 py-0.5 text-[10px] font-mono font-bold rounded-full bg-white/15 text-white">
                      {pendingCount}
                    </span>
                  )}
                </NavLink>
              );
            })}
          </nav>
        </div>

        {/* Secondary Section */}
        <div>
          <span className="px-3 text-[11px] font-mono uppercase tracking-wider text-white/25 font-semibold block mb-2">
            System & Support
          </span>
          <nav className="space-y-1">
            {secondaryNav.map((item) => {
              const active = location.pathname === item.path;
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.name}
                  to={item.path}
                  className={`flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-medium transition-colors duration-150 ${
                    active
                      ? 'bg-white text-black font-semibold'
                      : 'text-white/60 hover:bg-white/8 hover:text-white'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${active ? 'text-black' : 'text-white/40'}`} />
                  <span>{item.name}</span>
                </NavLink>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Sidebar Footer: System Status */}
      <div className="p-3.5 border-t border-white/8">
        <div className="bg-white/4 border border-white/8 rounded-xl p-2.5">
          <div className="flex items-center justify-between text-[11px] font-mono text-white/50 mb-1">
            <span>AI Core</span>
            <span className="text-white font-bold">Simulated</span>
          </div>
          <div className="text-[10px] text-white/30 truncate font-mono">
            Model: YOLOv9-SSS-v4
          </div>
        </div>
      </div>
    </aside>
  );
};
