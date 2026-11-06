import React from 'react';
import { MessageSquarePlus, BarChart3, ShieldCheck } from 'lucide-react';

export default function Header({ tabActiva, onCambiarTab }) {
  return (
    <header className="h-16 bg-[#0a0f19] border-b border-slate-800 flex items-center justify-between px-6 z-20">
      {/* Brand */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-500 to-teal-600 flex items-center justify-center text-white text-xl shadow-lg shadow-emerald-950/40 font-black">
          ⚽
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-base font-extrabold text-white tracking-tight">
              Tribuna Global
            </h1>
            <span className="text-[10px] bg-emerald-500/10 text-emerald-400 font-bold px-2 py-0.5 rounded-full border border-emerald-500/20">
              v1.0
            </span>
          </div>
          <p className="text-xs text-slate-400">
            Percepción de Futbolistas mediante LangChain
          </p>
        </div>
      </div>

      {/* Tabs Switcher */}
      <div className="flex bg-[#141b2a] p-1 rounded-xl border border-slate-700/80">
        <button
          onClick={() => onCambiarTab('chat')}
          className={`flex items-center gap-2 px-4 py-1.5 rounded-lg text-xs font-bold transition-all ${
            tabActiva === 'chat'
              ? 'bg-emerald-600 text-white shadow-md shadow-emerald-950/30'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <MessageSquarePlus className="w-4 h-4" />
          <span>Emitir Opinión</span>
        </button>

        <button
          onClick={() => onCambiarTab('consultas')}
          className={`flex items-center gap-2 px-4 py-1.5 rounded-lg text-xs font-bold transition-all ${
            tabActiva === 'consultas'
              ? 'bg-emerald-600 text-white shadow-md shadow-emerald-950/30'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <BarChart3 className="w-4 h-4" />
          <span>Consultar Opiniones</span>
        </button>
      </div>

      {/* Badge Estado */}
      <div className="hidden sm:flex items-center gap-2 text-xs font-medium text-slate-400 bg-slate-900/80 px-3 py-1.5 rounded-xl border border-slate-800">
        <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
        <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
        <span>LangChain LCEL Activo</span>
      </div>
    </header>
  );
}

