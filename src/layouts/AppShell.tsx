import React from 'react';
import { Outlet } from 'react-router-dom';
import { TopBar } from '../components/layout/TopBar';
import { BottomNav } from '../components/layout/BottomNav';
import { ToastContainer } from '../components/common/ToastContainer';

export const AppShell: React.FC = () => {
  return (
    <div className="min-h-screen bg-[#0d0d0d] text-white font-sans flex flex-col">
      <TopBar />
      <main className="flex-1 p-5 md:p-8 pb-28">
        <div className="max-w-7xl mx-auto w-full">
          <Outlet />
        </div>
      </main>
      <BottomNav />
      <ToastContainer />
    </div>
  );
};
