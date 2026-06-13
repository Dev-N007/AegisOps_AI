'use client';

import React, { useEffect, useState } from 'react';
import { Cpu, Clock, Award, Terminal, RefreshCw, Zap, CheckCircle2, Circle } from 'lucide-react';
import { motion } from 'framer-motion';
import { api } from '@/services/api';
import { AgentStatus } from '@/types';

export default function AgentsPage() {
  const [agents, setAgents] = useState<AgentStatus[]>([]);
  const [selectedAgent, setSelectedAgent] = useState<AgentStatus | null>(null);
  const [loading, setLoading] = useState(true);

  const loadAgents = async () => {
    try {
      setLoading(true);
      const data = await api.getAgents();
      setAgents(data);
      if (data.length > 0) {
        // Find if we had a selection previously
        const found = selectedAgent ? data.find(a => a.name === selectedAgent.name) : null;
        setSelectedAgent(found || data[0]);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAgents();
  }, []);

  // Map agent name to SVG coordinate positions on a 600x350 Canvas
  const nodePositions: { [key: string]: { x: number; y: number } } = {
    "Alert Analysis": { x: 80, y: 175 },
    "Log Investigation": { x: 220, y: 80 },
    "Root Cause Analysis": { x: 300, y: 175 },
    "Knowledge Retrieval": { x: 220, y: 270 },
    "Resolution Planning": { x: 440, y: 80 },
    "Executive Reporting": { x: 520, y: 175 }
  };

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex justify-between items-center border-b border-electric-blue/10 pb-6">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">Autonomous Agent Network</h2>
          <p className="text-gray-400 text-sm">Multi-agent SRE orchestration cluster status.</p>
        </div>
        <button 
          onClick={loadAgents} 
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-navy-900 border border-electric-blue/20 hover:bg-navy-800 text-sm text-gray-300 transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          Sync Agents
        </button>
      </div>

      {/* SVG Agent Graph Visualization Panel */}
      <div className="glass-card p-6 bg-navy-900/30 flex flex-col items-center">
        <h4 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-6 self-start flex items-center gap-2">
          <Zap className="w-4 h-4 text-electric-blue" />
          LangGraph state orchestration graph
        </h4>
        
        <div className="relative w-full max-w-[700px] aspect-[700/350] border border-electric-blue/10 bg-navy-950/70 rounded-xl overflow-hidden p-4">
          <svg className="w-full h-full" viewBox="0 0 600 350">
            {/* SVG Connecting Flow Lines with glowing dasharray */}
            {/* Alert -> Log */}
            <path d="M 80 175 Q 150 80 220 80" fill="none" stroke="rgba(59, 130, 246, 0.2)" strokeWidth="2" />
            <path d="M 80 175 Q 150 80 220 80" fill="none" stroke="#3b82f6" strokeWidth="2.5" 
                  strokeDasharray="10 40" strokeDashoffset="0" className="animate-[dash_6s_linear_infinite]" />
            
            {/* Log -> RCA */}
            <path d="M 220 80 Q 260 120 300 175" fill="none" stroke="rgba(59, 130, 246, 0.2)" strokeWidth="2" />
            <path d="M 220 80 Q 260 120 300 175" fill="none" stroke="#3b82f6" strokeWidth="2.5" 
                  strokeDasharray="10 40" strokeDashoffset="0" className="animate-[dash_6s_linear_infinite]" />
            
            {/* Alert -> RAG (Fallback logic paths if needed, or straight lines) */}
            {/* RCA -> Knowledge */}
            <path d="M 300 175 Q 260 220 220 270" fill="none" stroke="rgba(59, 130, 246, 0.2)" strokeWidth="2" />
            <path d="M 300 175 Q 260 220 220 270" fill="none" stroke="#3b82f6" strokeWidth="2.5" 
                  strokeDasharray="10 40" strokeDashoffset="0" className="animate-[dash_6s_linear_infinite]" />

            {/* Knowledge -> Resolution */}
            <path d="M 220 270 Q 330 175 440 80" fill="none" stroke="rgba(59, 130, 246, 0.2)" strokeWidth="2" />
            <path d="M 220 270 Q 330 175 440 80" fill="none" stroke="#3b82f6" strokeWidth="2.5" 
                  strokeDasharray="10 40" strokeDashoffset="0" className="animate-[dash_6s_linear_infinite]" />

            {/* Resolution -> Communication */}
            <path d="M 440 80 Q 480 125 520 175" fill="none" stroke="rgba(59, 130, 246, 0.2)" strokeWidth="2" />
            <path d="M 440 80 Q 480 125 520 175" fill="none" stroke="#3b82f6" strokeWidth="2.5" 
                  strokeDasharray="10 40" strokeDashoffset="0" className="animate-[dash_6s_linear_infinite]" />

            {/* SVG Interactive Node Dots */}
            {Object.keys(nodePositions).map((name) => {
              const pos = nodePositions[name];
              const isSelected = selectedAgent?.name === name;
              const agentData = agents.find(a => a.name === name);
              const isExecuting = agentData?.status === 'executing';
              
              return (
                <g 
                  key={name} 
                  transform={`translate(${pos.x}, ${pos.y})`}
                  className="cursor-pointer"
                  onClick={() => {
                    const found = agents.find(a => a.name === name);
                    if (found) setSelectedAgent(found);
                  }}
                >
                  {/* Outer glow aura */}
                  <circle 
                    r={isSelected ? "18" : "12"} 
                    className={`transition-all duration-300 ${
                      isExecuting 
                        ? 'fill-electric-blue/20 stroke-electric-blue animate-ping' 
                        : isSelected
                        ? 'fill-neon-purple/20 stroke-neon-purple animate-pulse-slow' 
                        : 'fill-navy-950 stroke-electric-blue/20'
                    }`} 
                    strokeWidth="1.5" 
                  />
                  {/* Inner node dot */}
                  <circle 
                    r="8" 
                    className={`transition-all duration-300 ${
                      isExecuting 
                        ? 'fill-electric-blue shadow-lg' 
                        : isSelected 
                        ? 'fill-neon-purple' 
                        : 'fill-navy-800 hover:fill-navy-700'
                    }`} 
                  />
                  {/* Label tag */}
                  <text 
                    y="25" 
                    textAnchor="middle" 
                    className={`text-[9px] font-semibold tracking-wide select-none transition-colors ${
                      isSelected ? 'fill-neon-purple font-bold' : 'fill-gray-400'
                    }`}
                  >
                    {name.split(' ')[0]}
                  </text>
                </g>
              );
            })}
          </svg>

          {/* SVG Keyframe Animation for moving neon dash */}
          <style jsx global>{`
            @keyframes dash {
              to {
                stroke-dashoffset: -200px;
              }
            }
          `}</style>
        </div>
      </div>

      {/* Details Row */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Selected Agent Stats (7 cols) */}
        {selectedAgent && (
          <div className="lg:col-span-7 space-y-6">
            <div className="glass-card p-6">
              <div className="flex justify-between items-start border-b border-electric-blue/10 pb-4 mb-6">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-navy-900 border border-electric-blue/10 rounded-lg text-electric-blue">
                    <Cpu className="w-5 h-5 text-neon-purple" />
                  </div>
                  <div>
                    <h3 className="font-bold text-white text-base">{selectedAgent.name} Agent</h3>
                    <span className="text-[10px] text-gray-500 font-mono">IncidentState Reader/Writer</span>
                  </div>
                </div>
                <div className="flex items-center gap-2 px-3 py-1 rounded bg-navy-950 border border-electric-blue/10">
                  <span className={`w-1.5 h-1.5 rounded-full ${
                    selectedAgent.status === 'executing' ? 'bg-electric-blue animate-pulse' : 'bg-neon-green'
                  }`}></span>
                  <span className="text-[10px] font-semibold text-gray-300 uppercase tracking-wider">
                    {selectedAgent.status}
                  </span>
                </div>
              </div>

              {/* Stats Grid */}
              <div className="grid grid-cols-3 gap-6 mb-6">
                <div className="p-4 rounded-xl bg-navy-950 border border-electric-blue/5">
                  <div className="flex items-center gap-1.5 text-gray-500">
                    <Clock className="w-3.5 h-3.5" />
                    <span className="text-[10px] uppercase font-semibold">Avg Response</span>
                  </div>
                  <p className="text-base font-bold text-white mt-1">{selectedAgent.avg_response_time}</p>
                </div>
                <div className="p-4 rounded-xl bg-navy-950 border border-electric-blue/5">
                  <div className="flex items-center gap-1.5 text-gray-500">
                    <Award className="w-3.5 h-3.5" />
                    <span className="text-[10px] uppercase font-semibold">Accuracy</span>
                  </div>
                  <p className="text-base font-bold text-neon-purple mt-1">{selectedAgent.confidence}</p>
                </div>
                <div className="p-4 rounded-xl bg-navy-950 border border-electric-blue/5">
                  <div className="flex items-center gap-1.5 text-gray-500">
                    <Terminal className="w-3.5 h-3.5" />
                    <span className="text-[10px] uppercase font-semibold">Total Runs</span>
                  </div>
                  <p className="text-base font-bold text-white mt-1">{selectedAgent.total_executions}</p>
                </div>
              </div>

              {/* Current Task */}
              <div className="p-4 rounded-xl bg-navy-950 border border-electric-blue/5">
                <span className="text-[10px] text-gray-500 uppercase font-semibold block mb-1">Current Task Context</span>
                <p className="text-xs text-gray-300 font-mono leading-relaxed">{selectedAgent.current_task}</p>
              </div>
            </div>
          </div>
        )}

        {/* Execution Log list (5 cols) */}
        {selectedAgent && (
          <div className="lg:col-span-5">
            <div className="glass-card p-6 h-full flex flex-col">
              <h4 className="text-xs font-bold text-gray-300 uppercase tracking-wide mb-4 flex items-center gap-1.5">
                <Terminal className="w-3.5 h-3.5 text-electric-blue" />
                Execution History Logs
              </h4>
              <div className="flex-1 overflow-y-auto space-y-3 max-h-[280px]">
                {selectedAgent.history && selectedAgent.history.length > 0 ? (
                  selectedAgent.history.map((log, index) => (
                    <div key={index} className="p-3 bg-navy-950/70 border border-electric-blue/5 rounded-lg flex justify-between items-center text-[10px] font-mono">
                      <div>
                        <span className="text-electric-blue">{log.incident_id}</span>
                        <p className="text-gray-500 mt-0.5">{log.timestamp}</p>
                      </div>
                      <div className="text-right">
                        <span className="text-neon-purple font-semibold">{log.duration}</span>
                        <p className="text-neon-green mt-0.5">{log.status}</p>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-gray-600 italic text-center py-12">
                    No logged execution runs found for this agent.
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
