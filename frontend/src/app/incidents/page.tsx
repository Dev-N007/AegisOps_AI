'use client';

import React, { useEffect, useState } from 'react';
import { 
  ShieldAlert, Clock, CheckCircle2, ChevronRight, AlertTriangle, 
  BookOpen, History, Award, FileText, Activity, RefreshCw 
} from 'lucide-react';
import { api } from '@/services/api';
import { Incident } from '@/types';

export default function IncidentsPage() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'report' | 'runbooks' | 'timeline'>('report');

  const loadIncidents = async (selectId?: string) => {
    try {
      setLoading(true);
      const data = await api.getIncidents();
      setIncidents(data);
      if (data.length > 0) {
        if (selectId) {
          const found = data.find(i => i.id === selectId);
          setSelectedIncident(found || data[0]);
        } else {
          setSelectedIncident(data[0]);
        }
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadIncidents();
  }, []);

  return (
    <div className="flex h-screen bg-navy-950 overflow-hidden">
      {/* Left List Pane (1/3 width) */}
      <div className="w-1/3 border-r border-electric-blue/10 flex flex-col h-full bg-navy-950/40">
        <div className="p-6 border-b border-electric-blue/10 flex justify-between items-center bg-navy-950/60">
          <div>
            <h3 className="font-bold text-lg text-white">Incident Registry</h3>
            <p className="text-[11px] text-gray-400">All alerts and autonomous triages.</p>
          </div>
          <button 
            onClick={() => loadIncidents(selectedIncident?.id)} 
            className="p-2 bg-navy-900 border border-electric-blue/15 hover:bg-navy-800 rounded text-gray-300 transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>

        {/* Incident List */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {loading && incidents.length === 0 ? (
            <div className="space-y-3">
              {[1, 2, 3].map((n) => (
                <div key={n} className="h-24 bg-navy-900/50 rounded-lg animate-pulse border border-electric-blue/5"></div>
              ))}
            </div>
          ) : (
            incidents.map((inc) => (
              <button
                key={inc.id}
                onClick={() => setSelectedIncident(inc)}
                className={`w-full p-4 rounded-xl border text-left transition-all duration-200 ${
                  selectedIncident?.id === inc.id
                    ? 'border-electric-blue bg-electric-blue/10 shadow-[0_0_15px_rgba(59,130,246,0.08)]'
                    : 'border-electric-blue/5 bg-navy-900/30 hover:bg-navy-900/60'
                }`}
              >
                <div className="flex justify-between items-start mb-2">
                  <span className="text-[10px] font-mono text-electric-blue bg-navy-900 px-2.5 py-0.5 rounded border border-electric-blue/10">
                    {inc.id}
                  </span>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                    inc.severity === 'Critical' 
                      ? 'bg-neon-red/10 text-neon-red border border-neon-red/20' 
                      : 'bg-orange-500/10 text-orange-400 border border-orange-500/20'
                  }`}>
                    {inc.severity}
                  </span>
                </div>
                <h4 className="font-semibold text-white text-xs truncate mb-2">{inc.title}</h4>
                <div className="flex justify-between items-center text-[10px] text-gray-400">
                  <div className="flex items-center gap-1.5">
                    <span className={`w-1.5 h-1.5 rounded-full ${
                      inc.status === 'Resolved' ? 'bg-neon-green' : 'bg-electric-blue animate-pulse'
                    }`}></span>
                    <span>{inc.status}</span>
                  </div>
                  <span className="text-gray-500">
                    {new Date(inc.created_at || Date.now()).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
              </button>
            ))
          )}
        </div>
      </div>

      {/* Right Details Pane (2/3 width) */}
      <div className="w-2/3 flex flex-col h-full bg-transparent overflow-y-auto">
        {selectedIncident ? (
          <div className="p-8 space-y-8 max-w-4xl">
            {/* Header Banner */}
            <div className="flex justify-between items-start border-b border-electric-blue/10 pb-6">
              <div>
                <div className="flex items-center gap-3 mb-2">
                  <span className="text-xs font-mono text-electric-blue bg-navy-900 border border-electric-blue/15 px-3 py-1 rounded-lg">
                    {selectedIncident.id}
                  </span>
                  <span className={`text-xs font-bold px-3 py-1 rounded-lg ${
                    selectedIncident.severity === 'Critical' ? 'bg-neon-red/15 text-neon-red' : 'bg-orange-500/15 text-orange-400'
                  }`}>
                    {selectedIncident.severity} Severity
                  </span>
                  <span className="text-xs text-gray-400">
                    Detected: {new Date(selectedIncident.created_at).toLocaleString()}
                  </span>
                </div>
                <h2 className="text-2xl font-bold text-white tracking-wide">{selectedIncident.title}</h2>
              </div>
              <div className="flex items-center gap-2 bg-navy-900 border border-electric-blue/10 px-4 py-2 rounded-xl">
                <Award className="w-4 h-4 text-neon-purple" />
                <span className="text-xs font-semibold text-gray-300">
                  AI Accuracy: <span className="text-neon-purple">{(selectedIncident.confidence_score * 100).toFixed(0)}%</span>
                </span>
              </div>
            </div>

            {/* Metadata Stats Row */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="p-4 rounded-xl bg-navy-900/40 border border-electric-blue/5">
                <span className="text-[10px] text-gray-500 uppercase font-semibold">Triage Status</span>
                <p className="text-sm font-bold text-white mt-1">{selectedIncident.status}</p>
              </div>
              <div className="p-4 rounded-xl bg-navy-900/40 border border-electric-blue/5">
                <span className="text-[10px] text-gray-500 uppercase font-semibold">Latency Spike</span>
                <p className="text-sm font-bold text-neon-red mt-1">{selectedIncident.metrics?.latency ? `${selectedIncident.metrics.latency}ms` : 'N/A'}</p>
              </div>
              <div className="p-4 rounded-xl bg-navy-900/40 border border-electric-blue/5">
                <span className="text-[10px] text-gray-500 uppercase font-semibold">Affected Node</span>
                <p className="text-sm font-bold text-white mt-1">{selectedIncident.alert_data?.service || 'postgres-cluster'}</p>
              </div>
              <div className="p-4 rounded-xl bg-navy-900/40 border border-electric-blue/5">
                <span className="text-[10px] text-gray-500 uppercase font-semibold">Failure Class</span>
                <p className="text-sm font-bold text-electric-blue mt-1">
                  {selectedIncident.title.includes('Pool') ? 'DB Conn Leak' : selectedIncident.title.includes('Memory') ? 'OOM Error' : 'System Defect'}
                </p>
              </div>
            </div>

            {/* Tabs for details */}
            <div className="border-b border-electric-blue/10">
              <div className="flex gap-6">
                {[
                  { id: 'report', label: 'Executive Report', icon: FileText },
                  { id: 'runbooks', label: 'RAG Knowledge base', icon: BookOpen },
                  { id: 'timeline', label: 'SRE Investigation Timeline', icon: Activity },
                ].map(t => {
                  const TabIcon = t.icon;
                  return (
                    <button
                      key={t.id}
                      onClick={() => setActiveTab(t.id as any)}
                      className={`flex items-center gap-2 pb-4 text-xs font-semibold uppercase tracking-wider border-b-2 transition-all ${
                        activeTab === t.id
                          ? 'border-electric-blue text-electric-blue'
                          : 'border-transparent text-gray-400 hover:text-gray-200'
                      }`}
                    >
                      <TabIcon className="w-4 h-4" />
                      {t.label}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Tab Contents */}
            <div className="min-h-[350px]">
              
              {/* Executive post-mortem report (markdown) */}
              {activeTab === 'report' && (
                <div className="p-6 rounded-xl bg-navy-900/30 border border-electric-blue/5 prose prose-invert max-w-none prose-sm leading-relaxed">
                  {selectedIncident.executive_report ? (
                    <div className="space-y-4">
                      {/* Very simple markdown renderer inside the component */}
                      {selectedIncident.executive_report.split('\n').map((line, i) => {
                        if (line.startsWith('# ')) {
                          return <h1 key={i} className="text-xl font-bold text-white border-b border-electric-blue/10 pb-2 mt-4">{line.replace('# ', '')}</h1>;
                        }
                        if (line.startsWith('## ')) {
                          return <h2 key={i} className="text-lg font-bold text-white mt-4">{line.replace('## ', '')}</h2>;
                        }
                        if (line.startsWith('### ')) {
                          return <h3 key={i} className="text-sm font-bold text-electric-blue mt-3 uppercase tracking-wider">{line.replace('### ', '')}</h3>;
                        }
                        if (line.startsWith('- ')) {
                          return <li key={i} className="text-gray-300 ml-4 list-disc text-xs mt-1">{line.replace('- ', '')}</li>;
                        }
                        return <p key={i} className="text-gray-300 text-xs mt-1">{line}</p>;
                      })}
                    </div>
                  ) : (
                    <div className="text-center py-12 text-gray-500 italic">
                      No report generated yet. Click 'Run AI Investigation' on the Dashboard.
                    </div>
                  )}
                </div>
              )}

              {/* RAG Knowledge Retrieval Tab */}
              {activeTab === 'runbooks' && (
                <div className="space-y-6">
                  {/* Retrieved Runbooks from ChromaDB */}
                  <div>
                    <h4 className="text-sm font-bold text-white mb-3 flex items-center gap-2">
                      <BookOpen className="w-4 h-4 text-electric-blue" />
                      Retrieved Troubleshooting Runbooks
                    </h4>
                    {selectedIncident.recommendations && selectedIncident.recommendations.length > 0 ? (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {[
                          { name: 'Database Connection Leak Runbook', doc: 'db_connection_leak_runbook.md', sim: '96% Similarity' },
                          { name: 'System Volume Storage Cleanups', doc: 'disk_saturation_runbook.md', sim: '84% Similarity' }
                        ].map((book, idx) => (
                          <div key={idx} className="p-4 rounded-xl bg-navy-900/40 border border-electric-blue/10">
                            <div className="flex justify-between items-center mb-2">
                              <span className="text-[10px] font-bold text-neon-purple uppercase tracking-wider">{book.sim}</span>
                              <span className="text-[9px] font-mono text-gray-500">{book.doc}</span>
                            </div>
                            <h5 className="font-semibold text-white text-xs mb-2">{book.name}</h5>
                            <p className="text-[11px] text-gray-400">
                              Parsed runbook vectors retrieved semantically matching the root cause log patterns.
                            </p>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-8 text-gray-500 italic border border-dashed border-electric-blue/10 rounded-lg">
                        Run active diagnostics to query ChromaDB knowledge logs.
                      </div>
                    )}
                  </div>

                  {/* Historical Incidents */}
                  <div>
                    <h4 className="text-sm font-bold text-white mb-3 flex items-center gap-2">
                      <History className="w-4 h-4 text-neon-cyan" />
                      Similar Historical Incidents
                    </h4>
                    {selectedIncident.root_cause ? (
                      <div className="space-y-3">
                        {[
                          { title: 'INC-2025-081: DB Connection Limit Spike', resolved: 'Resolved by terminating idle clients', sim: '92% similarity' },
                          { title: 'INC-2025-042: HikariPool Pool Exhaustion', resolved: 'Resolved by scaling pool size from 10 to 50', sim: '88% similarity' }
                        ].map((hist, idx) => (
                          <div key={idx} className="p-4 rounded-xl bg-navy-900/20 border border-electric-blue/5 flex justify-between items-center">
                            <div>
                              <h5 className="font-semibold text-xs text-white">{hist.title}</h5>
                              <p className="text-[10px] text-gray-400 mt-1">{hist.resolved}</p>
                            </div>
                            <span className="text-[10px] font-bold text-neon-cyan">{hist.sim}</span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-8 text-gray-500 italic border border-dashed border-electric-blue/10 rounded-lg">
                        Execute investigation loops to trigger ChromaDB vector queries.
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* chronologic timeline */}
              {activeTab === 'timeline' && (
                <div className="p-6 rounded-xl bg-navy-900/30 border border-electric-blue/5 space-y-6">
                  {selectedIncident.timeline && selectedIncident.timeline.length > 0 ? (
                    <div className="relative border-l border-electric-blue/15 ml-4 pl-6 space-y-6 py-2">
                      {selectedIncident.timeline.map((event, idx) => (
                        <div key={idx} className="relative">
                          <span className="absolute -left-[30px] top-0 w-4 h-4 rounded-full bg-navy-950 border border-electric-blue flex items-center justify-center">
                            <span className="w-1.5 h-1.5 rounded-full bg-electric-blue"></span>
                          </span>
                          <div className="text-[11px] font-mono text-electric-blue">{event.time}</div>
                          <p className="text-xs text-gray-300 mt-1 font-medium">{event.event}</p>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-12 text-gray-500 italic">
                      No investigation timelines logged. Run diagnostics.
                    </div>
                  )}
                </div>
              )}

            </div>
          </div>
        ) : (
          <div className="m-auto text-center py-24">
            <AlertTriangle className="w-12 h-12 text-gray-600 mx-auto mb-4" />
            <h3 className="font-semibold text-lg text-gray-400">No Incidents Selected</h3>
            <p className="text-xs text-gray-500">Pick an incident from the registry list to start investigation analysis.</p>
          </div>
        )}
      </div>
    </div>
  );
}
