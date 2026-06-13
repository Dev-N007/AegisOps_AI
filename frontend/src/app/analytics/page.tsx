'use client';

import React, { useEffect, useState } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, 
  ResponsiveContainer, AreaChart, Area, PieChart, Pie, Cell, Legend 
} from 'recharts';
import { RefreshCw, Activity, Clock, ShieldCheck, Award } from 'lucide-react';
import { api } from '@/services/api';
import { AnalyticsData } from '@/types';

export default function AnalyticsPage() {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [mounted, setMounted] = useState(false);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      const res = await api.getAnalytics();
      setData(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setMounted(true);
    loadAnalytics();
  }, []);

  if (!mounted) return null;

  const COLORS = ['#3b82f6', '#a855f7', '#06b6d4', '#ef4444', '#10b981'];

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex justify-between items-center border-b border-electric-blue/10 pb-6">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">Incident Analytics</h2>
          <p className="text-gray-400 text-sm">System performance metrics and SRE telemetry.</p>
        </div>
        <button 
          onClick={loadAnalytics} 
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-navy-900 border border-electric-blue/20 hover:bg-navy-800 text-sm text-gray-300 transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          Refresh Stats
        </button>
      </div>

      {loading || !data ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {[1, 2, 3, 4].map(n => (
            <div key={n} className="h-80 bg-navy-900/30 border border-electric-blue/5 rounded-xl animate-pulse"></div>
          ))}
        </div>
      ) : (
        <>
          {/* Top KPI row */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {[
              { label: 'Active Incidents', value: data.kpis.active_incidents, icon: Activity, color: 'text-neon-red' },
              { label: 'Critical Tickets', value: data.kpis.critical_alerts, icon: ShieldCheck, color: 'text-orange-400' },
              { label: 'Mean Time to Resolve', value: data.kpis.mttr, icon: Clock, color: 'text-neon-cyan' },
              { label: 'AI Prediction Accuracy', value: data.kpis.ai_confidence, icon: Award, color: 'text-neon-purple' }
            ].map((kpi, idx) => {
              const Icon = kpi.icon;
              return (
                <div key={idx} className="glass-card p-6 flex justify-between items-center bg-navy-900/20">
                  <div>
                    <span className="text-[10px] text-gray-400 font-semibold uppercase tracking-wider">{kpi.label}</span>
                    <p className="text-2xl font-bold text-white mt-1">{kpi.value}</p>
                  </div>
                  <div className={`p-3 rounded-lg bg-navy-950 border border-electric-blue/10 ${kpi.color}`}>
                    <Icon className="w-5 h-5" />
                  </div>
                </div>
              );
            })}
          </div>

          {/* Charts grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            
            {/* Chart 1: Incident Trends */}
            <div className="glass-card p-6">
              <h4 className="text-xs font-bold text-gray-300 uppercase tracking-wider mb-6">Incident & Resolution Trends</h4>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={data.trends} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <defs>
                      <linearGradient id="colorIncidents" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#ef4444" stopOpacity={0.2}/>
                        <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                      </linearGradient>
                      <linearGradient id="colorResolved" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.2}/>
                        <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1d264f" opacity={0.3} />
                    <XAxis dataKey="date" stroke="#9ca3af" fontSize={10} tickLine={false} />
                    <YAxis stroke="#9ca3af" fontSize={10} tickLine={false} />
                    <Tooltip contentStyle={{ backgroundColor: '#0a0e22', borderColor: '#1d264f', fontSize: '11px', color: '#fff' }} />
                    <Area type="monotone" dataKey="incidents" name="Triggered" stroke="#ef4444" strokeWidth={2} fillOpacity={1} fill="url(#colorIncidents)" />
                    <Area type="monotone" dataKey="resolved" name="Resolved" stroke="#10b981" strokeWidth={2} fillOpacity={1} fill="url(#colorResolved)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Chart 2: Root Causes */}
            <div className="glass-card p-6">
              <h4 className="text-xs font-bold text-gray-300 uppercase tracking-wider mb-6">Root Cause Classification</h4>
              <div className="h-64 flex items-center justify-between">
                <ResponsiveContainer width="55%" height="100%">
                  <PieChart>
                    <Pie
                      data={data.root_causes}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={80}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {data.root_causes.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip contentStyle={{ backgroundColor: '#0a0e22', borderColor: '#1d264f', fontSize: '11px', color: '#fff' }} />
                  </PieChart>
                </ResponsiveContainer>
                <div className="w-[40%] space-y-3 pr-4">
                  {data.root_causes.map((entry, index) => (
                    <div key={entry.name} className="flex items-center gap-2">
                      <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: COLORS[index % COLORS.length] }}></span>
                      <div className="text-[11px] text-gray-300 font-medium truncate">
                        {entry.name} ({entry.value})
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Chart 3: MTTM by Category */}
            <div className="glass-card p-6">
              <h4 className="text-xs font-bold text-gray-300 uppercase tracking-wider mb-6">Mitigation Duration (mins)</h4>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={data.resolution_times} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1d264f" opacity={0.3} />
                    <XAxis dataKey="category" stroke="#9ca3af" fontSize={9} tickLine={false} />
                    <YAxis stroke="#9ca3af" fontSize={10} tickLine={false} />
                    <Tooltip contentStyle={{ backgroundColor: '#0a0e22', borderColor: '#1d264f', fontSize: '11px', color: '#fff' }} />
                    <Bar dataKey="time" name="Minutes" fill="#3b82f6" radius={[4, 4, 0, 0]}>
                      {data.resolution_times.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Chart 4: Agent Performance Speeds */}
            <div className="glass-card p-6">
              <h4 className="text-xs font-bold text-gray-300 uppercase tracking-wider mb-6">Agent Node Latency (seconds)</h4>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart layout="vertical" data={data.agent_speeds} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1d264f" opacity={0.3} />
                    <XAxis type="number" stroke="#9ca3af" fontSize={10} tickLine={false} />
                    <YAxis dataKey="agent" type="category" stroke="#9ca3af" fontSize={9} tickLine={false} />
                    <Tooltip contentStyle={{ backgroundColor: '#0a0e22', borderColor: '#1d264f', fontSize: '11px', color: '#fff' }} />
                    <Bar dataKey="duration" name="Seconds" fill="#a855f7" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

          </div>
        </>
      )}
    </div>
  );
}
