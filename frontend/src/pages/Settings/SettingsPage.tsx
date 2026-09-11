import React from 'react';
import { Sun, Moon } from 'lucide-react';
import { useTheme } from '../../context/ThemeContext';

export const SettingsPage: React.FC = () => {
  const { theme, setTheme, toggleTheme } = useTheme();
  const isDark = theme === 'dark';

  return (
    <div className="space-y-6 max-w-sm animate-fade-in">
      <div className="pb-4 border-b border-white/8">
        <h1 className="text-xl md:text-2xl font-bold text-white tracking-tight">Settings</h1>
      </div>

      <div className="bg-[#161616] border border-white/8 rounded-2xl p-5 space-y-5 shadow-lg">
        <div className="flex items-center justify-between gap-4">
        <div>
          <span className="text-sm font-semibold text-white block">Theme</span>
          <span className="text-xs text-white/40 mt-0.5 block font-mono">
            {isDark ? 'Dark mode active' : 'Light mode active'}
          </span>
        </div>
        <button
          onClick={toggleTheme}
          type="button"
          aria-label="Toggle theme"
          className={`relative w-14 h-7 rounded-full p-0.5 border transition-all duration-300 flex items-center shadow-inner cursor-pointer ${isDark
              ? 'bg-gradient-to-r from-[#252525] to-[#1a1a1a] border-white/20'
              : 'bg-gradient-to-r from-gray-300 via-gray-200 to-gray-300 border-black/15 shadow-sm'
            }`}
        >
          <span
            className={`w-6 h-6 rounded-full flex items-center justify-center transition-all duration-300 shadow-md ${isDark
                ? 'translate-x-0.5 bg-gradient-to-b from-[#111] to-[#000] text-white border border-white/20'
                : 'translate-x-6.5 bg-gradient-to-b from-white to-gray-100 text-gray-800 border border-gray-300'
              }`}
          >
            {isDark
              ? <Moon className="w-3 h-3 text-white" />
              : <Sun className="w-3 h-3 text-gray-800" />
            }
          </span>
        </button>
        </div>

        <div className="grid grid-cols-2 gap-2 rounded-xl bg-white/5 border border-white/10 p-1">
          <button
            type="button"
            onClick={() => setTheme('dark')}
            className={`flex items-center justify-center gap-2 rounded-lg px-3 py-2 text-xs font-mono font-bold transition-all ${isDark ? 'bg-white text-black' : 'text-white/55 hover:text-white hover:bg-white/8'}`}
          >
            <Moon className="w-3.5 h-3.5" />
            Dark
          </button>
          <button
            type="button"
            onClick={() => setTheme('light')}
            className={`flex items-center justify-center gap-2 rounded-lg px-3 py-2 text-xs font-mono font-bold transition-all ${!isDark ? 'bg-white text-black' : 'text-white/55 hover:text-white hover:bg-white/8'}`}
          >
            <Sun className="w-3.5 h-3.5" />
            Light
          </button>
        </div>
      </div>
    </div>
  );
};
