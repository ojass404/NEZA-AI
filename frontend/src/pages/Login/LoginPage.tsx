import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Compass, ArrowRight, Lock, Mail } from 'lucide-react';
import { DemoBadge } from '../../components/common/Badges';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('r.ramanathan@niot.res.in');
  const [password, setPassword] = useState('••••••••••••');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    navigate('/dashboard');
  };

  return (
    <div className="min-h-screen bg-[#0d0d0d] flex items-center justify-center p-4 font-sans">
      <div className="bg-[#161616] border border-white/10 rounded-2xl max-w-md w-full p-8 shadow-2xl text-white space-y-6 relative">
        {/* Brand Header */}
        <div className="text-center space-y-2">
          <div className="w-12 h-12 mx-auto rounded-full bg-white/10 border border-white/15 flex items-center justify-center text-white">
            <Compass className="w-7 h-7 stroke-[2.2]" />
          </div>
          <h1 className="text-2xl font-bold font-mono tracking-wider text-white">
            NEZA<span className="text-white/50">.AI</span>
          </h1>
          <p className="text-xs text-white/40 leading-relaxed max-w-xs mx-auto">
            AI-Powered Marine Debris and Underwater Anomaly Intelligence Platform
          </p>
          <div className="pt-1">
            <DemoBadge text="MoES / NIOT SIH-2026 EVALUATION" />
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1">
            <label className="block text-xs font-mono text-white/50">Analyst Email</label>
            <div className="relative">
              <Mail className="w-4 h-4 text-white/30 absolute left-3 top-2.5" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-[#0d0d0d] border border-white/10 rounded-lg pl-9 pr-3 py-2 text-xs font-mono text-white/80 focus:outline-hidden focus:border-white/25 transition-colors"
              />
            </div>
          </div>

          <div className="space-y-1">
            <label className="block text-xs font-mono text-white/50">Security Key</label>
            <div className="relative">
              <Lock className="w-4 h-4 text-white/30 absolute left-3 top-2.5" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-[#0d0d0d] border border-white/10 rounded-lg pl-9 pr-3 py-2 text-xs font-mono text-white/80 focus:outline-hidden focus:border-white/25 transition-colors"
              />
            </div>
          </div>

          <button
            type="submit"
            className="w-full py-2.5 rounded-xl bg-white hover:bg-white/90 text-black font-bold text-xs font-mono flex items-center justify-center gap-2 transition-colors"
          >
            <span>Sign In to Operation Portal</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        <div className="pt-2 border-t border-white/8 text-center">
          <button
            type="button"
            onClick={() => navigate('/dashboard')}
            className="text-xs font-mono text-white/40 hover:text-white transition-colors"
          >
            Direct Prototype Access (Skip Login) →
          </button>
        </div>
      </div>
    </div>
  );
};
