import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api, setApiKey } from '../../api/client';
import { useAppState } from '../../context/AppStateContext';
export const LoginPage = () => {
  const [key, setKey] = useState(''); const [error, setError] = useState('');
  const navigate = useNavigate(); const {refresh} = useAppState();
  const connect = async (e: React.FormEvent) => { e.preventDefault(); setApiKey(key);
    try { await api('/health/dependencies'); await refresh(); navigate('/sonar-analysis'); }
    catch (e) {setError((e as Error).message); setApiKey('');}
  };
  return <form onSubmit={connect} className="p-10 space-y-4 text-white bg-[#161616] min-h-screen">
    <h1 className="text-2xl">Connect to NEZA AI</h1><p>Enter the deployment API key if configured. Local-only deployments may leave this blank.</p>
    <input aria-label="API key" type="password" value={key} onChange={e => setKey(e.target.value)} autoComplete="off" className="bg-[#242424] p-3"/>
    <button className="bg-white text-black p-3">Connect</button><p role="alert">{error}</p>
    <p>The key stays in this page’s memory and is cleared on reload. Access is shared within one trusted team.</p>
  </form>;
};
