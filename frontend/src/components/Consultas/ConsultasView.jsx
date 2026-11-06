import React, { useState, useEffect } from 'react';
import { Download, Filter, MessageSquare, ThumbsUp, ThumbsDown, MinusCircle, Shuffle, Calendar, Hash } from 'lucide-react';
import { getOpiniones } from '../../services/api';

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

export default function ConsultasView({ jugadores }) {
  const [jugadorFiltro, setJugadorFiltro] = useState('todos');
  const [sentimientoFiltro, setSentimientoFiltro] = useState('todos');
  const [opiniones, setOpiniones] = useState([]);
  const [metricas, setMetricas] = useState({ total: 0, por_sentimiento: {} });
  const [cargando, setCargando] = useState(false);

  const cargarDatos = async () => {
    setCargando(true);
    try {
      const data = await getOpiniones(jugadorFiltro, sentimientoFiltro);
      setOpiniones(data.opiniones || []);
      setMetricas(data.metricas_filtradas || { total: 0, por_sentimiento: {} });
    } catch (err) {
      console.error(err);
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargarDatos();
  }, [jugadorFiltro, sentimientoFiltro]);

  const descargarJSON = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(opiniones, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `tribuna_global_${jugadorFiltro}_${sentimientoFiltro}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-[#0a0e17] overflow-hidden p-6">
      {/* Barra superior con Filtros y Descarga */}
      <div className="bg-[#0d131f] border border-slate-800 rounded-2xl p-4 mb-6 shadow-lg">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex flex-wrap items-center gap-3">
            <div className="flex items-center gap-2 text-slate-300 font-semibold text-sm">
              <Filter className="w-4 h-4 text-emerald-400" />
              <span>Filtros de consulta:</span>
            </div>

            {/* Selector de Jugador */}
            <select
              value={jugadorFiltro}
              onChange={(e) => setJugadorFiltro(e.target.value)}
              className="bg-[#141b2a] border border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
            >
              <option value="todos">⭐ Todos los futbolistas</option>
              {jugadores.map((j) => (
                <option key={j.id} value={j.id}>
                  {BANDERAS[j.pais] || '⚽'} {j.nombre} ({j.pais})
                </option>
              ))}
            </select>

            {/* Selector de Sentimiento */}
            <select
              value={sentimientoFiltro}
              onChange={(e) => setSentimientoFiltro(e.target.value)}
              className="bg-[#141b2a] border border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
            >
              <option value="todos">⭐ Todos los sentimientos</option>
              <option value="positivo">🟢 Positivo</option>
              <option value="negativo">🔴 Negativo</option>
              <option value="neutro">⚪ Neutro</option>
              <option value="mixto">🟡 Mixto</option>
            </select>
          </div>

          <button
            onClick={descargarJSON}
            disabled={opiniones.length === 0}
            className="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-800 disabled:text-slate-600 px-4 py-2 rounded-xl text-xs font-semibold text-white transition-all shadow-md shadow-emerald-950/30"
          >
            <Download className="w-4 h-4" />
            <span>Descargar JSON ({opiniones.length})</span>
          </button>
        </div>
      </div>

      {/* Tarjetas KPI de Resumen */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3.5 mb-6">
        <div className="bg-[#0f1624] border border-slate-800/80 rounded-2xl p-4 text-center">
          <div className="flex items-center justify-center gap-1.5 text-xs text-slate-400 mb-1">
            <MessageSquare className="w-3.5 h-3.5 text-blue-400" />
            <span>Total Filtrado</span>
          </div>
          <p className="text-2xl font-extrabold text-blue-400">{metricas.total}</p>
        </div>

        <div className="bg-[#0f1624] border border-slate-800/80 rounded-2xl p-4 text-center">
          <div className="flex items-center justify-center gap-1.5 text-xs text-slate-400 mb-1">
            <ThumbsUp className="w-3.5 h-3.5 text-emerald-400" />
            <span>Positivos</span>
          </div>
          <p className="text-2xl font-extrabold text-emerald-400">
            {metricas.por_sentimiento?.positivo || 0}
          </p>
        </div>

        <div className="bg-[#0f1624] border border-slate-800/80 rounded-2xl p-4 text-center">
          <div className="flex items-center justify-center gap-1.5 text-xs text-slate-400 mb-1">
            <ThumbsDown className="w-3.5 h-3.5 text-rose-400" />
            <span>Negativos</span>
          </div>
          <p className="text-2xl font-extrabold text-rose-400">
            {metricas.por_sentimiento?.negativo || 0}
          </p>
        </div>

        <div className="bg-[#0f1624] border border-slate-800/80 rounded-2xl p-4 text-center">
          <div className="flex items-center justify-center gap-1.5 text-xs text-slate-400 mb-1">
            <MinusCircle className="w-3.5 h-3.5 text-slate-400" />
            <span>Neutros</span>
          </div>
          <p className="text-2xl font-extrabold text-slate-300">
            {metricas.por_sentimiento?.neutro || 0}
          </p>
        </div>

        <div className="bg-[#0f1624] border border-slate-800/80 rounded-2xl p-4 text-center">
          <div className="flex items-center justify-center gap-1.5 text-xs text-slate-400 mb-1">
            <Shuffle className="w-3.5 h-3.5 text-amber-400" />
            <span>Mixtos</span>
          </div>
          <p className="text-2xl font-extrabold text-amber-400">
            {metricas.por_sentimiento?.mixto || 0}
          </p>
        </div>
      </div>

      {/* Lista de Registros */}
      <div className="flex-1 overflow-y-auto space-y-3 pr-1">
        {cargando ? (
          <div className="text-center py-12 text-slate-500 text-sm">Cargando registros...</div>
        ) : opiniones.length === 0 ? (
          <div className="text-center py-12 text-slate-500 text-sm">
            No se encontraron opiniones para los filtros seleccionados.
          </div>
        ) : (
          opiniones.map((op) => (
            <div
              key={op.id}
              className="bg-[#0e1422] border border-slate-800/90 hover:border-slate-700/80 rounded-2xl p-4 transition-all duration-150 shadow-md"
            >
              <div className="flex items-center justify-between gap-3 mb-2">
                <span className="font-bold text-slate-200 text-sm flex items-center gap-1.5">
                  <span>⚽</span> {op.jugador_nombre}
                </span>

                <span
                  className={`text-[10px] uppercase font-bold tracking-wider px-2.5 py-0.5 rounded-full border ${
                    op.sentimiento === 'positivo'
                      ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30'
                      : op.sentimiento === 'negativo'
                      ? 'bg-rose-500/15 text-rose-400 border-rose-500/30'
                      : op.sentimiento === 'mixto'
                      ? 'bg-amber-500/15 text-amber-400 border-amber-500/30'
                      : 'bg-slate-500/15 text-slate-300 border-slate-500/30'
                  }`}
                >
                  {op.sentimiento}
                </span>
              </div>

              <p className="text-slate-100 text-sm font-medium mb-1.5 leading-relaxed">
                «{op.opinion_original}»
              </p>

              <p className="text-xs text-slate-400 italic mb-3 bg-black/20 p-2 rounded-lg border border-slate-800/60">
                {op.razon}
              </p>

              <div className="flex flex-wrap items-center justify-between text-[11px] text-slate-500 border-t border-slate-800/60 pt-2 gap-2">
                <span className="flex items-center gap-1">
                  <Calendar className="w-3 h-3 text-slate-500" />
                  {new Date(op.fecha_utc).toLocaleString()}
                </span>

                <span className="flex items-center gap-1 font-mono text-slate-400">
                  <Hash className="w-3 h-3 text-slate-500" />
                  {op.id}
                </span>

                <span className="bg-slate-800/60 text-slate-400 px-2 py-0.5 rounded text-[10px]">
                  {op.modelo}
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

