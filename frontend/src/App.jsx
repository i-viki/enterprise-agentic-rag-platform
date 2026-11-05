import React, { useState } from 'react';
import './App.css';
import { 
  ShieldCheck, MessageSquare, Activity, Database, 
  Lock 
} from 'lucide-react';
import CognitionStudio from './components/CognitionStudio';
import ObservabilityHub from './components/ObservabilityHub';
import KnowledgeVault from './components/KnowledgeVault';

export default function App() {
  const [activeTab, setActiveTab] = useState('cognition'); // cognition, observability, knowledge
  const [tenantId] = useState('tenant-enterprise-prod');
  const [clearanceLevel, setClearanceLevel] = useState(1);
  const [userRoles] = useState(['EMPLOYEE', 'FINANCE']);
  const [latestTrace, setLatestTrace] = useState(null);

  return (
    <div className="app-container">
      {/* 56px Top Navigation */}
      <header className="app-header">
        <div className="brand-section">
          <div className="brand-glyph">
            <ShieldCheck size={16} />
          </div>
          <div className="brand-title-wrap">
            <span className="brand-title">Enterprise Cognitive Engine</span>
            <span className="brand-badge">Air-Gapped</span>
          </div>
        </div>

        {/* Center Nav Toggle Group */}
        <nav className="nav-toggle-group">
          <button
            className={`nav-toggle-item ${activeTab === 'cognition' ? 'active' : ''}`}
            onClick={() => setActiveTab('cognition')}
          >
            <MessageSquare size={14} /> Cognition Studio
          </button>
          <button
            className={`nav-toggle-item ${activeTab === 'observability' ? 'active' : ''}`}
            onClick={() => setActiveTab('observability')}
          >
            <Activity size={14} /> Observability & APM
          </button>
          <button
            className={`nav-toggle-item ${activeTab === 'knowledge' ? 'active' : ''}`}
            onClick={() => setActiveTab('knowledge')}
          >
            <Database size={14} /> Knowledge Vault
          </button>
        </nav>

        {/* Right Status & Clearance Controls */}
        <div className="header-controls">
          {/* RBAC Clearance Level Selector */}
          <div className="clearance-select-pill">
            <Lock size={12} color="var(--ink-subtle)" />
            <span>Clearance:</span>
            <select
              value={clearanceLevel}
              onChange={(e) => setClearanceLevel(Number(e.target.value))}
            >
              <option value={1}>L1 (Public)</option>
              <option value={2}>L2 (Internal)</option>
              <option value={3}>L3 (Confidential)</option>
              <option value={4}>L4 (Restricted)</option>
              <option value={5}>L5 (Top Secret)</option>
            </select>
          </div>

          {/* Microservice Live Status Indicators */}
          <div className="status-pills">
            <div className="status-pill" title="Java 21 Spring Boot Governance Gateway (Port 8080)">
              <span className="status-dot"></span> Core :8080
            </div>
            <div className="status-pill" title="Python 3.12 FastAPI LangGraph Engine (Port 8000)">
              <span className="status-dot"></span> Agent :8000
            </div>
            <div className="status-pill" title="Local Ollama Private Models (Port 11434)">
              <span className="status-dot"></span> Ollama :11434
            </div>
          </div>
        </div>
      </header>

      {/* Main Canvas Area */}
      <main className="main-content">
        {activeTab === 'cognition' && (
          <CognitionStudio 
            tenantId={tenantId}
            clearanceLevel={clearanceLevel}
            userRoles={userRoles}
            onTraceGenerated={(traceData) => setLatestTrace(traceData)}
          />
        )}

        {activeTab === 'observability' && (
          <ObservabilityHub 
            currentTrace={latestTrace}
          />
        )}

        {activeTab === 'knowledge' && (
          <KnowledgeVault 
            tenantId={tenantId}
            clearanceLevel={clearanceLevel}
          />
        )}
      </main>

      {/* Refined Canvas Footer */}
      <footer style={{
        borderTop: '1px solid var(--hairline)',
        backgroundColor: 'var(--canvas)',
        padding: '16px 24px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        fontSize: '12px',
        color: 'var(--ink-subtle)',
        marginTop: 'auto'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span>Enterprise Agentic RAG Platform</span>
          <span style={{ color: 'var(--ink-tertiary)' }}>·</span>
          <span>Zero-Data-Egress Cognitive Architecture</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <span>Crafted by <a href="https://jayavignesh.dev" target="_blank" rel="noreferrer" style={{ color: 'var(--ink)', textDecoration: 'none', fontWeight: 500 }}>Jayavignesh</a></span>
          <span style={{ color: 'var(--ink-tertiary)' }}>·</span>
          <a href="https://jayavignesh.dev" target="_blank" rel="noreferrer" style={{ color: 'var(--primary)', textDecoration: 'none' }}>jayavignesh.dev</a>
          <span style={{ color: 'var(--ink-tertiary)' }}>·</span>
          <a href="https://github.com/i-viki" target="_blank" rel="noreferrer" style={{ color: 'var(--ink-subtle)', textDecoration: 'none' }}>GitHub</a>
        </div>
      </footer>
    </div>
  );
}
