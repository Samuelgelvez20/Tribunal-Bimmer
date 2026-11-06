import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import PlayerList from './components/Sidebar/PlayerList';
import ChatView from './components/Chat/ChatView';
import ConsultasView from './components/Consultas/ConsultasView';
import { getJugadores, analizarOpinion } from './services/api';

export default function App() {
  const [tabActiva, setTabActiva] = useState('chat');
  const [jugadores, setJugadores] = useState([]);
  const [jugadorSeleccionado, setJugadorSeleccionado] = useState(null);
  const [mensajes, setMensajes] = useState([]);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function cargar() {
      try {
        const lista = await getJugadores();
        setJugadores(lista);
        if (lista.length > 0) {
          setJugadorSeleccionado(lista[0]);
        }
      } catch (err) {
        setError('No se pudo conectar con el catálogo de jugadores.');
      }
    }
    cargar();
  }, []);

  const handleEnviarMensaje = async (texto) => {
    if (!jugadorSeleccionado) return;

    // Capturar el jugador seleccionado en el momento exacto del envío
    const jugadorActual = jugadorSeleccionado;

    // Agregar mensaje del usuario a la sesión
    const mensajeUsuario = {
      tipo: 'usuario',
      jugador_id: jugadorActual.id,
      jugador_nombre: jugadorActual.nombre,
      contenido: texto.trim(),
    };

    setMensajes((prev) => [...prev, mensajeUsuario]);
    setCargando(true);
    setError(null);

    try {
      const data = await analizarOpinion(jugadorActual.id, texto.trim());

      const mensajeAsistente = {
        tipo: 'asistente',
        jugador_id: jugadorActual.id,
        jugador_nombre: jugadorActual.nombre,
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
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-[#080c14]">
      {/* Header Superior */}
      <Header tabActiva={tabActiva} onCambiarTab={setTabActiva} />

      {/* Contenido Principal */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar izquierdo (lista de jugadores) */}
        <PlayerList
          jugadores={jugadores}
          jugadorSeleccionado={jugadorSeleccionado}
          onSeleccionarJugador={setJugadorSeleccionado}
        />

        {/* Vista dinámica (Chat o Consultas) */}
        {tabActiva === 'chat' ? (
          <ChatView
            jugadorSeleccionado={jugadorSeleccionado}
            mensajes={mensajes}
            onEnviarMensaje={handleEnviarMensaje}
            onLimpiarConversacion={handleLimpiarConversacion}
            cargando={cargando}
            error={error}
          />
        ) : (
          <ConsultasView jugadores={jugadores} />
        )}
      </div>
    </div>
  );
}

