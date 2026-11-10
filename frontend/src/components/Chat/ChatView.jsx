import React, { useState, useRef, useEffect } from 'react';
import {
  Send,
  Trash2,
  Bot,
  User,
  AlertCircle,
  CheckCircle2,
  Sparkles,
  Gauge,
  Zap,
  Timer,
  Flame,
  Info,
  Car
} from 'lucide-react';

export default function ChatView({
  jugadorSeleccionado: modeloSeleccionado,
  mensajes,
  onEnviarMensaje,
  onLimpiarConversacion,
  cargando,
  error,
}) {
  const [texto, setTexto] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [mensajes, cargando]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (texto.trim().length < 5 || texto.trim().length > 1000 || cargando) return;
    onEnviarMensaje(texto);
    setTexto('');
  };

  const len = texto.trim().length;
  const esValido = len >= 5 && len <= 1000;

  const modeloNombre =
    modeloSeleccionado?.modelo || modeloSeleccionado?.nombre || 'BMW M Power';

  // Sugerencias de opiniones automotrices
  const sugerencias = [
    `El empuje y sonido del motor ${modeloSeleccionado?.motor?.split('(')[0] || 'BMW'} transmiten una emoción inigualable en curva.`,
    `Un modelo icónico con gran dinamismo, aunque su peso y costo de mantenimiento me dejan dudas.`,
    `Fue fabricado en el año ${modeloSeleccionado?.ano_creacion || '1986'} con especificación de chasis ${modeloSeleccionado?.chasis || 'M'}.`,
  ];

  return (
    <div className="flex-1 flex flex-col h-full bg-[#0A0D12] overflow-hidden">
      {/* Header y Ficha Técnica del Modelo BMW */}
      <div className="border-b border-[#1E2638] bg-[#0E121A] px-6 py-4 z-10 shadow-sm relative">
        {/* Franja M Badge superior */}
        <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-[#0096D6] via-[#00205B] to-[#E00034]"></div>

        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-[#121620] border border-[#1E2638] flex items-center justify-center text-white font-black italic shadow-inner">
              <span className="text-[#0096D6] text-xl">///</span>
              <span className="text-[#E00034] text-xl">M</span>
            </div>
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <h2 className="font-extrabold text-white text-lg tracking-tight">
                  {modeloNombre}
                </h2>
                <span className="bg-[#0096D6]/15 text-[#0096D6] text-[10px] font-bold px-2.5 py-0.5 rounded-full border border-[#0096D6]/30">
                  {modeloSeleccionado?.era || 'BMW Classic & Modern'}
                </span>
                {modeloSeleccionado?.chasis && (
                  <span className="bg-[#00205B]/40 text-[#93c5fd] text-[10px] font-mono px-2 py-0.5 rounded border border-[#00205B]">
                    Chasis: {modeloSeleccionado.chasis}
                  </span>
                )}
              </div>
              <p className="text-xs text-[#94A3B8] mt-0.5">
                {modeloSeleccionado?.caracteristica || 'Modelo de altas prestaciones del fabricante bávaro'}
              </p>
            </div>
          </div>

          {/* Botón limpiar sesión */}
          <button
            onClick={onLimpiarConversacion}
            title="Reiniciar chat actual (los veredictos persisten en disco)"
            className="self-start lg:self-center flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-[#94A3B8] hover:text-[#E00034] hover:bg-[#E00034]/10 border border-[#1E2638] hover:border-[#E00034]/30 transition-all"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>Nuevo Juicio</span>
          </button>
        </div>

        {/* Barra de especificaciones técnicas (KPIs rápidos del auto) */}
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-2 mt-3 pt-3 border-t border-[#1E2638]/70">
          <div className="bg-[#121620] p-2 rounded-lg border border-[#1E2638]/80 text-center">
            <span className="text-[10px] text-[#94A3B8] uppercase block">Potencia</span>
            <span className="text-xs font-bold font-mono text-[#0096D6]">
              {modeloSeleccionado?.caballos_fuerza ? `${modeloSeleccionado.caballos_fuerza} HP` : 'N/D'}
            </span>
          </div>

          <div className="bg-[#121620] p-2 rounded-lg border border-[#1E2638]/80 text-center">
            <span className="text-[10px] text-[#94A3B8] uppercase block">0-100 km/h</span>
            <span className="text-xs font-bold font-mono text-[#E00034]">
              {modeloSeleccionado?.aceleracion_0_100_kmh_s ? `${modeloSeleccionado.aceleracion_0_100_kmh_s} s` : 'N/D'}
            </span>
          </div>

          <div className="bg-[#121620] p-2 rounded-lg border border-[#1E2638]/80 text-center">
            <span className="text-[10px] text-[#94A3B8] uppercase block">Vel. Máxima</span>
            <span className="text-xs font-bold font-mono text-white">
              {modeloSeleccionado?.velocidad_maxima_kmh ? `${modeloSeleccionado.velocidad_maxima_kmh} km/h` : 'N/D'}
            </span>
          </div>

          <div className="bg-[#121620] p-2 rounded-lg border border-[#1E2638]/80 text-center">
            <span className="text-[10px] text-[#94A3B8] uppercase block">Torque</span>
            <span className="text-xs font-bold font-mono text-slate-300">
              {modeloSeleccionado?.torque_nm ? `${modeloSeleccionado.torque_nm} Nm` : 'N/D'}
            </span>
          </div>

          <div className="bg-[#121620] p-2 rounded-lg border border-[#1E2638]/80 text-center">
            <span className="text-[10px] text-[#94A3B8] uppercase block">Año</span>
            <span className="text-xs font-bold font-mono text-slate-300">
              {modeloSeleccionado?.ano_creacion || 'N/D'}
            </span>
          </div>

          <div className="bg-[#121620] p-2 rounded-lg border border-[#1E2638]/80 text-center">
            <span className="text-[10px] text-[#94A3B8] uppercase block">Carrocería</span>
            <span className="text-xs font-bold uppercase text-[#0096D6] truncate block">
              {modeloSeleccionado?.tipo || 'Turismo'}
            </span>
          </div>
        </div>
      </div>

      {/* Área de Mensajes */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {mensajes.length === 0 && (
          <div className="h-full flex flex-col items-center justify-center text-center p-8 text-[#94A3B8]">
            <div className="w-16 h-16 rounded-2xl bg-[#121620] border border-[#1E2638] flex items-center justify-center text-3xl mb-4 relative overflow-hidden shadow-lg">
              <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-[#0096D6] via-[#00205B] to-[#E00034]"></div>
              <Car className="w-8 h-8 text-[#0096D6]" />
            </div>
            <h3 className="text-lg font-bold text-white mb-1">
              ¿Cuál es tu veredicto sobre el {modeloNombre}?
            </h3>
            <p className="text-sm text-[#94A3B8] max-w-lg mb-6">
              Expresa tu crítica, elogio o análisis técnico sobre su comportamiento, motor o diseño. El Tribunal Bimmer evaluará la pertinencia y el sentimiento con LangChain LCEL.
            </p>

            {/* Sugerencias clicables */}
            <div className="flex flex-col gap-2 max-w-xl w-full">
              <span className="text-xs font-semibold text-[#94A3B8]/80 mb-1">
                💡 Haz clic en una sugerencia o escribe tu propio juicio:
              </span>
              {sugerencias.map((sug, idx) => (
                <button
                  key={idx}
                  onClick={() => setTexto(sug)}
                  className="text-xs text-left bg-[#121620] hover:bg-[#1E2638] border border-[#1E2638] hover:border-[#0096D6]/40 p-2.5 rounded-xl text-slate-300 hover:text-white transition-all shadow-sm"
                >
                  "{sug}"
                </button>
              ))}
            </div>
          </div>
        )}

        {mensajes.map((m, index) => {
          if (m.tipo === 'usuario') {
            return (
              <div key={index} className="flex justify-end">
                <div className="max-w-2xl bg-[#121620] border border-[#1E2638] rounded-2xl p-4 shadow-md">
                  <div className="flex items-center gap-2 mb-1.5 text-xs text-[#94A3B8]">
                    <User className="w-3.5 h-3.5 text-[#0096D6]" />
                    <span className="font-semibold text-white">Entusiasta Bimmer</span>
                    <span className="text-[10px] text-[#94A3B8]/60">• {m.jugador_nombre}</span>
                  </div>
                  <p className="text-sm text-slate-200 leading-relaxed whitespace-pre-wrap">
                    {m.contenido}
                  </p>
                </div>
              </div>
            );
          }

          // Mensaje del Asistente / Tribunal
          const esPertinente = m.es_pertinente;
          const sent = m.sentimiento;

          return (
            <div key={index} className="flex justify-start">
              <div className="max-w-2xl bg-[#0E121A] border border-[#1E2638] rounded-2xl p-5 shadow-lg relative overflow-hidden w-full">
                {/* Franja vertical de veredicto */}
                <div
                  className={`absolute top-0 bottom-0 left-0 w-1.5 ${
                    !esPertinente
                      ? 'bg-amber-500'
                      : sent === 'positivo'
                      ? 'bg-emerald-500'
                      : sent === 'negativo'
                      ? 'bg-[#E00034]'
                      : sent === 'mixto'
                      ? 'bg-amber-400'
                      : 'bg-[#0096D6]'
                  }`}
                />

                <div className="flex items-center justify-between mb-3 pl-1">
                  <div className="flex items-center gap-2">
                    <div className="w-7 h-7 rounded-lg bg-[#121620] border border-[#1E2638] flex items-center justify-center">
                      <Sparkles className="w-4 h-4 text-[#0096D6]" />
                    </div>
                    <div>
                      <h4 className="text-xs font-bold text-white tracking-wide">
                        Dictamen del Tribunal Bimmer
                      </h4>
                      <p className="text-[10px] text-[#94A3B8]">Análisis LCEL Determinista (t=0.0)</p>
                    </div>
                  </div>

                  {/* Badge de Sentimiento */}
                  {esPertinente && (
                    <span
                      className={`text-[11px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-full border ${
                        sent === 'positivo'
                          ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30'
                          : sent === 'negativo'
                          ? 'bg-[#E00034]/15 text-[#ff4d6d] border-[#E00034]/40'
                          : sent === 'mixto'
                          ? 'bg-amber-400/15 text-amber-300 border-amber-400/30'
                          : 'bg-[#0096D6]/15 text-[#38bdf8] border-[#0096D6]/30'
                      }`}
                    >
                      {sent === 'positivo' && '🟢 Sentimiento Favorable'}
                      {sent === 'negativo' && '🔴 Sentimiento Crítico'}
                      {sent === 'neutro' && '⚪ Descriptivo / Fáctico'}
                      {sent === 'mixto' && '🟡 Juicio Mixto'}
                    </span>
                  )}
                </div>

                {/* Justificación en tercera persona */}
                <div className="bg-[#121620] p-3.5 rounded-xl border border-[#1E2638] mb-3 ml-1">
                  <p className="text-xs text-slate-300 leading-relaxed font-sans">
                    <span className="font-semibold text-white">Justificación Analítica: </span>
                    {m.razon}
                  </p>
                </div>

                {/* Estado de Persistencia */}
                <div className="flex items-center justify-between text-[11px] text-[#94A3B8] pt-1 pl-1">
                  <div className="flex items-center gap-1.5">
                    {esPertinente ? (
                      <>
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                        <span className="text-emerald-400 font-medium">
                          Registrado en Base de Datos de Opiniones
                        </span>
                      </>
                    ) : (
                      <>
                        <AlertCircle className="w-3.5 h-3.5 text-amber-400" />
                        <span className="text-amber-400 font-medium">
                          No Pertinente (Rechazado sin guardar)
                        </span>
                      </>
                    )}
                  </div>
                  {m.id_registro && (
                    <span className="font-mono text-[10px] text-[#94A3B8]/70">
                      ID: {m.id_registro.substring(0, 8)}...
                    </span>
                  )}
                </div>
              </div>
            </div>
          );
        })}

        {cargando && (
          <div className="flex justify-start">
            <div className="bg-[#0E121A] border border-[#1E2638] rounded-2xl p-4 flex items-center gap-3">
              <div className="w-6 h-6 border-2 border-[#0096D6] border-t-transparent rounded-full animate-spin" />
              <span className="text-xs text-[#94A3B8]">
                El Tribunal está deliberando con el modelo de IA...
              </span>
            </div>
          </div>
        )}

        {error && (
          <div className="bg-[#E00034]/15 border border-[#E00034]/30 rounded-xl p-3 flex items-center gap-2 text-xs text-[#ff4d6d]">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Formulario de Entrada */}
      <div className="p-4 border-t border-[#1E2638] bg-[#0E121A]">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto space-y-2">
          <div className="relative">
            <textarea
              value={texto}
              onChange={(e) => setTexto(e.target.value)}
              placeholder={`Escribe tu crítica o juicio sobre el ${modeloNombre} (5 a 1000 caracteres)...`}
              rows={2}
              className="w-full bg-[#121620] border border-[#1E2638] rounded-xl px-4 py-3 text-xs text-white placeholder-[#94A3B8]/60 focus:outline-none focus:border-[#0096D6] resize-none transition-colors"
            />
            <button
              type="submit"
              disabled={!esValido || cargando}
              className="absolute right-2.5 bottom-2.5 bg-[#0096D6] hover:bg-[#0080B8] disabled:bg-[#1E2638] disabled:text-[#94A3B8]/40 text-white px-4 py-2 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 shadow-md shadow-[#0096D6]/20"
            >
              <span>Veredicto</span>
              <Send className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="flex items-center justify-between text-[11px] text-[#94A3B8] px-1">
            <span>
              Restricción estricta: entre <strong className="text-white">5</strong> y{' '}
              <strong className="text-white">1000</strong> caracteres.
            </span>
            <span
              className={`font-mono ${
                len > 1000 || (len > 0 && len < 5) ? 'text-[#E00034]' : 'text-[#0096D6]'
              }`}
            >
              {len} / 1000
            </span>
          </div>
        </form>
      </div>
    </div>
  );
}
