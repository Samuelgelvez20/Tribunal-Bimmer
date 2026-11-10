import React, { useState, useEffect } from 'react';
import {
  Download,
  Filter,
  MessageSquare,
  ThumbsUp,
  ThumbsDown,
  MinusCircle,
  Shuffle,
  Calendar,
  Hash,
  Car,
  FileJson
} from 'lucide-react';
import { getOpiniones } from '../../services/api';

export default function ConsultasView({ jugadores: modelos = [] }) {
  const [modeloFiltro, setModeloFiltro] = useState('todos');
  const [sentimientoFiltro, setSentimientoFiltro] = useState('todos');
  const [opiniones, setOpiniones] = useState([]);
  const [metricas, setMetricas] = useState({ total: 0, por_sentimiento: {} });
  const [cargando, setCargando] = useState(false);

  const cargarDatos = async () => {
    setCargando(true);
    try {
      const data = await getOpiniones(modeloFiltro, sentimientoFiltro);
      setOpiniones(data.opiniones || []);
      setMetricas(data.metricas_filtradas || { total: 0, por_sentimiento: {} });
    } catch (err) {
      console.error('Error al cargar veredictos:', err);
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargarDatos();
  }, [modeloFiltro, sentimientoFiltro]);

  const descargarJSON = () => {
    const dataStr =
      'data:text/json;charset=utf-8,' +
      encodeURIComponent(JSON.stringify(opiniones, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute('href', dataStr);
    downloadAnchor.setAttribute(
      'download',
      `tribunal_bimmer_${modeloFiltro}_${sentimientoFiltro}.json`
    );
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  const sent = metricas.por_sentimiento || {};

  return (
    <div className="flex-1 flex flex-col h-full bg-[#0A0D12] overflow-hidden p-6">
      {/* Barra superior con Filtros y Descarga */}
      <div className="bg-[#0E121A] border border-[#1E2638] rounded-2xl p-4 mb-6 shadow-lg relative overflow-hidden">
        <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-[#0096D6] via-[#00205B] to-[#E00034]"></div>

        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex flex-wrap items-center gap-3">
            <div className="flex items-center gap-2 text-white font-bold text-sm">
              <Filter className="w-4 h-4 text-[#0096D6]" />
              <span>Filtros de Dictámenes:</span>
            </div>

            {/* Selector de Modelo BMW */}
            <select
              value={modeloFiltro}
              onChange={(e) => setModeloFiltro(e.target.value)}
              className="bg-[#121620] border border-[#1E2638] rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-[#0096D6] max-w-xs"
            >
              <option value="todos">🏎️ Todos los modelos BMW</option>
              {modelos.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.modelo || m.nombre} ({m.ano_creacion || 'BMW'})
                </option>
              ))}
            </select>

            {/* Selector de Sentimiento */}
            <select
              value={sentimientoFiltro}
              onChange={(e) => setSentimientoFiltro(e.target.value)}
              className="bg-[#121620] border border-[#1E2638] rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-[#0096D6]"
            >
              <option value="todos">⭐ Todos los sentimientos</option>
              <option value="positivo">🟢 Favorable / Positivo</option>
              <option value="negativo">🔴 Crítico / Negativo</option>
              <option value="neutro">⚪ Descriptivo / Neutro</option>
              <option value="mixto">🟡 Juicio Mixto</option>
            </select>
          </div>

          <button
            onClick={descargarJSON}
            disabled={opiniones.length === 0}
            className="flex items-center gap-2 bg-[#0096D6] hover:bg-[#0080B8] disabled:bg-[#1E2638] disabled:text-[#94A3B8]/40 px-4 py-2 rounded-xl text-xs font-bold text-white transition-all shadow-md shadow-[#0096D6]/20"
          >
            <Download className="w-4 h-4" />
            <span>Descargar JSON ({opiniones.length})</span>
          </button>
        </div>
      </div>

      {/* Tarjetas de Métricas Estadísticas con paleta BMW M */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-6">
        <div className="bg-[#0E121A] border border-[#1E2638] rounded-2xl p-4 text-center shadow-md">
          <div className="flex items-center justify-center gap-1.5 text-xs text-[#94A3B8] font-semibold mb-1">
            <MessageSquare className="w-3.5 h-3.5 text-[#0096D6]" />
            <span>Total Veredictos</span>
          </div>
          <p className="text-2xl font-black text-white font-mono">{metricas.total}</p>
        </div>

        <div className="bg-[#0E121A] border border-[#1E2638] rounded-2xl p-4 text-center shadow-md">
          <div className="flex items-center justify-center gap-1.5 text-xs text-emerald-400 font-semibold mb-1">
            <ThumbsUp className="w-3.5 h-3.5" />
            <span>Favorables</span>
          </div>
          <p className="text-2xl font-black text-emerald-400 font-mono">
            {sent.positivo || 0}
          </p>
        </div>

        <div className="bg-[#0E121A] border border-[#1E2638] rounded-2xl p-4 text-center shadow-md">
          <div className="flex items-center justify-center gap-1.5 text-xs text-[#ff4d6d] font-semibold mb-1">
            <ThumbsDown className="w-3.5 h-3.5 text-[#E00034]" />
            <span>Críticos</span>
          </div>
          <p className="text-2xl font-black text-[#ff4d6d] font-mono">
            {sent.negativo || 0}
          </p>
        </div>

        <div className="bg-[#0E121A] border border-[#1E2638] rounded-2xl p-4 text-center shadow-md">
          <div className="flex items-center justify-center gap-1.5 text-xs text-[#38bdf8] font-semibold mb-1">
            <MinusCircle className="w-3.5 h-3.5 text-[#0096D6]" />
            <span>Descriptivos</span>
          </div>
          <p className="text-2xl font-black text-[#38bdf8] font-mono">
            {sent.neutro || 0}
          </p>
        </div>

        <div className="bg-[#0E121A] border border-[#1E2638] rounded-2xl p-4 text-center shadow-md col-span-2 md:col-span-1">
          <div className="flex items-center justify-center gap-1.5 text-xs text-amber-400 font-semibold mb-1">
            <Shuffle className="w-3.5 h-3.5" />
            <span>Mixtos</span>
          </div>
          <p className="text-2xl font-black text-amber-400 font-mono">
            {sent.mixto || 0}
          </p>
        </div>
      </div>

      {/* Lista de Registros Persistentes */}
      <div className="flex-1 overflow-y-auto space-y-3 pr-1">
        {opiniones.length === 0 ? (
          <div className="h-64 flex flex-col items-center justify-center text-center p-8 bg-[#0E121A] rounded-2xl border border-[#1E2638]">
            <Car className="w-12 h-12 text-[#94A3B8]/40 mb-3" />
            <h4 className="text-base font-bold text-white mb-1">
              No se encontraron dictámenes
            </h4>
            <p className="text-xs text-[#94A3B8] max-w-sm">
              No hay opiniones registradas para la combinación de filtros seleccionada.
            </p>
          </div>
        ) : (
          opiniones.map((op) => {
            const sentClass =
              op.sentimiento === 'positivo'
                ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30'
                : op.sentimiento === 'negativo'
                ? 'bg-[#E00034]/15 text-[#ff4d6d] border-[#E00034]/30'
                : op.sentimiento === 'mixto'
                ? 'bg-amber-400/15 text-amber-300 border-amber-400/30'
                : 'bg-[#0096D6]/15 text-[#38bdf8] border-[#0096D6]/30';

            const modeloTexto =
              op.modelo_nombre || op.jugador_nombre || 'BMW Model';

            return (
              <div
                key={op.id}
                className="bg-[#0E121A] border border-[#1E2638] rounded-2xl p-4 shadow-sm hover:border-[#0096D6]/40 transition-colors"
              >
                <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-sm text-white">{modeloTexto}</span>
                    <span
                      className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full border ${sentClass}`}
                    >
                      {op.sentimiento}
                    </span>
                  </div>

                  <div className="flex items-center gap-3 text-[11px] text-[#94A3B8]">
                    <span className="flex items-center gap-1 font-mono">
                      <Calendar className="w-3 h-3 text-[#94A3B8]" />
                      {op.fecha_utc ? new Date(op.fecha_utc).toLocaleString() : 'Reciente'}
                    </span>
                    <span className="font-mono bg-[#121620] px-2 py-0.5 rounded border border-[#1E2638]">
                      {op.id.substring(0, 8)}
                    </span>
                  </div>
                </div>

                <p className="text-xs text-slate-300 italic mb-2 pl-3 border-l-2 border-[#0096D6]">
                  "{op.opinion_original}"
                </p>

                <div className="bg-[#121620] p-2.5 rounded-xl border border-[#1E2638] text-xs text-[#94A3B8]">
                  <strong className="text-white">Dictamen: </strong>
                  {op.razon}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
