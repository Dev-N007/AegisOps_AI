'use client';

import React, { useState } from 'react';
import { Settings, Key, Database, Sliders, Shield, Save, RefreshCw } from 'lucide-react';

export default function SettingsPage() {
  const [apiKey, setApiKey] = useState('••••••••••••••••••••••••••••••••');
  const [model, setModel] = useState('gemini-1.5-flash');
  const [dbUrl, setDbUrl] = useState('sqlite:///./aegisops.db');
  const [cpuThreshold, setCpuThreshold] = useState(85);
  const [latencyThreshold, setLatencyThreshold] = useState(2000);
  const [saving, setSaving] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setTimeout(() => {
      setSaving(false);
      alert('AegisOps AI settings saved successfully.');
    }, 800);
  };

  return (
    <div className="p-8 space-y-8 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex justify-between items-center border-b border-electric-blue/10 pb-6">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">System Settings</h2>
          <p className="text-gray-400 text-sm">Configure AI integrations, databases, and threshold parameters.</p>
        </div>
      </div>

      <form onSubmit={handleSave} className="space-y-8">
        {/* Section 1: LLM Engine Configuration */}
        <div className="glass-card p-6">
          <h3 className="text-sm font-semibold text-white uppercase tracking-wider mb-6 flex items-center gap-2">
            <Key className="w-4 h-4 text-electric-blue" />
            AI LLM Core Engine
          </h3>
          
          <div className="space-y-4">
            <div>
              <label className="text-xs text-gray-400 block mb-1">Gemini API Key</label>
              <input
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                className="w-full bg-navy-950 border border-electric-blue/15 rounded-lg px-4 py-2 text-xs text-white focus:outline-none focus:border-electric-blue transition-colors font-mono"
              />
              <span className="text-[10px] text-gray-500 mt-1 block">
                If omitted, AegisOps AI runs in zero-dependency High-Fidelity Simulation Mode.
              </span>
            </div>

            <div>
              <label className="text-xs text-gray-400 block mb-1">Primary Triage Model</label>
              <select
                value={model}
                onChange={(e) => setModel(e.target.value)}
                className="w-full bg-navy-950 border border-electric-blue/15 rounded-lg px-4 py-2 text-xs text-white focus:outline-none focus:border-electric-blue transition-colors"
              >
                <option value="gemini-1.5-flash">Gemini 1.5 Flash (Default Speed)</option>
                <option value="gemini-1.5-pro">Gemini 1.5 Pro (High Accuracy)</option>
                <option value="gemini-2.5-flash">Gemini 2.5 Flash (Ultra Low Latency)</option>
                <option value="gemini-2.5-pro">Gemini 2.5 Pro (Recommended)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Section 2: Datastores */}
        <div className="glass-card p-6">
          <h3 className="text-sm font-semibold text-white uppercase tracking-wider mb-6 flex items-center gap-2">
            <Database className="w-4 h-4 text-neon-purple" />
            Active Databases
          </h3>
          
          <div className="space-y-4">
            <div>
              <label className="text-xs text-gray-400 block mb-1">Relational Database URI</label>
              <input
                type="text"
                value={dbUrl}
                onChange={(e) => setDbUrl(e.target.value)}
                className="w-full bg-navy-950 border border-electric-blue/15 rounded-lg px-4 py-2 text-xs text-white focus:outline-none focus:border-electric-blue transition-colors font-mono"
              />
            </div>
            
            <div>
              <label className="text-xs text-gray-400 block mb-1">ChromaDB Path</label>
              <input
                type="text"
                value="./vector_db"
                disabled
                className="w-full bg-navy-950/50 border border-electric-blue/10 rounded-lg px-4 py-2 text-xs text-gray-500 font-mono"
              />
            </div>
          </div>
        </div>

        {/* Section 3: Metric Thresholds */}
        <div className="glass-card p-6">
          <h3 className="text-sm font-semibold text-white uppercase tracking-wider mb-6 flex items-center gap-2">
            <Sliders className="w-4 h-4 text-neon-cyan" />
            Alerting Telemetry Thresholds
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="text-xs text-gray-400 block mb-1">CPU Anomaly Threshold (%)</label>
              <input
                type="number"
                value={cpuThreshold}
                onChange={(e) => setCpuThreshold(Number(e.target.value))}
                className="w-full bg-navy-950 border border-electric-blue/15 rounded-lg px-4 py-2 text-xs text-white focus:outline-none focus:border-electric-blue"
              />
            </div>
            
            <div>
              <label className="text-xs text-gray-400 block mb-1">Latency Trigger limit (ms)</label>
              <input
                type="number"
                value={latencyThreshold}
                onChange={(e) => setLatencyThreshold(Number(e.target.value))}
                className="w-full bg-navy-950 border border-electric-blue/15 rounded-lg px-4 py-2 text-xs text-white focus:outline-none focus:border-electric-blue"
              />
            </div>
          </div>
        </div>

        {/* Save button */}
        <div className="flex justify-end gap-4 border-t border-electric-blue/10 pt-6">
          <button
            type="submit"
            disabled={saving}
            className="flex items-center gap-2 px-6 py-2.5 bg-electric-blue hover:bg-electric-glow text-white text-xs font-bold rounded-lg transition-all shadow-[0_0_15px_rgba(59,130,246,0.3)] disabled:opacity-50"
          >
            {saving ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                Saving Configs...
              </>
            ) : (
              <>
                <Save className="w-4 h-4" />
                Save Settings
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
