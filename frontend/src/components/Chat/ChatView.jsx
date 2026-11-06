import React, { useState, useRef, useEffect } from 'react';
import { Send, Trash2, Bot, User, AlertCircle, CheckCircle2, Sparkles } from 'lucide-react';

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

export default function ChatView({
  jugadorSeleccionado,
  mensajes,
  onEnviarMensaje,
  onLimpiarConversacion,
  cargando,
  error
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
  const bandera = BANDERAS[jugadorSeleccionado?.pais] || '⚽';

  return (
    <div className="flex-1 flex flex-col h-full bg-[#0a0e17] overflow-hidden">
      {/* Header del Chat */}
      <div className="h-16 border-b border-slate-800 bg-[#0d131f]/90 backdrop-blur px-6 flex items-center justify-between z-10">
        <div className="flex items-center gap-3">
          <span className="text-2xl">{bandera}</span>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="font-bold text-white text-base">{jugadorSeleccionado?.nombre}</h2>
              <span className="bg-emerald-500/10 text-emerald-400 text-[10px] font-bold px-2 py-0.5 rounded-full border border-emerald-500/20">
                EN SESIÓN
              </span>
            </div>
            <p className="text-xs text-slate-400">Opinando sobre el futbolista seleccionado</p>
          </div>
        </div>

        <button
          onClick={onLimpiarConversacion}
          title="Limpiar chat actual (las opiniones guardadas se conservan)"
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-slate-300 hover:text-rose-400 hover:bg-rose-500/10 border border-slate-700 hover:border-rose-500/30 transition-all"
        >
          <Trash2 className="w-3.5 h-3.5" />
          <span>Nueva conversación</span>
        </button>
      </div>

      {/* Área de Mensajes */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {mensajes.length === 0 && (
          <div className="h-full flex flex-col items-center justify-center text-center p-8 text-slate-400">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-emerald-500/20 to-blue-500/20 border border-slate-700 flex items-center justify-center text-3xl mb-4 animate-bounce">
              ⚽
            </div>
            <h3 className="text-lg font-bold text-slate-200 mb-1">
              ¿Qué opinas sobre {jugadorSeleccionado?.nombre}?
            </h3>
            <p className="text-sm text-slate-400 max-w-md mb-4">
              Escribe una crítica, elogio o análisis sobre su juego. El sistema evaluará el sentimiento con LangChain y lo registrará en la base de datos persistente.
            </p>
            <div className="flex flex-wrap gap-2 justify-center max-w-lg">
              <span className="text-xs bg-slate-800/80 border border-slate-700 px-3 py-1.5 rounded-full text-slate-300">
                💡 Ejemplo: "Su visión de juego y precisión son extraordinarias"
              </span>
              <span className="text-xs bg-slate-800/80 border border-slate-700 px-3 py-1.5 rounded-full text-slate-300">
                💡 Ejemplo: "Tiene calidad, pero su actitud me decepciona"
              </span>
            </div>
          </div>
        )}

        {mensajes.map((msg, index) => {
          const esUsuario = msg.tipo === 'usuario';
          return (
            <div
              key={index}
              className={`flex gap-3.5 max-w-3xl ${esUsuario ? 'ml-auto flex-row-reverse' : 'mr-auto'}`}
            >
              {/* Avatar estilo captura */}
              <div
                className={`w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 text-white font-bold text-sm shadow-md ${
                  esUsuario
                    ? 'bg-rose-600/90 shadow-rose-950/40'
                    : 'bg-amber-600/90 shadow-amber-950/40'
                }`}
              >
                {esUsuario ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
              </div>

              {/* Contenido del mensaje */}
              <div
                className={`flex-1 rounded-2xl p-4 text-sm leading-relaxed border transition-all ${
                  esUsuario
                    ? 'bg-[#1a2333] border-slate-700/80 text-slate-100 shadow-lg'
                    : 'bg-[#111723] border-slate-800 text-slate-200 shadow-xl'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-bold text-slate-300">
                    {msg.jugador_nombre}
                  </span>
                  {msg.tipo === 'asistente' && msg.es_pertinente && (
                    <span
                      className={`text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full border ${
                        msg.sentimiento === 'positivo'
                          ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30'
                          : msg.sentimiento === 'negativo'
                          ? 'bg-rose-500/15 text-rose-400 border-rose-500/30'
                          : msg.sentimiento === 'mixto'
                          ? 'bg-amber-500/15 text-amber-400 border-amber-500/30'
                          : 'bg-slate-500/15 text-slate-300 border-slate-500/30'
                      }`}
                    >
                      {msg.sentimiento}
                    </span>
                  )}
                </div>

                {esUsuario ? (
                  <p className="text-slate-100 font-medium">{msg.contenido}</p>
                ) : msg.es_pertinente ? (
                  <div className="space-y-2">
                    <p className="text-emerald-400 font-semibold flex items-center gap-1.5">
                      <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                      Opinión guardada. Sentimiento estimado: <span className="underline decoration-emerald-500/50">{msg.sentimiento}</span>.
                    </p>
                    <p className="text-slate-200 bg-black/20 p-2.5 rounded-lg border border-slate-800">
                      {msg.razon}
                    </p>
                    <div className="pt-1 text-[11px] font-mono text-slate-400 flex items-center gap-1">
                      <span>Registro:</span>
                      <code className="text-slate-300 bg-slate-800/80 px-1.5 py-0.5 rounded select-all">
                        {msg.id_registro}
                      </code>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-1.5 text-rose-300">
                    <p className="font-semibold flex items-center gap-1.5 text-rose-400">
                      <AlertCircle className="w-4 h-4 text-rose-400" />
                      Opinión rechazada (No pertinente al futbolista)
                    </p>
                    <p className="text-xs text-slate-300">{msg.razon}</p>
                    <p className="text-[11px] text-slate-500 italic">No se guardó ningún registro en la base de datos.</p>
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {cargando && (
          <div className="flex gap-3.5 max-w-3xl mr-auto">
            <div className="w-9 h-9 rounded-xl bg-amber-600/90 flex items-center justify-center text-white shadow-md">
              <Bot className="w-5 h-5 animate-spin" />
            </div>
            <div className="bg-[#111723] border border-slate-800 rounded-2xl p-4 text-sm text-slate-300 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-emerald-400 animate-pulse" />
              <span>Analizando con LangChain y evaluando pertinencia...</span>
            </div>
          </div>
        )}

        {error && (
          <div className="p-3 bg-rose-500/10 border border-rose-500/30 rounded-xl text-rose-300 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Formulario */}
      <div className="p-4 bg-[#0d131f] border-t border-slate-800">
        <form onSubmit={handleSubmit} className="relative max-w-4xl mx-auto">
          <input
            type="text"
            value={texto}
            onChange={(e) => setTexto(e.target.value)}
            placeholder={`Escribe una opinión sobre ${jugadorSeleccionado?.nombre} (5 a 1000 caracteres)...`}
            disabled={cargando}
            className="w-full bg-[#141b2a] border border-slate-700 rounded-xl pl-4 pr-28 py-3.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-all"
          />

          <div className="absolute right-2.5 top-2.5 flex items-center gap-2">
            <span
              className={`text-[11px] font-mono px-2 py-0.5 rounded ${
                len > 0 && !esValido
                  ? 'text-rose-400 bg-rose-500/10'
                  : 'text-slate-400 bg-slate-800/80'
              }`}
            >
              {len}/1000
            </span>

            <button
              type="submit"
              disabled={!esValido || cargando}
              className={`p-2 rounded-lg font-medium text-white transition-all ${
                esValido && !cargando
                  ? 'bg-emerald-600 hover:bg-emerald-500 shadow-md shadow-emerald-900/30'
                  : 'bg-slate-700/50 text-slate-500 cursor-not-allowed'
              }`}
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

