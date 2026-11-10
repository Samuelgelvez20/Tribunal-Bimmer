import React from 'react';
import { MessageSquarePlus, BarChart3, ShieldCheck, Gauge } from 'lucide-react';

export default function Header({ tabActiva, onCambiarTab }) {
  return (
    <header className="h-16 bg-[#0A0D12] border-b border-[#1E2638] flex items-center justify-between px-6 z-20 select-none relative">
      {/* Franja superior icónica M Badge */}
      <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-[#0096D6] via-[#00205B] to-[#E00034]"></div>

      {/* Marca / Branding */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-full bg-[#121620] border border-[#1E2638] flex items-center justify-center relative overflow-hidden shadow-lg p-0.5 group hover:border-[#0096D6] transition-colors">
          <img src="/bmw-logo.svg" alt="BMW Logo" className="w-full h-full object-contain" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-base font-extrabold text-white tracking-wide flex items-center gap-2">
              Tribunal Bimmer
              <span className="font-black italic text-xs tracking-tighter text-[#0096D6]">///M</span>
            </h1>
            <span className="text-[10px] bg-[#0096D6]/15 text-[#0096D6] font-bold px-2 py-0.5 rounded-full border border-[#0096D6]/30">
              BMW M Series
            </span>
          </div>
          <p className="text-xs text-[#94A3B8]">
            Análisis y Clasificación de Sentimiento con LangChain LCEL
          </p>
        </div>
      </div>

      {/* Selector de Pestañas */}
      <div className="flex bg-[#121620] p-1 rounded-xl border border-[#1E2638]">
        <button
          onClick={() => onCambiarTab('chat')}
          className={`flex items-center gap-2 px-4 py-1.5 rounded-lg text-xs font-bold transition-all ${
            tabActiva === 'chat'
              ? 'bg-[#0096D6] text-white shadow-md shadow-[#0096D6]/30'
              : 'text-[#94A3B8] hover:text-white'
          }`}
        >
          <MessageSquarePlus className="w-4 h-4" />
          <span>Emitir Juicio</span>
        </button>

        <button
          onClick={() => onCambiarTab('consultas')}
          className={`flex items-center gap-2 px-4 py-1.5 rounded-lg text-xs font-bold transition-all ${
            tabActiva === 'consultas'
              ? 'bg-[#0096D6] text-white shadow-md shadow-[#0096D6]/30'
              : 'text-[#94A3B8] hover:text-white'
          }`}
        >
          <BarChart3 className="w-4 h-4" />
          <span>Consultar Veredictos</span>
        </button>
      </div>

      {/* Estado del Sistema */}
      <div className="hidden sm:flex items-center gap-2 text-xs font-medium text-[#94A3B8] bg-[#121620] px-3 py-1.5 rounded-xl border border-[#1E2638]">
        <span className="w-2 h-2 rounded-full bg-[#0096D6] animate-pulse"></span>
        <ShieldCheck className="w-3.5 h-3.5 text-[#0096D6]" />
        <span>LangChain LCEL Activo</span>
      </div>
    </header>
  );
}
