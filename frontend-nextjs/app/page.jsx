"use client";
import { useState } from 'react';
import Sidebar from '../components/Sidebar';
import AIAssistant from '../components/AIAssistant';
import FilterSearch from '../components/FilterSearch';
import LoadingOverlay from '../components/LoadingOverlay';

export default function Home() {
  const [mode, setMode] = useState('ai');
  const [isLoading, setIsLoading] = useState(false);

  return (
    <div className="app-container">
      <Sidebar mode={mode} setMode={setMode} />
      <main className="main-content">
        <header className="mobile-header">
          <div className="logo">
            <span className="material-symbols-outlined logo__icon">restaurant_menu</span>
            <span className="logo__text">GastroAI</span>
          </div>
        </header>
        
        {mode === 'ai' ? (
          <AIAssistant setIsLoading={setIsLoading} />
        ) : (
          <FilterSearch setIsLoading={setIsLoading} />
        )}
      </main>

      <nav className="bottom-nav">
        <a href="#" className={`bottom-nav__link ${mode === 'ai' ? 'bottom-nav__link--active' : ''}`} onClick={(e) => {e.preventDefault(); setMode('ai');}}>
          <span className="material-symbols-outlined">smart_toy</span>
          <span>AI</span>
        </a>
        <a href="#" className={`bottom-nav__link ${mode === 'filter' ? 'bottom-nav__link--active' : ''}`} onClick={(e) => {e.preventDefault(); setMode('filter');}}>
          <span className="material-symbols-outlined">tune</span>
          <span>Filter</span>
        </a>
      </nav>

      <LoadingOverlay isLoading={isLoading} />
    </div>
  );
}
