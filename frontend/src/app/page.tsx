'use client';

import React, { useEffect, useState } from 'react';
import { 
  ShieldAlert, Activity, CheckCircle, Clock, Zap, Play, Check, 
  Terminal, FileText, ArrowRight, ShieldCheck, Database, RefreshCw, Cpu
} from 'lucide-react';
import { api } from '@/services/api';
import { Incident, KPIStats, SimulationResponse } from '@/types';

export default function Dashboard() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null);
  const [kpis, setKpis] = useState<KPIStats>({
    active_incidents: 0,
    critical_alerts: 0,
    mttr: '14.2 mins',
    ai_confidence: '93.4%'
  });
  
  const [loading, setLoading] = useState(true);
  const [diagnosing, setDiagnosing] = useState(false);
  
  // What-If Simulator State
  const [simulationQuery, setSimulationQuery] = useState('');
  const [simulationResult, setSimulationResult] = useState<SimulationResponse | null>(null);
  const [simulating, setSimulating] = useState(false);

  const loadData = async (selectId?: string) => {
    try {
      setLoading(true);
      const data = await api.getIncidents();
      setIncidents(data);
      
      // Auto select incident
      if (data.length > 0) {
        if (selectId) {
          const found = data.find(i => i.id === selectId);
          setSelectedIncident(found || data[0]);
        } else {
          setSelectedIncident(data[0]);
        }
      }
      
      const analytics = await api.getAnalytics();
      setKpis(analytics.kpis);
    } catch (e) {
      console.error("Failed to load dashboard data:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleDiagnose = async (id: string) => {
    setDiagnosing(true);
    try {
      await api.diagnoseIncident(id);
      await loadData(id);
    } catch (e) {
      alert("Diagnostics execution failed.");
      console.error(e);
    } finally {
      setDiagnosing(false);
    }
  };

  const handleSimulate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!simulationQuery || !selectedIncident) return;
    setSimulating(true);
    try {
      const res = await api.simulateAction(simulationQuery, selectedIncident.id);
      setSimulationResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setSimulating(false);
    }
  };

  // Stepper timeline helper
  const getStepStatus = (stepName: string, status: string) => {
    const order = ["Triggered", "Investigating", "RCA Found", "Knowledge Retrieved", "Resolution Generated", "Mitigating", "Resolved"];
    const currentIdx = order.indexOf(status);
    
    const stepsMap: { [key: string]: number } = {
      'alert': 0,
      'log': 1,
      'rca': 2,
      'rag': 3,
      'resolution': 4,
      'communication': 5
    };
    
    const targetStepIdx = stepsMap[stepName];
    
    if (currentIdx > targetStepIdx) return 'completed';
    if (currentIdx === targetStepIdx) return 'active';
    return 'pending';
  };

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex justify-between items-center border-b border-electric-blue/10 pb-6">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">Incident Command Center</h2>
          <p className="text-gray-400 text-sm">Autonomous site reliability engineering workspace.</p>
        </div>
        <button 
          onClick={() => loadData(selectedIncident?.id)} 
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-navy-900 border border-electric-blue/20 hover:bg-navy-800 text-sm text-gray-300 transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          Refresh Stats
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {[
          { label: 'Active Incidents', value: kpis.active_incidents, icon: ShieldAlert, color: 'text-neon-red' },
          { label: 'Critical Alerts', value: kpis.critical_alerts, icon: Activity, color: 'text-orange-500' },
          { label: 'Platform MTTR', value: kpis.mttr, icon: Clock, color: 'text-electric-blue' },
          { label: 'AI Resolution Confidence', value: kpis.ai_confidence, icon: Zap, color: 'text-neon-purple' },
        ].map((card, i) => {
          const CardIcon = card.icon;
          return (
            <div key={i} className="glass-card p-6 flex items-center justify-between">
              <div>
                <span className="text-xs text-gray-400 font-medium tracking-wide uppercase">{card.label}</span>
                <h3 className="text-2xl font-bold text-white mt-1">{card.value}</h3>
              </div>
              <div className={`p-3 rounded-lg bg-navy-900 border border-electric-blue/10 ${card.color}`}>
                <CardIcon className="w-5 h-5" />
              </div>
            </div>
          );
        })}
      </div>

      {/* Main Grid split */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Left 8 cols: Incident details, metrics and timeline */}
        <div className="lg:col-span-8 space-y-8">
          
          {/* Incident Selector */}
          <div className="glass-card p-6">
            <h4 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-4">Select Active Incident</h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
              {incidents.map((inc) => (
                <button
                  key={inc.id}
                  onClick={() => setSelectedIncident(inc)}
                  className={`p-4 rounded-lg border text-left transition-all ${
                    selectedIncident?.id === inc.id
                      ? 'border-electric-blue bg-electric-blue/10'
                      : 'border-electric-blue/10 bg-navy-950 hover:bg-navy-900/40'
                  }`}
                >
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-[10px] font-mono text-electric-blue bg-navy-900 px-2 py-0.5 rounded">
                      {inc.id}
                    </span>
                    <span className={`text-[10px] font-semibold px-2 py-0.5 rounded ${
                      inc.severity === 'Critical' ? 'bg-neon-red/15 text-neon-red' : 'bg-orange-500/15 text-orange-400'
                    }`}>
                      {inc.severity}
                    </span>
                  </div>
                  <h5 className="font-semibold text-white text-xs truncate">{inc.title}</h5>
                  <div className="flex items-center gap-1.5 mt-2">
                    <span className={`w-1.5 h-1.5 rounded-full ${
                      inc.status === 'Resolved' ? 'bg-neon-green' : 'bg-electric-blue animate-pulse'
                    }`}></span>
                    <span className="text-[10px] text-gray-400">{inc.status}</span>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {selectedIncident && (
            <>
              {/* Alert Metrics Section */}
              <div className="glass-card p-6">
                <div className="flex justify-between items-center mb-6">
                  <h4 className="text-sm font-semibold text-gray-300 uppercase tracking-wider">Metrics Snapshot ({selectedIncident.id})</h4>
                  <span className="text-xs text-gray-400 font-mono">Service: {selectedIncident.alert_data?.service || 'N/A'}</span>
                </div>
                
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-6">
                  {[
                    { label: 'CPU Usage', value: selectedIncident.metrics?.cpu ? `${selectedIncident.metrics.cpu}%` : 'N/A' },
                    { label: 'Memory Usage', value: selectedIncident.metrics?.memory ? `${selectedIncident.metrics.memory}%` : 'N/A' },
                    { label: 'API Latency', value: selectedIncident.metrics?.latency ? `${selectedIncident.metrics.latency}ms` : 'N/A' },
                    { label: 'Error Rate', value: selectedIncident.metrics?.error_rate ? `${selectedIncident.metrics.error_rate}%` : 'N/A' },
                  ].map((metric, idx) => (
                    <div key={idx} className="p-4 rounded-lg bg-navy-950 border border-electric-blue/5">
                      <span className="text-[10px] text-gray-500 font-medium uppercase">{metric.label}</span>
                      <p className="text-lg font-bold text-white mt-1">{metric.value}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Visual Orchestration Timeline Progress */}
              <div className="glass-card p-6">
                <h4 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-6">Agent In-Flight Workflow</h4>
                <div className="relative flex justify-between items-center">
                  {/* Progress Line */}
                  <div className="absolute left-0 right-0 top-1/2 h-0.5 bg-navy-800 -translate-y-1/2 z-0"></div>
                  
                  {[
                    { key: 'alert', label: 'Alert Analysis' },
                    { key: 'log', label: 'Log Parsing' },
                    { key: 'rca', label: 'Root Cause' },
                    { key: 'rag', label: 'Knowledge RAG' },
                    { key: 'resolution', label: 'Resolution Plan' },
                    { key: 'communication', label: 'Executive Report' }
                  ].map((step, idx) => {
                    const status = getStepStatus(step.key, selectedIncident.status);
                    return (
                      <div key={idx} className="flex flex-col items-center z-10">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center border transition-all duration-300 ${
                          status === 'completed' 
                            ? 'bg-neon-green/20 border-neon-green text-neon-green shadow-[0_0_15px_rgba(16,185,129,0.3)]'
                            : status === 'active'
                            ? 'bg-electric-blue/20 border-electric-blue text-electric-blue animate-pulse-glow shadow-[0_0_15px_rgba(59,130,246,0.3)]'
                            : 'bg-navy-950 border-navy-800 text-gray-500'
                        }`}>
                          {status === 'completed' ? <Check className="w-4 h-4" /> : <span className="text-[10px] font-bold">{idx + 1}</span>}
                        </div>
                        <span className="text-[10px] font-medium text-gray-400 mt-2 bg-navy-950 px-2 py-0.5 rounded">
                          {step.label}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* What-If Sandbox (Simulation Panel) */}
              <div className="glass-card p-6">
                <h4 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-4">What-If Remediation Sandbox</h4>
                <p className="text-xs text-gray-400 mb-4">Simulate operational mitigation actions in a predictive SRE sandbox before applying updates.</p>
                <form onSubmit={handleSimulate} className="flex gap-4">
                  <input
                    type="text"
                    placeholder="e.g. Restart Database connection pool, Revert deploy #d8f1e09, Scale replica size to 15"
                    value={simulationQuery}
                    onChange={(e) => setSimulationQuery(e.target.value)}
                    className="flex-1 bg-navy-950 border border-electric-blue/15 rounded-lg px-4 py-2 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-electric-blue transition-colors"
                  />
                  <button
                    type="submit"
                    disabled={simulating || !simulationQuery}
                    className="px-4 py-2 bg-navy-900 border border-electric-blue/30 text-xs font-semibold text-white rounded-lg hover:bg-navy-800 disabled:opacity-50 flex items-center gap-2"
                  >
                    {simulating ? 'Simulating...' : 'Run Simulation'}
                  </button>
                </form>

                {simulationResult && (
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 p-4 rounded-lg bg-navy-950/80 border border-electric-blue/10">
                    <div className="p-3 bg-navy-900/40 rounded border border-electric-blue/5">
                      <span className="text-[9px] uppercase text-gray-500 font-semibold">Success Probability</span>
                      <p className="text-sm font-bold text-neon-green mt-1">{(simulationResult.success_probability * 100).toFixed(0)}%</p>
                    </div>
                    <div className="p-3 bg-navy-900/40 rounded border border-electric-blue/5">
                      <span className="text-[9px] uppercase text-gray-500 font-semibold">Est. Recovery Time</span>
                      <p className="text-sm font-bold text-white mt-1">{simulationResult.recovery_estimate}</p>
                    </div>
                    <div className="p-3 bg-navy-900/40 rounded border border-electric-blue/5">
                      <span className="text-[9px] uppercase text-gray-500 font-semibold">Est. Downtime</span>
                      <p className="text-sm font-bold text-white mt-1">{simulationResult.downtime_estimate}</p>
                    </div>
                    <div className="p-3 bg-navy-900/40 rounded border border-electric-blue/5">
                      <span className="text-[9px] uppercase text-gray-500 font-semibold">Risk Assessment</span>
                      <p className="text-sm font-bold text-orange-400 mt-1">{simulationResult.risk_estimate}</p>
                    </div>
                  </div>
                )}
              </div>
            </>
          )}
        </div>

        {/* Right 4 cols: AI Commander Panel */}
        <div className="lg:col-span-4 space-y-8">
          {selectedIncident && (
            <div className="glass-card p-6 flex flex-col h-full border border-electric-blue/20 bg-gradient-to-b from-navy-950 to-navy-900/80">
              <div className="flex items-center gap-2 border-b border-electric-blue/10 pb-4 mb-4">
                <Cpu className="w-5 h-5 text-electric-blue animate-pulse-glow" />
                <div>
                  <h4 className="text-sm font-bold text-white">AI Commander</h4>
                  <span className="text-[9px] font-mono text-gray-500 uppercase">LangGraph Controller</span>
                </div>
              </div>

              {/* Diagnosis Execution button */}
              {selectedIncident.status === 'Triggered' ? (
                <div className="p-4 rounded-lg bg-navy-950/80 border border-electric-blue/10 flex flex-col items-center justify-center text-center py-8 mb-6">
                  <ShieldAlert className="w-10 h-10 text-orange-500 mb-3 animate-pulse" />
                  <h5 className="text-sm font-semibold text-white mb-1">Untriaged Alert Incident</h5>
                  <p className="text-[11px] text-gray-400 max-w-[200px] mb-4">
                    The LangGraph multi-agent orchestration has not run on this incident.
                  </p>
                  <button
                    onClick={() => handleDiagnose(selectedIncident.id)}
                    disabled={diagnosing}
                    className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-electric-blue hover:bg-electric-glow text-white text-xs font-bold transition-all shadow-[0_0_15px_rgba(59,130,246,0.3)] active:scale-95"
                  >
                    {diagnosing ? (
                      <>
                        <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                        AI Agent Investigating...
                      </>
                    ) : (
                      <>
                        <Play className="w-3.5 h-3.5 fill-current" />
                        Run AI Agent Investigation
                      </>
                    )}
                  </button>
                </div>
              ) : selectedIncident.status === 'Investigating' ? (
                <div className="p-4 rounded-lg bg-navy-950/80 border border-electric-blue/10 flex flex-col items-center justify-center text-center py-8 mb-6">
                  <RefreshCw className="w-10 h-10 text-electric-blue animate-spin mb-3" />
                  <h5 className="text-sm font-semibold text-white mb-1">LangGraph Executing Node</h5>
                  <p className="text-[11px] text-gray-400">Agents are exchanging state context...</p>
                </div>
              ) : (
                <div className="p-4 rounded-lg bg-navy-950/80 border border-neon-green/30 bg-neon-green/5 flex flex-col items-center justify-center text-center py-4 mb-6">
                  <ShieldCheck className="w-8 h-8 text-neon-green mb-2" />
                  <h5 className="text-xs font-semibold text-white">Triaged by AegisOps AI</h5>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-[10px] text-gray-400">Confidence:</span>
                    <span className="text-xs font-bold text-neon-green">{(selectedIncident.confidence_score * 100).toFixed(0)}%</span>
                  </div>
                  <button 
                    onClick={() => handleDiagnose(selectedIncident.id)}
                    className="text-[9px] text-electric-blue hover:underline font-semibold mt-3"
                  >
                    Re-run Diagnostics
                  </button>
                </div>
              )}

              {/* Core findings */}
              {selectedIncident.root_cause && (
                <div className="space-y-4 mb-6">
                  <div>
                    <h5 className="text-xs font-bold text-gray-300 uppercase tracking-wide mb-1.5">Root Cause</h5>
                    <p className="text-xs text-gray-200 bg-navy-950 p-3 rounded-lg border border-electric-blue/5 leading-relaxed font-mono">
                      {selectedIncident.root_cause}
                    </p>
                  </div>
                  
                  <div>
                    <h5 className="text-xs font-bold text-gray-300 uppercase tracking-wide mb-1.5">Anomalies Detected</h5>
                    <ul className="space-y-1.5">
                      {selectedIncident.findings?.slice(0, 3).map((f, idx) => (
                        <li key={idx} className="flex gap-2 text-[11px] text-gray-400 bg-navy-950/30 p-2 rounded border border-electric-blue/5">
                          <span className="text-electric-blue font-bold">#</span>
                          <span>{f}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}

              {/* Live reasoning trace logger */}
              <div className="flex-1 flex flex-col min-h-[220px]">
                <h5 className="text-xs font-bold text-gray-300 uppercase tracking-wide mb-2 flex items-center gap-1.5">
                  <Terminal className="w-3.5 h-3.5 text-electric-blue" />
                  Reasoning Trace log
                </h5>
                <div className="flex-1 bg-navy-950/95 border border-electric-blue/10 rounded-lg p-3 font-mono text-[10px] text-electric-blue overflow-y-auto max-h-[300px]">
                  {selectedIncident.reasoning_trace && selectedIncident.reasoning_trace.length > 0 ? (
                    <div className="space-y-2">
                      {selectedIncident.reasoning_trace.map((log, idx) => (
                        <div key={idx} className="border-b border-navy-900 pb-1.5 last:border-0">
                          <span className="text-neon-purple">[Agent Node]</span> {log}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-gray-600 italic text-center mt-12">
                      No logs in trace buffer. Trigger diagnostics to generate execution loops.
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
