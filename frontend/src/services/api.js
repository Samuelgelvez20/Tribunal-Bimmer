const API_BASE = '/api';

export async function getJugadores() {
  const res = await fetch(`${API_BASE}/jugadores`);
  if (!res.ok) throw new Error('Error al cargar la lista de jugadores');
  return res.json();
}

export async function getOpiniones(jugadorId = null, sentimiento = null) {
  const params = new URLSearchParams();
  if (jugadorId && jugadorId !== 'todos') params.append('jugador_id', jugadorId);
  if (sentimiento && sentimiento !== 'todos') params.append('sentimiento', sentimiento);
  
  const res = await fetch(`${API_BASE}/opiniones?${params.toString()}`);
  if (!res.ok) throw new Error('Error al cargar las opiniones');
  return res.json();
}

export async function analizarOpinion(jugadorId, textoOpinion, apiKey = null, modelo = null) {
  const res = await fetch(`${API_BASE}/opiniones/analizar`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      jugador_id: jugadorId,
      texto_opinion: textoOpinion,
      api_key: apiKey,
      modelo: modelo
    })
  });
  
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || 'Error al analizar la opinión');
  }
  return data;
}

