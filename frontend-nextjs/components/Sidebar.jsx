"use client";
export default function Sidebar({ mode, setMode }) {
  return (
    <nav className="sidebar">
      <div className="logo">
        <span className="material-symbols-outlined logo__icon">restaurant_menu</span>
        <span className="logo__text">GastroAI</span>
      </div>
      <div className="sidebar__nav">
        <h3 className="nav-section-title">Mode</h3>
        <button 
          className={`mode-toggle-btn ${mode === 'ai' ? 'mode-toggle-btn--active' : 'mode-toggle-btn--inactive'}`}
          onClick={() => setMode('ai')}
        >
          <span className="material-symbols-outlined">smart_toy</span>
          AI Assistant
        </button>
        <button 
          className={`mode-toggle-btn ${mode === 'filter' ? 'mode-toggle-btn--active' : 'mode-toggle-btn--inactive'}`}
          onClick={() => setMode('filter')}
        >
          <span className="material-symbols-outlined">tune</span>
          Filter Search
        </button>
      </div>
    </nav>
  );
}
