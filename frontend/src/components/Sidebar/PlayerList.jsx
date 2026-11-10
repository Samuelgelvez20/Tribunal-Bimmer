import React, { useState, useMemo } from 'react';
import { Search, SlidersHorizontal, RotateCcw, Gauge, Calendar, ShieldCheck, ChevronDown, Check } from 'lucide-react';

const TIPOS_CARROCERIA = [
  { id: 'todos', label: 'Todos' },
  { id: 'deportivo', label: 'Deportivo' },
  { id: 'sedan', label: 'Sedán' },
  { id: 'semideportivo', label: 'Semideportivo' },
  { id: 'familiar', label: 'Familiar' },
  { id: 'compacto', label: 'Compacto' },
];

export default function PlayerList({
  jugadores: modelos = [],
  jugadorSeleccionado: modeloSeleccionado,
  onSeleccionarJugador: onSeleccionarModelo,
}) {
  const [busqueda, setBusqueda] = useState('');
  const [tipoSeleccionado, setTipoSeleccionado] = useState('todos');
  const [anoMin, setAnoMin] = useState(1929);
  const [anoMax, setAnoMax] = useState(2026);
  const [mostrarFiltrosAvanzados, setMostrarFiltrosAvanzados] = useState(false);

  // Obtener límites reales de año del catálogo
  const { minCatalogo, maxCatalogo } = useMemo(() => {
    if (!modelos.length) return { minCatalogo: 1929, maxCatalogo: 2026 };
    const anos = modelos.map((m) => m.ano_creacion).filter(Boolean);
    return {
      minCatalogo: Math.min(...anos),
      maxCatalogo: Math.max(...anos),
    };
  }, [modelos]);

  // Filtrado compuesto: Búsqueda de texto + Tipo de carrocería + Rango de año
  const filtrados = useMemo(() => {
    return modelos.filter((m) => {
      // 1. Filtro por texto (modelo, chasis, era, motor)
      const q = busqueda.toLowerCase().trim();
      const coincideTexto =
        !q ||
        (m.modelo || m.nombre || '').toLowerCase().includes(q) ||
        (m.chasis && m.chasis.toLowerCase().includes(q)) ||
        (m.era && m.era.toLowerCase().includes(q)) ||
        (m.motor && m.motor.toLowerCase().includes(q));

      // 2. Filtro por tipo de carrocería
      const coincideTipo =
        tipoSeleccionado === 'todos' ||
        (m.tipo && m.tipo.toLowerCase() === tipoSeleccionado.toLowerCase());

      // 3. Filtro por año de creación
      const ano = m.ano_creacion || 2000;
      const coincideAno = ano >= anoMin && ano <= anoMax;

      return coincideTexto && coincideTipo && coincideAno;
    });
  }, [modelos, busqueda, tipoSeleccionado, anoMin, anoMax]);

  const hayFiltrosActivos =
    tipoSeleccionado !== 'todos' ||
    anoMin > minCatalogo ||
    anoMax < maxCatalogo ||
    busqueda.trim() !== '';

  const handleResetFiltros = () => {
    setBusqueda('');
    setTipoSeleccionado('todos');
    setAnoMin(minCatalogo);
    setAnoMax(maxCatalogo);
  };

  const getBadgeClass = (tipo) => {
    switch ((tipo || '').toLowerCase()) {
      case 'deportivo':
        return 'badge-bmw-deportivo';
      case 'semideportivo':
        return 'badge-bmw-semideportivo';
      case 'sedan':
        return 'badge-bmw-sedan';
      case 'familiar':
        return 'badge-bmw-familiar';
      default:
        return 'badge-bmw-compacto';
    }
  };

  return (
    <aside className="w-88 md:w-96 bg-[#0A0D12] border-r border-[#1E2638] flex flex-col h-full select-none flex-shrink-0">
      {/* Header del Sidebar */}
      <div className="p-4 border-b border-[#1E2638] bg-[#0A0D12]">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2.5">
            {/* Insignia M tricolor */}
            <div className="w-8 h-8 rounded-lg bg-[#121620] border border-[#1E2638] flex items-center justify-center relative overflow-hidden shadow-inner">
              <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-[#0096D6] via-[#00205B] to-[#E00034]"></div>
              <span className="font-black text-sm italic tracking-tighter text-white">///M</span>
            </div>
            <div>
              <h2 className="font-extrabold text-white text-sm tracking-wide flex items-center gap-1.5">
                Modelos BMW
                <span className="text-[10px] font-mono bg-[#121620] text-[#0096D6] px-1.5 py-0.5 rounded border border-[#1E2638]">
                  {filtrados.length}
                </span>
              </h2>
              <p className="text-[11px] text-[#94A3B8]">Catálogo Histórico & M Power</p>
            </div>
          </div>

          {hayFiltrosActivos && (
            <button
              onClick={handleResetFiltros}
              className="text-[11px] flex items-center gap-1 text-[#94A3B8] hover:text-[#0096D6] transition-colors bg-[#121620] px-2 py-1 rounded-md border border-[#1E2638]"
              title="Restablecer todos los filtros"
            >
              <RotateCcw className="w-3 h-3" />
              <span>Limpiar</span>
            </button>
          )}
        </div>

        {/* Buscador reactivo */}
        <div className="relative mb-3">
          <Search className="w-4 h-4 text-[#94A3B8] absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Buscar modelo (M3, E30, V8, CSL...)"
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
            className="w-full bg-[#121620] border border-[#1E2638] rounded-xl pl-9 pr-3 py-2 text-xs text-white placeholder-[#94A3B8]/60 focus:outline-none focus:border-[#0096D6] transition-colors shadow-inner"
          />
        </div>

        {/* Botón selector de Filtros */}
        <div className="space-y-2">
          {/* Pills de Tipo de Carrocería */}
          <div className="flex items-center justify-between text-[11px] font-semibold text-[#94A3B8] mb-1">
            <span className="flex items-center gap-1">
              <SlidersHorizontal className="w-3 h-3 text-[#0096D6]" /> Tipo de Carrocería:
            </span>
            <span className="capitalize text-white font-mono text-[10px]">
              {tipoSeleccionado}
            </span>
          </div>

          <div className="flex flex-wrap gap-1.5">
            {TIPOS_CARROCERIA.map((tipo) => {
              const activo = tipoSeleccionado === tipo.id;
              return (
                <button
                  key={tipo.id}
                  onClick={() => setTipoSeleccionado(tipo.id)}
                  className={`px-2.5 py-1 rounded-lg text-[11px] font-medium transition-all ${
                    activo
                      ? 'bg-[#0096D6] text-white shadow-sm shadow-[#0096D6]/40 font-bold'
                      : 'bg-[#121620] text-[#94A3B8] hover:text-white hover:bg-[#1E2638] border border-[#1E2638]'
                  }`}
                >
                  {tipo.label}
                </button>
              );
            })}
          </div>

          {/* Filtro por Año de Creación */}
          <div className="pt-2 border-t border-[#1E2638]/70">
            <div className="flex items-center justify-between text-[11px] font-semibold text-[#94A3B8] mb-1">
              <span className="flex items-center gap-1">
                <Calendar className="w-3 h-3 text-[#E00034]" /> Año de Creación:
              </span>
              <span className="text-[#0096D6] font-mono font-bold text-[11px]">
                {anoMin} — {anoMax}
              </span>
            </div>

            {/* Doble control de año */}
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="text-[10px] text-[#94A3B8]/70 block mb-0.5">Desde ({anoMin})</label>
                <input
                  type="range"
                  min={minCatalogo}
                  max={anoMax}
                  value={anoMin}
                  onChange={(e) => setAnoMin(Number(e.target.value))}
                  className="w-full accent-[#0096D6] h-1.5 bg-[#1E2638] rounded-lg cursor-pointer"
                />
              </div>
              <div>
                <label className="text-[10px] text-[#94A3B8]/70 block mb-0.5">Hasta ({anoMax})</label>
                <input
                  type="range"
                  min={anoMin}
                  max={maxCatalogo}
                  value={anoMax}
                  onChange={(e) => setAnoMax(Number(e.target.value))}
                  className="w-full accent-[#E00034] h-1.5 bg-[#1E2638] rounded-lg cursor-pointer"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Lista de Modelos BMW scrolleable */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1.5">
        {filtrados.map((m) => {
          const esActivo = modeloSeleccionado?.id === m.id;
          const badgeClass = getBadgeClass(m.tipo);

          return (
            <button
              key={m.id}
              onClick={() => onSeleccionarModelo(m)}
              className={`w-full group text-left p-3 rounded-xl transition-all duration-150 relative overflow-hidden border ${
                esActivo
                  ? 'bg-[#121620] border-[#0096D6] shadow-lg shadow-[#0096D6]/10'
                  : 'bg-[#0E121A] hover:bg-[#121620] border-[#1E2638]/70 hover:border-[#1E2638]'
              }`}
            >
              {/* Franja vertical M Stripe cuando está activo */}
              {esActivo && (
                <div className="absolute top-0 bottom-0 left-0 w-1.5 bg-gradient-to-b from-[#0096D6] via-[#00205B] to-[#E00034]" />
              )}

              <div className="flex items-start justify-between gap-2 pl-1">
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-1.5 mb-1">
                    <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-[#0A0D12] text-[#94A3B8] border border-[#1E2638]">
                      {m.ano_creacion}
                    </span>
                    {m.chasis && (
                      <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-[#00205B]/40 text-[#93c5fd] border border-[#00205B]">
                        {m.chasis}
                      </span>
                    )}
                    <span className={`text-[9px] uppercase font-bold tracking-wider px-1.5 py-0.2 rounded ${badgeClass}`}>
                      {m.tipo}
                    </span>
                  </div>

                  <h3 className={`text-xs font-bold leading-tight truncate ${esActivo ? 'text-white' : 'text-slate-200 group-hover:text-white'}`}>
                    {m.modelo || m.nombre}
                  </h3>

                  <p className="text-[11px] text-[#94A3B8] truncate mt-0.5">
                    {m.motor}
                  </p>
                </div>

                {/* Potencia HP si existe */}
                {m.caballos_fuerza && (
                  <div className="text-right flex-shrink-0">
                    <span className="text-xs font-bold font-mono text-[#0096D6]">
                      {m.caballos_fuerza}
                    </span>
                    <span className="text-[9px] text-[#94A3B8] block">HP</span>
                  </div>
                )}
              </div>
            </button>
          );
        })}

        {filtrados.length === 0 && (
          <div className="text-center py-12 px-4">
            <div className="w-12 h-12 mx-auto rounded-full bg-[#121620] border border-[#1E2638] flex items-center justify-center text-[#94A3B8] mb-3">
              🔍
            </div>
            <p className="text-xs font-semibold text-slate-300 mb-1">
              No hay modelos con estos filtros
            </p>
            <p className="text-[11px] text-[#94A3B8] mb-3">
              Prueba modificando el rango de año o la categoría.
            </p>
            <button
              onClick={handleResetFiltros}
              className="text-xs bg-[#1E2638] hover:bg-[#0096D6] text-white px-3 py-1.5 rounded-lg transition-colors"
            >
              Restablecer Filtros
            </button>
          </div>
        )}
      </div>

      {/* Footer del Sidebar con resumen */}
      <div className="p-3 border-t border-[#1E2638] text-[11px] text-[#94A3B8] flex justify-between items-center bg-[#07090D]">
        <div className="flex items-center gap-1.5">
          <div className="w-2 h-2 rounded-full bg-[#0096D6] animate-pulse" />
          <span>BMW M Database</span>
        </div>
        <span className="font-mono text-[#0096D6] bg-[#121620] px-2 py-0.5 rounded border border-[#1E2638]">
          {modeloSeleccionado?.id || '---'}
        </span>
      </div>
    </aside>
  );
}
