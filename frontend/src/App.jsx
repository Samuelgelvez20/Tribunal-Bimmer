import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import PlayerList from './components/Sidebar/PlayerList';
import ChatView from './components/Chat/ChatView';
import ConsultasView from './components/Consultas/ConsultasView';
import { getModelos, analizarOpinion } from './services/api';

export default function App() {
  const [tabActiva, setTabActiva] = useState('chat');
  const [modelos, setModelos] = useState([]);
  const [modeloSeleccionado, setModeloSeleccionado] = useState(null);
  const [mensajes, setMensajes] = useState([]);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function cargar() {
      try {
        const lista = await getModelos();
        setModelos(lista);
        if (lista.length > 0) {
          setModeloSeleccionado(lista[0]);
        }
      } catch (err) {
        setError('No se pudo conectar con el catálogo de modelos BMW.');
      }
    }
    cargar();
  }, []);

  const handleEnviarMensaje = async (texto) => {
    if (!modeloSeleccionado) return;

    // Capturar el modelo seleccionado en el momento exacto del envío
    const modeloActual = modeloSeleccionado;
    const nombreModelo = modeloActual.modelo || modeloActual.nombre;

    // Agregar mensaje del usuario a la sesión
    const mensajeUsuario = {
      tipo: 'usuario',
      jugador_id: modeloActual.id,
      jugador_nombre: nombreModelo,
      contenido: texto.trim(),
    };

    setMensajes((prev) => [...prev, mensajeUsuario]);
    setCargando(true);
    setError(null);

    try {
      const data = await analizarOpinion(modeloActual.id, texto.trim());

      const mensajeAsistente = {
        tipo: 'asistente',
        jugador_id: modeloActual.id,
        jugador_nombre: nombreModelo,
        es_pertinente: data.es_pertinente,
        sentimiento: data.sentimiento,
        razon: data.razon,
        id_registro: data.registro?.id,
      };

      setMensajes((prev) => [...prev, mensajeAsistente]);
    } catch (err) {
      setError(err.message || 'Error al procesar la opinión.');
    } finally {
      setCargando(false);
    }
  };

  const handleLimpiarConversacion = () => {
    setMensajes([]);
    setError(null);
  };

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-[#0A0D12]">
      {/* Header Superior */}
      <Header tabActiva={tabActiva} onCambiarTab={setTabActiva} />

      {/* Contenido Principal */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar izquierdo (lista de modelos BMW con filtros por Tipo y Año) */}
        <PlayerList
          jugadores={modelos}
          jugadorSeleccionado={modeloSeleccionado}
          onSeleccionarJugador={setModeloSeleccionado}
        />

        {/* Vista dinámica (Chat o Consultas) */}
        {tabActiva === 'chat' ? (
          <ChatView
            jugadorSeleccionado={modeloSeleccionado}
            mensajes={mensajes}
            onEnviarMensaje={handleEnviarMensaje}
            onLimpiarConversacion={handleLimpiarConversacion}
            cargando={cargando}
            error={error}
          />
        ) : (
          <ConsultasView jugadores={modelos} />
        )}
      </div>
    </div>
  );
}
