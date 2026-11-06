import json
import streamlit as st
from datetime import datetime
from src.config import RUTA_JUGADORES, RUTA_OPINIONES, OPENAI_MODEL, OPENAI_API_KEY
from src.almacenamiento import (
    cargar_jugadores,
    cargar_opiniones,
    crear_registro,
    guardar_opinion,
    consultar_opiniones,
    calcular_metricas,
)
from src.analisis import ClasificadorOpiniones, validar_longitud_opinion

# Configuración de página
st.set_page_config(
    page_title="Tribuna Global ⚽",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilos CSS personalizados para una interfaz moderna, limpia y deportiva
st.markdown("""
<style>
    /* Estilos generales */
    .stApp {
        background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
        color: #e6edf3;
    }
    
    /* Encabezado principal */
    .main-header {
        background: linear-gradient(90deg, #1f6feb 0%, #238636 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.3rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        color: #8b949e;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }
    
    /* Badges de sentimiento */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .badge-positivo {
        background-color: rgba(35, 134, 54, 0.2);
        color: #3fb950;
        border: 1px solid #238636;
    }
    .badge-negativo {
        background-color: rgba(218, 54, 51, 0.2);
        color: #f85149;
        border: 1px solid #da3633;
    }
    .badge-neutro {
        background-color: rgba(110, 118, 129, 0.2);
        color: #8b949e;
        border: 1px solid #6e7681;
    }
    .badge-mixto {
        background-color: rgba(210, 153, 34, 0.2);
        color: #e3b341;
        border: 1px solid #d29922;
    }
    
    /* Tarjetas de estadísticas */
    .stat-card {
        background: #21262d;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease;
    }
    .stat-card:hover {
        transform: translateY(-2px);
    }
    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        margin: 0.3rem 0;
    }
    .stat-label {
        font-size: 0.85rem;
        color: #8b949e;
        text-transform: uppercase;
    }
    
    /* Tarjeta de opinión registrada */
    .opinion-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# Banderas de apoyo para jugadores
BANDERAS = {
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
}

# Inicializar sesión
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

# Cargar catálogo de jugadores con caché para optimizar el ciclo de ejecución (rerun)
@st.cache_data
def obtener_catalogo_cacheado(ruta: str):
    return cargar_jugadores(ruta)

try:
    jugadores = obtener_catalogo_cacheado(str(RUTA_JUGADORES))
except Exception as e:
    st.error(f"❌ Error crítico al cargar el catálogo de jugadores: {e}")
    st.stop()

# Diccionario rápido de jugadores
dict_jugadores = {j.id: j for j in jugadores}

# Barra Lateral: Configuración y Selector
with st.sidebar:
    st.markdown("## ⚽ Tribuna Global")
    st.caption("Sistema de Percepción y Análisis de Futbolistas")
    st.markdown("---")
    
    st.subheader("1. Seleccionar Futbolista")
    opciones_jugador = {
        j.id: f"{BANDERAS.get(j.pais, '⚽')} {j.nombre} ({j.pais})" for j in jugadores
    }
    jugador_id_sel = st.selectbox(
        "Jugador:",
        options=list(opciones_jugador.keys()),
        format_func=lambda x: opciones_jugador[x],
    )
    jugador_seleccionado = dict_jugadores[jugador_id_sel]

    st.markdown("---")
    st.subheader("2. Configuración IA")
    api_key_env = OPENAI_API_KEY
    if not api_key_env:
        api_key_input = st.text_input("OpenAI API Key:", type="password")
        api_key_usar = api_key_input
    else:
        api_key_usar = api_key_env
        st.success("API Key cargada desde `.env`", icon="🔑")

    modelo_sel = st.selectbox(
        "Modelo:",
        ["gpt-4o-mini", "gpt-4", "gpt-3.5-turbo"],
        index=0,
    )

    st.markdown("---")
    if st.button("🗑️ Nueva conversación", use_container_width=True):
        st.session_state.mensajes = []
        st.success("Conversación actual limpiada. (Las opiniones guardadas se conservan).")
        st.rerun()

# Cabecera de la aplicación
st.markdown('<div class="main-header">⚽ Tribuna Global</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Expresa tu opinión sobre las leyendas del fútbol y analiza la percepción de los aficionados.</div>', unsafe_allow_html=True)

# Pestañas de navegación
tab_chat, tab_consultas = st.tabs(["💬 Emitir Opinión", "📊 Consultar Opiniones"])

# ==========================================
# PESTAÑA 1: EMITIR OPINIÓN (CHAT)
# ==========================================
with tab_chat:
    st.info(f"Opinando sobre: **{BANDERAS.get(jugador_seleccionado.pais, '')} {jugador_seleccionado.nombre}** ({jugador_seleccionado.pais})")
    
    # Renderizar historial de la sesión actual
    for msg in st.session_state.mensajes:
        if msg["tipo"] == "usuario":
            with st.chat_message("user", avatar="👤"):
                st.markdown(f"**{msg['jugador_nombre']}**")
                st.write(msg["contenido"])
        else:
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(f"**{msg['jugador_nombre']}**")
                if msg.get("es_pertinente"):
                    sent = msg["sentimiento"]
                    st.markdown(f"Opinión guardada. Sentimiento estimado: <span class='badge badge-{sent}'>{sent}</span>", unsafe_allow_html=True)
                    st.write(msg["razon"])
                    st.caption(f"Registro: `{msg['id_registro']}`")
                else:
                    st.warning(f"⚠️ **Opinión no pertinente:** {msg['razon']}")
                    st.caption("Este mensaje no fue registrado en la base de datos.")

    # Input del chat
    texto_usuario = st.chat_input(f"Escribe tu opinión sobre {jugador_seleccionado.nombre} (5 - 1000 caracteres)...")

    if texto_usuario:
        valido, texto_o_error = validar_longitud_opinion(texto_usuario)
        if not valido:
            st.error(f"⚠️ {texto_o_error}")
        else:
            # Capturar el jugador seleccionado en el momento del envío
            jugador_en_envio = jugador_seleccionado

            # Guardar mensaje usuario en session_state
            st.session_state.mensajes.append({
                "tipo": "usuario",
                "jugador_id": jugador_en_envio.id,
                "jugador_nombre": jugador_en_envio.nombre,
                "contenido": texto_o_error,
            })

            # Analizar con IA
            with st.spinner("Analizando sentimiento con LangChain..."):
                try:
                    clasificador = ClasificadorOpiniones(
                        api_key=api_key_usar,
                        model_name=modelo_sel,
                    )
                    analisis = clasificador.analizar(
                        nombre_jugador=jugador_en_envio.nombre,
                        texto_opinion=texto_o_error,
                    )

                    if analisis.es_pertinente:
                        # Crear registro y persistir atómicamente
                        nuevo_reg = crear_registro(
                            jugador=jugador_en_envio,
                            texto_opinion=texto_o_error,
                            analisis=analisis,
                            modelo=modelo_sel,
                        )
                        guardar_opinion(RUTA_OPINIONES, nuevo_reg)

                        st.session_state.mensajes.append({
                            "tipo": "asistente",
                            "jugador_id": jugador_en_envio.id,
                            "jugador_nombre": jugador_en_envio.nombre,
                            "es_pertinente": True,
                            "sentimiento": analisis.sentimiento,
                            "razon": analisis.razon,
                            "id_registro": nuevo_reg.id,
                        })
                    else:
                        # Rechazado por no ser pertinente (no se guarda en disco)
                        st.session_state.mensajes.append({
                            "tipo": "asistente",
                            "jugador_id": jugador_en_envio.id,
                            "jugador_nombre": jugador_en_envio.nombre,
                            "es_pertinente": False,
                            "razon": analisis.razon,
                        })

                except Exception as e:
                    st.error(f"❌ Error al procesar opinión: {e}")

            st.rerun()

# ==========================================
# PESTAÑA 2: CONSULTAR OPINIONES
# ==========================================
with tab_consultas:
    st.subheader("🔍 Panel de Consultas y Percepción")
    
    try:
        base_ops = cargar_opiniones(RUTA_OPINIONES)
    except Exception as e:
        st.error(f"Error al leer la base de datos de opiniones: {e}")
        base_ops = None

    if base_ops:
        col_filtro1, col_filtro2 = st.columns(2)
        
        with col_filtro1:
            opciones_filtro_jugador = {"todos": "⭐ Todos los futbolistas"}
            for j in jugadores:
                opciones_filtro_jugador[j.id] = f"{BANDERAS.get(j.pais, '')} {j.nombre}"
            
            filtro_j = st.selectbox(
                "Filtrar por Futbolista:",
                options=list(opciones_filtro_jugador.keys()),
                format_func=lambda x: opciones_filtro_jugador[x],
            )
            
        with col_filtro2:
            filtro_s = st.selectbox(
                "Filtrar por Sentimiento:",
                ["todos", "positivo", "negativo", "neutro", "mixto"],
                format_func=lambda x: "⭐ Todos los sentimientos" if x == "todos" else x.capitalize(),
            )

        # Aplicar filtros
        resultados = consultar_opiniones(
            base_ops.opiniones,
            jugador_id=filtro_j,
            sentimiento=filtro_s,
        )
        metricas = calcular_metricas(resultados)

        # KPIs y Métricas
        st.markdown("### Resumen")
        m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)
        with m_col1:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">Total</div>
                <div class="stat-value" style="color: #58a6ff;">{metricas['total']}</div>
            </div>
            """, unsafe_allow_html=True)
        with m_col2:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">Positivos</div>
                <div class="stat-value" style="color: #3fb950;">{metricas['por_sentimiento']['positivo']}</div>
            </div>
            """, unsafe_allow_html=True)
        with m_col3:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">Negativos</div>
                <div class="stat-value" style="color: #f85149;">{metricas['por_sentimiento']['negativo']}</div>
            </div>
            """, unsafe_allow_html=True)
        with m_col4:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">Neutros</div>
                <div class="stat-value" style="color: #8b949e;">{metricas['por_sentimiento']['neutro']}</div>
            </div>
            """, unsafe_allow_html=True)
        with m_col5:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">Mixtos</div>
                <div class="stat-value" style="color: #e3b341;">{metricas['por_sentimiento']['mixto']}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        
        # Botón de descarga
        if resultados:
            json_exportar = json.dumps([r.model_dump() for r in resultados], ensure_ascii=False, indent=2)
            st.download_button(
                label="📥 Descargar resultados como JSON",
                data=json_exportar,
                file_name=f"opiniones_tribuna_global_{filtro_j}_{filtro_s}.json",
                mime="application/json",
            )
            
            st.markdown(f"#### Lista de opiniones ({len(resultados)})")
            for r in reversed(resultados):
                sent = r.sentimiento.lower()
                st.markdown(f"""
                <div class="opinion-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <strong>⚽ {r.jugador_nombre}</strong>
                        <span class="badge badge-{sent}">{sent}</span>
                    </div>
                    <p style="margin: 0.3rem 0; font-size: 1.05rem;">«{r.opinion_original}»</p>
                    <p style="color: #8b949e; font-size: 0.9rem; margin-bottom: 0.3rem;"><em>{r.razon}</em></p>
                    <div style="font-size: 0.75rem; color: #6e7681;">
                        📅 {r.fecha_utc} &nbsp;|&nbsp; 🆔 <code>{r.id}</code> &nbsp;|&nbsp; 🤖 Modelo: {r.modelo}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No se encontraron opiniones para los filtros seleccionados.")

