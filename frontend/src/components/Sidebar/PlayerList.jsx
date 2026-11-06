import React, { useState } from 'react';
import { Search, UserCheck } from 'lucide-react';

const BANDERAS = {
  "Argentina": "🇦🇷",
  "Portugal": "🇵🇹",
  "Brasil": "🇧🇷",
  "Francia": "🇫🇷",
  "Noruega": "🇳🇴",
  "Egipto": "🇪🇬",
  "Polonia": "🇵🇱",
  "Croacia": "🇭🇷",
  "Bélgica": "🇧🇪",
  "Uruguay": "🇺🇾",
  "Colombia": "🇨🇴",
  "Corea del Sur": "🇰🇷",
  "Senegal": "🇸🇳",
};

export default function PlayerList({ jugadores, jugadorSeleccionado, onSeleccionarJugador }) {
  const [busqueda, setBusqueda] = useState('');

  const filtrados = jugadores.filter(j => 
    j.nombre.toLowerCase().includes(busqueda.toLowerCase()) ||
    j.pais.toLowerCase().includes(busqueda.toLowerCase())
  );

  return (
    <aside className="w-80 bg-[#0d131f] border-r border-slate-800 flex flex-col h-full select-none">
      {/* Header Sidebar */}
      <div className="p-4 border-b border-slate-800/80">
        <div className="flex items-center gap-2 mb-3">
          <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 font-bold">
            ⚽
          </div>
          <div>
            <h2 className="font-bold text-white text-base leading-tight">Catálogo Oficial</h2>
            <p className="text-xs text-slate-400">20 Futbolistas Leyenda</p>
          </div>
        </div>

        {/* Buscador */}
        <div className="relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Buscar por nombre o país..."
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
            className="w-full bg-[#141b2a] border border-slate-700/80 rounded-lg pl-9 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-emerald-500 transition-colors"
          />
        </div>
      </div>

      {/* Lista scrolleable */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {filtrados.map((j) => {
          const esActivo = jugadorSeleccionado?.id === j.id;
          const bandera = BANDERAS[j.pais] || '⚽';
          return (
            <button
              key={j.id}
              onClick={() => onSeleccionarJugador(j)}
              className={`w-full flex items-center justify-between p-2.5 rounded-xl text-left transition-all duration-150 ${
                esActivo
                  ? 'bg-gradient-to-r from-emerald-500/20 to-emerald-600/10 border border-emerald-500/40 text-emerald-300 shadow-md shadow-emerald-950/20'
                  : 'hover:bg-slate-800/50 text-slate-300 border border-transparent'
              }`}
            >
              <div className="flex items-center gap-3 min-w-0">
                <span className="text-xl flex-shrink-0">{bandera}</span>
                <div className="truncate">
                  <p className={`text-sm font-semibold truncate ${esActivo ? 'text-white' : 'text-slate-200'}`}>
                    {j.nombre}
                  </p>
                  <p className="text-xs text-slate-400 truncate">{j.pais}</p>
                </div>
              </div>
              {esActivo && (
                <UserCheck className="w-4 h-4 text-emerald-400 flex-shrink-0" />
              )}
            </button>
          );
        })}
        {filtrados.length === 0 && (
          <p className="text-center text-xs text-slate-500 py-6">No se encontraron futbolistas</p>
        )}
      </div>

      {/* Footer Info */}
      <div className="p-3 border-t border-slate-800 text-[11px] text-slate-500 flex justify-between items-center bg-[#0a0f19]">
        <span>Identificador inmutable</span>
        <span className="font-mono text-slate-400 bg-slate-800/80 px-1.5 py-0.5 rounded">
          {jugadorSeleccionado?.id || '---'}
        </span>
      </div>
    </aside>
  );
}

