import React from 'react';
import { useAppState } from '../context/AppStateContext';
import { Outlet, Link } from 'react-router-dom';
import { TopBar } from '../components/layout/TopBar';
import { BottomNav } from '../components/layout/BottomNav';
import { ToastContainer } from '../components/common/ToastContainer';

export const AppShell: React.FC = () => {
  const {error, refresh} = useAppState();
  return (
    <div className="min-h-screen bg-[#0d0d0d] text-white font-sans flex flex-col">
      <TopBar />
      <main className="flex-1 p-5 md:p-8 pb-28">
        <div className="max-w-7xl mx-auto w-full">
          {error && <div role="alert" className="p-4 mb-4 border border-red-400 text-red-300">{error} <button onClick={() => refresh()}>Retry</button> · <Link to="/login">Configure access</Link></div>}
          <Outlet />
        </div>
      </main>
      <BottomNav />
      <ToastContainer />
    </div>
  );
};
