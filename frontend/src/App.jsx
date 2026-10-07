import React, { useState } from 'react';
import Dashboard from './pages/Dashboard';
import { BarChart3, Search, Settings, BookOpen } from 'lucide-react';

function App() {
  const [activeTab, setActiveTab] = useState('overview'); // overview, single, compare, config

  return (
    <div className="min-h-screen bg-[#0A0F1C] font-sans text-slate-50 selection:bg-blue-500/30">
      <header className="border-b border-slate-800/60 sticky top-0 z-10 bg-[#0A0F1C]/80 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 py-3 sm:px-6 lg:px-8 flex items-center justify-between">
          <div className="flex items-center gap-3 cursor-pointer" onClick={() => setActiveTab('overview')}>
            <div className="w-8 h-8 bg-[#3B82F6] rounded-md flex items-center justify-center text-white font-bold text-lg shadow-lg shadow-blue-500/20">F</div>
            <h1 className="text-xl font-bold text-white tracking-tight">Finlytics AI</h1>
          </div>
          <nav className="hidden md:flex space-x-1">
            <button 
              onClick={() => setActiveTab('overview')}
              className={`flex items-center gap-2 text-sm px-4 py-2 rounded-lg font-medium transition-colors ${activeTab === 'overview' ? 'text-blue-400 bg-blue-500/10' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'}`}>
              <BarChart3 className="w-4 h-4" />
              Overview
            </button>
            <button 
              onClick={() => setActiveTab('single')}
              className={`flex items-center gap-2 text-sm px-4 py-2 rounded-lg font-medium transition-colors ${activeTab === 'single' ? 'text-blue-400 bg-blue-500/10' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'}`}>
              <Search className="w-4 h-4" />
              Company Deep Dive
            </button>
            <button 
              onClick={() => setActiveTab('compare')}
              className={`flex items-center gap-2 text-sm px-4 py-2 rounded-lg font-medium transition-colors ${activeTab === 'compare' ? 'text-blue-400 bg-blue-500/10' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'}`}>
              <Settings className="w-4 h-4" />
              Peer Comparison
            </button>
            <button 
              onClick={() => setActiveTab('config')}
              className={`flex items-center gap-2 text-sm px-4 py-2 rounded-lg font-medium transition-colors ${activeTab === 'config' ? 'text-blue-400 bg-blue-500/10' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'}`}>
              <BookOpen className="w-4 h-4" />
              Investment Principles
            </button>
          </nav>
        </div>
      </header>
      <main>
        <Dashboard externalMode={activeTab} setExternalMode={setActiveTab} />
      </main>
    </div>
  );
}

export default App;
