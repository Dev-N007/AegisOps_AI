'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Shield, Terminal, Cpu, BarChart2, Settings, Radio } from 'lucide-react';

export default function Sidebar() {
  const pathname = usePathname();

  const links = [
    { name: 'Dashboard', href: '/', icon: Radio },
    { name: 'Incidents', href: '/incidents', icon: Shield },
    { name: 'AI SRE Agents', href: '/agents', icon: Cpu },
    { name: 'Analytics', href: '/analytics', icon: BarChart2 },
    { name: 'Settings', href: '/settings', icon: Settings },
  ];

  return (
    <aside className="w-64 border-r border-electric-blue/15 bg-navy-950/85 backdrop-blur-xl h-screen flex flex-col fixed left-0 top-0 z-30">
      {/* Brand Header */}
      <div className="h-16 flex items-center px-6 gap-3 border-b border-electric-blue/10">
        <div className="p-2 bg-gradient-to-tr from-electric-blue to-neon-purple rounded-lg animate-pulse-slow">
          <Terminal className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="font-bold text-white tracking-wide text-lg bg-clip-text text-transparent bg-gradient-to-r from-white via-gray-200 to-electric-blue">
            AegisOps AI
          </h1>
          <span className="text-[10px] text-electric-blue font-semibold uppercase tracking-wider glow-text-blue">
            Autonomous SRE
          </span>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-4 py-6 space-y-1">
        {links.map((link) => {
          const Icon = link.icon;
          const isActive = pathname === link.href;
          return (
            <Link
              key={link.href}
              href={link.href}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 ${
                isActive
                  ? 'bg-electric-blue/15 text-electric-blue border-l-2 border-electric-blue shadow-[0_0_15px_rgba(59,130,246,0.1)]'
                  : 'text-gray-400 hover:bg-navy-900/50 hover:text-gray-200'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-electric-blue' : 'text-gray-400 group-hover:text-gray-200'}`} />
              {link.name}
            </Link>
          );
        })}
      </nav>

      {/* Footer Info */}
      <div className="p-4 border-t border-electric-blue/10 bg-navy-900/20">
        <div className="flex items-center gap-3">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-neon-green opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-neon-green"></span>
          </span>
          <div className="text-[11px] text-gray-500">
            System Status: <span className="text-neon-green font-semibold">Active</span>
          </div>
        </div>
        <div className="text-[9px] text-gray-600 mt-2">
          MVP v1.0.0 • Prompt Surfers
        </div>
      </div>
    </aside>
  );
}
