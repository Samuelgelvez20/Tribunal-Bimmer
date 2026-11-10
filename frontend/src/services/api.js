const API_BASE = '/api';

export async function getModelos() {
  const res = await fetch(`${API_BASE}/modelos`);
  if (!res.ok) throw new Error('Error al cargar la lista de modelos de BMW');
  return res.json();
}

// Alias compatible
export async function getJugadores() {
  return getModelos();
}

export async function getOpiniones(modeloId = null, sentimiento = null) {
  const params = new URLSearchParams();
  if (modeloId && modeloId !== 'todos') params.append('modelo_id', modeloId);
  if (sentimiento && sentimiento !== 'todos') params.append('sentimiento', sentimiento);
  
  const res = await fetch(`${API_BASE}/opiniones?${params.toString()}`);
  if (!res.ok) throw new Error('Error al cargar las opiniones');
  return res.json();
}

export async function analizarOpinion(modeloId, textoOpinion, apiKey = null, modelo = null) {
  const res = await fetch(`${API_BASE}/opiniones/analizar`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      modelo_id: modeloId,
      jugador_id: modeloId,
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
