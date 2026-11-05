import React, { useState } from 'react';
import { Database, Plus, Search, Shield, FileText } from 'lucide-react';

export default function KnowledgeVault({ tenantId: _tenantId, clearanceLevel }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [activeFilter, setActiveFilter] = useState('ALL');
  const [showIngestModal, setShowIngestModal] = useState(false);

  // Ingest Form State
  const [newContent, setNewContent] = useState('');
  const [newKind, setNewKind] = useState('procedural');
  const [newRef, setNewRef] = useState('');
  const [newClearance, setNewClearance] = useState(1);

  const [memories, setMemories] = useState([
    {
      id: "mem-001",
      kind: "procedural",
      content: "Corporate Travel Policy Section 4.1: Domestic flights are reimbursed up to economy class limit of $500. Any higher fare requires VP approval.",
      source_reference: "Corporate Travel Policy Section 4.1",
      required_clearance_level: 1,
      confidence: 0.98,
      status: "active",
      created_at: "2026-11-01"
    },
    {
      id: "mem-002",
      kind: "procedural",
      content: "InfoSec SOP 12: Lost laptops or mobile devices must be reported to the SOC helpdesk within 1 hour. An automated remote wipe will be initiated immediately.",
      source_reference: "InfoSec SOP 12",
      required_clearance_level: 1,
      confidence: 0.99,
      status: "active",
      created_at: "2026-11-02"
    },
    {
      id: "mem-003",
      kind: "semantic",
      content: "Architecture Governance Guideline 8: All East-West microservice traffic must be secured via mTLS using SPIFFE/SPIRE x509 certificates alongside signed JWT tokens.",
      source_reference: "Architecture Governance Guideline 8",
      required_clearance_level: 2,
      confidence: 0.95,
      status: "active",
      created_at: "2026-11-03"
    },
    {
      id: "mem-004",
      kind: "semantic",
      content: "Compliance Policy FIN-901: All transaction ledgers and customer audit records must be preserved for exactly 7 years in immutable WORM storage.",
      source_reference: "Compliance Policy FIN-901",
      required_clearance_level: 3,
      confidence: 0.97,
      status: "active",
      created_at: "2026-11-04"
    },
    {
      id: "mem-005",
      kind: "episodic",
      content: "Employee Handbook Benefits 2026: Full-time employees with at least 6 months of tenure are entitled to 16 weeks of fully paid parental leave.",
      source_reference: "Employee Handbook Benefits 2026",
      required_clearance_level: 1,
      confidence: 0.95,
      status: "active",
      created_at: "2026-11-05"
    }
  ]);

  const handleIngest = (e) => {
    e.preventDefault();
    if (!newContent.trim() || !newRef.trim()) return;

    const newRec = {
      id: `mem-${Math.random().toString(16).substring(2, 6)}`,
      kind: newKind,
      content: newContent,
      source_reference: newRef,
      required_clearance_level: Number(newClearance),
      confidence: 0.98,
      status: "active",
      created_at: "Just now"
    };

    setMemories(prev => [newRec, ...prev]);
    setNewContent('');
    setNewRef('');
    setShowIngestModal(false);
  };

  const filteredMemories = memories.filter(m => {
    const matchesQuery = m.content.toLowerCase().includes(searchQuery.toLowerCase()) || 
                         m.source_reference.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesFilter = activeFilter === 'ALL' || m.kind.toUpperCase() === activeFilter;
    const matchesClearance = m.required_clearance_level <= clearanceLevel;
    return matchesQuery && matchesFilter && matchesClearance;
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      
      {/* Top Filter and Search Bar */}
      <div className="card-panel" style={{ padding: '16px 20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '16px' }}>
        
        {/* Search Input */}
        <div style={{ position: 'relative', flex: 1, maxWidth: '480px' }}>
          <Search size={14} color="var(--ink-subtle)" style={{ position: 'absolute', left: '12px', top: '10px' }} />
          <input
            type="text"
            className="input-text"
            style={{ width: '100%', paddingLeft: '34px' }}
            placeholder="Filter chunks by semantic keywords, citations, or references..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        {/* Category Pills & Ingest Trigger */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div className="nav-toggle-group">
            {['ALL', 'PROCEDURAL', 'SEMANTIC', 'EPISODIC'].map((f) => (
              <button
                key={f}
                className={`nav-toggle-item ${activeFilter === f ? 'active' : ''}`}
                onClick={() => setActiveFilter(f)}
                style={{ fontSize: '11px', padding: '4px 10px' }}
              >
                {f}
              </button>
            ))}
          </div>

          <button className="btn-primary" onClick={() => setShowIngestModal(true)}>
            <Plus size={14} />
            <span>Ingest Document</span>
          </button>
        </div>
      </div>

      {/* Memory Chunks Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(420px, 1fr))', gap: '16px' }}>
        {filteredMemories.map((m) => (
          <div 
            key={m.id} 
            className="card-panel" 
            style={{ 
              display: 'flex', 
              flexDirection: 'column', 
              justifyContent: 'space-between', 
              gap: '12px',
              transition: 'background-color 0.15s ease, border-color 0.15s ease'
            }}
            onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = 'var(--surface-2)'; e.currentTarget.style.borderColor = 'var(--hairline-strong)'; }}
            onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = 'var(--surface-1)'; e.currentTarget.style.borderColor = 'var(--hairline)'; }}
          >
            <div>
              {/* Card Meta Header */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span className="mono" style={{ fontSize: '11px', color: 'var(--ink-subtle)' }}>
                  {m.id} · {m.kind.toUpperCase()}
                </span>
                <span className="status-badge" style={{ backgroundColor: 'var(--surface-3)', color: 'var(--ink-muted)' }}>
                  <Shield size={10} color="var(--primary)" />
                  Lvl {m.required_clearance_level}
                </span>
              </div>

              {/* Chunk Content */}
              <div style={{ fontSize: '13px', lineHeight: '1.6', color: 'var(--ink)', marginBottom: '12px' }}>
                {m.content}
              </div>
            </div>

            {/* Card Footer */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '10px', borderTop: '1px solid var(--hairline)', fontSize: '11px', color: 'var(--ink-subtle)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                <FileText size={11} color="var(--ink-tertiary)" />
                <span style={{ fontWeight: 500 }}>{m.source_reference}</span>
              </div>
              <div className="mono">
                Conf: {(m.confidence * 100).toFixed(0)}%
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Ingest Document Modal */}
      {showIngestModal && (
        <div 
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'var(--semantic-overlay)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
            backdropFilter: 'blur(4px)'
          }}
        >
          <div 
            className="card-panel" 
            style={{ 
              width: '100%', 
              maxWidth: '540px', 
              backgroundColor: 'var(--surface-1)',
              borderColor: 'var(--hairline-strong)',
              boxShadow: '0 20px 40px rgba(0, 0, 0, 0.8), inset 0 1px 0 0 rgba(255, 255, 255, 0.08)'
            }}
          >
            <div className="card-header">
              <span className="card-title">
                <Database size={16} color="var(--primary)" />
                Ingest Enterprise Document
              </span>
              <button 
                onClick={() => setShowIngestModal(false)}
                style={{ background: 'transparent', border: 'none', color: 'var(--ink-subtle)', fontSize: '16px' }}
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleIngest} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '12px', color: 'var(--ink-muted)', marginBottom: '6px' }}>Source Reference</label>
                <input
                  type="text"
                  className="input-text"
                  style={{ width: '100%' }}
                  placeholder="e.g. IT Security SOP 2026-B"
                  value={newRef}
                  onChange={(e) => setNewRef(e.target.value)}
                  required
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '12px', color: 'var(--ink-muted)', marginBottom: '6px' }}>Memory Kind</label>
                  <select
                    className="input-text"
                    style={{ width: '100%', cursor: 'pointer' }}
                    value={newKind}
                    onChange={(e) => setNewKind(e.target.value)}
                  >
                    <option value="procedural">Procedural (SOP)</option>
                    <option value="semantic">Semantic (Fact/Rule)</option>
                    <option value="episodic">Episodic (Event)</option>
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '12px', color: 'var(--ink-muted)', marginBottom: '6px' }}>Required Clearance</label>
                  <select
                    className="input-text"
                    style={{ width: '100%', cursor: 'pointer' }}
                    value={newClearance}
                    onChange={(e) => setNewClearance(Number(e.target.value))}
                  >
                    <option value={1}>L1 (Public)</option>
                    <option value={2}>L2 (Internal)</option>
                    <option value={3}>L3 (Confidential)</option>
                    <option value={4}>L4 (Restricted)</option>
                  </select>
                </div>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '12px', color: 'var(--ink-muted)', marginBottom: '6px' }}>Chunk Document Content</label>
                <textarea
                  className="input-text"
                  rows={5}
                  style={{ width: '100%', resize: 'vertical' }}
                  placeholder="Paste verified policy text, instructions, or regulatory guidelines..."
                  value={newContent}
                  onChange={(e) => setNewContent(e.target.value)}
                  required
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '8px' }}>
                <button type="button" className="btn-secondary" onClick={() => setShowIngestModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary">
                  Commit to Memory (HNSW + BM25)
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}
