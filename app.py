import json
import streamlit as st
from datetime import datetime
from src.config import RUTA_MODELOS_BMW, RUTA_OPINIONES, DEFAULT_MODEL, DEFAULT_API_KEY
from src.almacenamiento import (
    cargar_modelos_bmw,
    cargar_opiniones,
    crear_registro,
    guardar_opinion,
    consultar_opiniones,
    calcular_metricas,
)
from src.analisis import ClasificadorOpiniones, validar_longitud_opinion

# Configuración de página
st.set_page_config(
    page_title="Tribunal Bimmer 🏁",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilos CSS personalizados con la paleta oficial BMW M
st.markdown("""
<style>
    :root {
        /* BMW M Accent Palette */
        --bimmer-blue-light: #0096D6;
        --bimmer-blue-dark:  #00205B;
        --bimmer-red:        #E00034;

        /* Surface & Background */
        --bg-obsidian:       #0A0D12;
        --bg-card:           #121620;
        --border-steel:      #1E2638;

        /* Typography */
        --text-primary:      #FFFFFF;
        --text-secondary:    #94A3B8;

        /* Gradiente icónico M Badge */
        --m-stripe-gradient: linear-gradient(
            90deg, 
            #0096D6 0%, 
            #00205B 50%, 
            #E00034 100%
        );
    }

    /* Estilos generales */
    .stApp {
        background-color: var(--bg-obsidian);
        color: var(--text-primary);
    }
    
    /* Franja M icónica */
    .m-stripe-header {
        height: 4px;
        background: var(--m-stripe-gradient);
        border-radius: 2px;
        margin-bottom: 1.2rem;
    }
    
    /* Encabezado principal */
    .main-header {
        color: #FFFFFF;
        font-size: 2.3rem;
        font-weight: 900;
        letter-spacing: -0.02em;
        margin-bottom: 0.1rem;
    }
    .sub-header {
        color: var(--text-secondary);
        font-size: 0.95rem;
        margin-bottom: 1.2rem;
    }
    
    /* Ficha Técnica Card */
    .spec-card {
        background: var(--bg-card);
        border: 1px solid var(--border-steel);
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        position: relative;
        overflow: hidden;
    }
    .spec-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: var(--m-stripe-gradient);
    }
    
    /* Badges de sentimiento */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.65rem;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .badge-positivo {
        background-color: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.4);
    }
    .badge-negativo {
        background-color: rgba(224, 0, 52, 0.15);
        color: #ff4d6d;
        border: 1px solid rgba(224, 0, 52, 0.4);
    }
    .badge-neutro {
        background-color: rgba(0, 150, 214, 0.15);
        color: #38bdf8;
        border: 1px solid rgba(0, 150, 214, 0.4);
    }
    .badge-mixto {
        background-color: rgba(245, 158, 11, 0.15);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.4);
    }
    
    /* Tarjetas de estadísticas */
    .stat-card {
        background: var(--bg-card);
        border: 1px solid var(--border-steel);
        border-radius: 12px;
        padding: 1.1rem;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    .stat-value {
        font-size: 2rem;
        font-weight: 800;
        font-family: monospace;
        margin: 0.2rem 0;
    }
    .stat-label {
        font-size: 0.8rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        font-weight: 600;
    }
    
    /* Tarjeta de opinión registrada */
    .opinion-card {
        background: var(--bg-card);
        border: 1px solid var(--border-steel);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
        border-left: 3px solid var(--bimmer-blue-light);
    }
</style>
""", unsafe_allow_html=True)

# Inicializar estado de sesión
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

# Cargar catálogo de modelos BMW con caché
@st.cache_data
def obtener_catalogo_cacheado(ruta: str):
    return cargar_modelos_bmw(ruta)

try:
    modelos = obtener_catalogo_cacheado(str(RUTA_MODELOS_BMW))
except Exception as e:
    st.error(f"❌ Error crítico al cargar el catálogo de modelos BMW: {e}")
    st.stop()

# Diccionario rápido de modelos
dict_modelos = {m.id: m for m in modelos}

# ==========================================
# BARRA LATERAL CON FILTROS POR TIPO Y AÑO
# ==========================================
with st.sidebar:
    st.markdown("## 🏁 Tribunal Bimmer")
    st.caption("Catálogo & Crítica de Modelos BMW")
    st.markdown('<div class="m-stripe-header"></div>', unsafe_allow_html=True)
    
    st.subheader("🔍 Filtros de Catálogo")
    
    # 1. Filtro por Tipo de carrocería
    tipos_disponibles = ["todos", "deportivo", "sedan", "semideportivo", "familiar", "compacto"]
    tipo_filtro = st.selectbox(
        "Tipo de Carrocería:",
        options=tipos_disponibles,
        format_func=lambda x: "⭐ Todos los tipos" if x == "todos" else x.capitalize(),
        index=0,
    )
    
    # 2. Filtro por Año de creación
    anos = [m.ano_creacion for m in modelos if m.ano_creacion]
    min_ano, max_ano = (min(anos), max(anos)) if anos else (1929, 2026)
    
    ano_rango = st.slider(
        "Rango de Año de Creación:",
        min_value=min_ano,
        max_value=max_ano,
        value=(min_ano, max_ano),
    )
    
    # Filtrar modelos según selección
    modelos_filtrados = [
        m for m in modelos
        if (tipo_filtro == "todos" or m.tipo.lower() == tipo_filtro.lower())
        and (ano_rango[0] <= m.ano_creacion <= ano_rango[1])
    ]
    
    if not modelos_filtrados:
        st.warning("No hay modelos que coincidan con estos filtros.")
        modelos_filtrados = modelos
    
    st.caption(f"Mostrando **{len(modelos_filtrados)}** de **{len(modelos)}** modelos BMW")
    
    # Selector del Modelo específico
    opciones_modelo = {
        m.id: f"{m.modelo} ({m.ano_creacion}{f' • {m.chasis}' if m.chasis else ''})"
        for m in modelos_filtrados
    }
    
    modelo_id_sel = st.selectbox(
        "Seleccionar Modelo BMW:",
        options=list(opciones_modelo.keys()),
        format_func=lambda x: opciones_modelo[x],
        index=0,
    )
    modelo_seleccionado = dict_modelos[modelo_id_sel]

    st.markdown("---")
    st.subheader("⚙️ Configuración IA")
    api_key_env = DEFAULT_API_KEY
    if not api_key_env:
        api_key_input = st.text_input("API Key (OpenAI o Gemini):", type="password")
        api_key_usar = api_key_input
    else:
        api_key_usar = api_key_env
        st.success("API Key cargada desde el entorno", icon="🔑")

    modelo_sel = st.selectbox(
        "Modelo LLM:",
        ["gemini-3.8-flash", "gpt-4o-mini", "gpt-4"],
        index=0 if DEFAULT_MODEL.startswith("gemini") else 1,
    )

    st.markdown("---")
    if st.button("🗑️ Nueva conversación", use_container_width=True):
        st.session_state.mensajes = []
        st.success("Conversación actual limpiada. (Las opiniones guardadas persisten).")
        st.rerun()

# Cabecera principal
st.markdown('<div class="main-header">🏁 Tribunal Bimmer</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Sistema de Percepción y Análisis Inteligente de Modelos BMW con LangChain LCEL</div>', unsafe_allow_html=True)
st.markdown('<div class="m-stripe-header"></div>', unsafe_allow_html=True)

# Pestañas de navegación
tab_chat, tab_consultas = st.tabs(["💬 Emitir Veredicto (Chat)", "📊 Consultar Dictámenes"])

# ==========================================
# PESTAÑA 1: EMITIR OPINIÓN / VEREDICTO
# ==========================================
with tab_chat:
    # Ficha técnica del modelo seleccionado
    with st.container():
        st.markdown(f"""
        <div class="spec-card">
            <div style="display: flex; justify-content: space-between; align-items: baseline; flex-wrap: wrap; gap: 0.5rem;">
                <h3 style="color: #FFFFFF; margin: 0; font-size: 1.4rem; font-weight: 800;">
                    {modelo_seleccionado.modelo}
                </h3>
                <div>
                    <span class="badge badge-neutro">{modelo_seleccionado.era}</span>
                    {f'<span class="badge" style="background: rgba(0,32,91,0.4); color: #93c5fd; border: 1px solid #00205B;">Chasis: {modelo_seleccionado.chasis}</span>' if modelo_seleccionado.chasis else ''}
                    <span class="badge badge-negativo">{modelo_seleccionado.tipo.upper()}</span>
                </div>
            </div>
            <p style="color: var(--text-secondary); font-size: 0.9rem; margin-top: 0.4rem; margin-bottom: 0.8rem;">
                {modelo_seleccionado.caracteristica}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Grid de métricas técnicas rápidas
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        c1.metric("⚡ Potencia", f"{modelo_seleccionado.caballos_fuerza} HP" if modelo_seleccionado.caballos_fuerza else "N/D")
        c2.metric("⏱️ 0-100 km/h", f"{modelo_seleccionado.aceleracion_0_100_kmh_s} s" if modelo_seleccionado.aceleracion_0_100_kmh_s else "N/D")
        c3.metric("🏁 Vel. Máx", f"{modelo_seleccionado.velocidad_maxima_kmh} km/h" if modelo_seleccionado.velocidad_maxima_kmh else "N/D")
        c4.metric("🔄 Torque", f"{modelo_seleccionado.torque_nm} Nm" if modelo_seleccionado.torque_nm else "N/D")
        c5.metric("📅 Año", str(modelo_seleccionado.ano_creacion))
        c6.metric("⚙️ Tipo", modelo_seleccionado.tipo.capitalize())

    st.markdown("---")
    
    # Renderizar historial de chat
    for msg in st.session_state.mensajes:
        if msg["tipo"] == "usuario":
            with st.chat_message("user", avatar="🏎️"):
                st.markdown(f"**{msg.get('jugador_nombre') or msg.get('modelo_nombre')}**")
                st.write(msg["contenido"])
        else:
            with st.chat_message("assistant", avatar="⚖️"):
                st.markdown(f"**Dictamen del Tribunal Bimmer — {msg.get('jugador_nombre') or msg.get('modelo_nombre')}**")
                if msg.get("es_pertinente"):
                    sent = msg["sentimiento"]
                    st.markdown(f"Veredicto: <span class='badge badge-{sent}'>{sent}</span>", unsafe_allow_html=True)
                    st.write(msg["razon"])
                    st.caption(f"Registro persistente ID: `{msg.get('id_registro')}`")
                else:
                    st.warning(f"⚠️ **Opinión no pertinente:** {msg['razon']}")
                    st.caption("Rechazado: no se registró en la base de datos.")

    # Input del chat
    texto_usuario = st.chat_input(f"Escribe tu opinión o crítica técnica sobre {modelo_seleccionado.modelo} (5 - 1000 caracteres)...")

    if texto_usuario:
        valido, texto_o_error = validar_longitud_opinion(texto_usuario)
        if not valido:
            st.error(f"⚠️ {texto_o_error}")
        else:
            modelo_en_envio = modelo_seleccionado

            st.session_state.mensajes.append({
                "tipo": "usuario",
                "jugador_id": modelo_en_envio.id,
                "jugador_nombre": modelo_en_envio.modelo,
                "contenido": texto_o_error,
            })

            with st.spinner("El Tribunal Bimmer está analizando con LangChain LCEL..."):
                try:
                    clasificador = ClasificadorOpiniones(
                        api_key=api_key_usar,
                        model_name=modelo_sel,
                    )
                    analisis = clasificador.analizar(
                        nombre_modelo=modelo_en_envio.modelo,
                        texto_opinion=texto_o_error,
                    )

                    if analisis.es_pertinente:
                        nuevo_reg = crear_registro(
                            jugador=modelo_en_envio,
                            texto_opinion=texto_o_error,
                            analisis=analisis,
                            modelo=modelo_sel,
                        )
                        guardar_opinion(RUTA_OPINIONES, nuevo_reg)

                        st.session_state.mensajes.append({
                            "tipo": "asistente",
                            "jugador_id": modelo_en_envio.id,
                            "jugador_nombre": modelo_en_envio.modelo,
                            "es_pertinente": True,
                            "sentimiento": analisis.sentimiento,
                            "razon": analisis.razon,
                            "id_registro": nuevo_reg.id,
                        })
                    else:
                        st.session_state.mensajes.append({
                            "tipo": "asistente",
                            "jugador_id": modelo_en_envio.id,
                            "jugador_nombre": modelo_en_envio.modelo,
                            "es_pertinente": False,
                            "razon": analisis.razon,
                        })

                except Exception as e:
                    st.error(f"❌ Error al procesar el dictamen: {e}")

            st.rerun()

# ==========================================
# PESTAÑA 2: CONSULTAR DICTÁMENES
# ==========================================
with tab_consultas:
    st.subheader("🔍 Panel de Dictámenes y Percepción")
    
    try:
        base_ops = cargar_opiniones(RUTA_OPINIONES)
    except Exception as e:
        st.error(f"Error al leer la base de datos de opiniones: {e}")
        base_ops = None

    if base_ops:
        col_filtro1, col_filtro2 = st.columns(2)
        
        with col_filtro1:
            opciones_filtro_modelo = {"todos": "🏎️ Todos los modelos BMW"}
            for m in modelos:
                opciones_filtro_modelo[m.id] = f"{m.modelo} ({m.ano_creacion})"
            
            filtro_m = st.selectbox(
                "Filtrar por Modelo:",
                options=list(opciones_filtro_modelo.keys()),
                format_func=lambda x: opciones_filtro_modelo[x],
            )
            
        with col_filtro2:
            filtro_s = st.selectbox(
                "Filtrar por Sentimiento:",
                ["todos", "positivo", "negativo", "neutro", "mixto"],
                format_func=lambda x: "⭐ Todos los sentimientos" if x == "todos" else x.capitalize(),
            )

        resultados = consultar_opiniones(
            base_ops.opiniones,
            modelo_id=filtro_m,
            sentimiento=filtro_s,
        )
        metricas = calcular_metricas(resultados)

        # KPIs y Métricas con paleta BMW M
        st.markdown("### Resumen Estadístico")
        m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)
        with m_col1:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">Total</div>
                <div class="stat-value" style="color: #0096D6;">{metricas['total']}</div>
            </div>
            """, unsafe_allow_html=True)
        with m_col2:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">Favorables</div>
                <div class="stat-value" style="color: #34d399;">{metricas['por_sentimiento']['positivo']}</div>
            </div>
            """, unsafe_allow_html=True)
        with m_col3:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">Críticos</div>
                <div class="stat-value" style="color: #ff4d6d;">{metricas['por_sentimiento']['negativo']}</div>
            </div>
            """, unsafe_allow_html=True)
        with m_col4:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">Descriptivos</div>
                <div class="stat-value" style="color: #38bdf8;">{metricas['por_sentimiento']['neutro']}</div>
            </div>
            """, unsafe_allow_html=True)
        with m_col5:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">Mixtos</div>
                <div class="stat-value" style="color: #fbbf24;">{metricas['por_sentimiento']['mixto']}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        
        # Botón de descarga
        if resultados:
            json_exportar = json.dumps([r.model_dump() for r in resultados], ensure_ascii=False, indent=2)
            st.download_button(
                label="📥 Descargar resultados como JSON",
                data=json_exportar,
                file_name=f"tribunal_bimmer_{filtro_m}_{filtro_s}.json",
                mime="application/json",
            )
            
            st.markdown(f"#### Lista de veredictos ({len(resultados)})")
            for r in reversed(resultados):
                sent = r.sentimiento.lower()
                nom = getattr(r, "modelo_nombre", None) or r.jugador_nombre
                st.markdown(f"""
                <div class="opinion-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <strong style="color: #FFFFFF;">🏎️ {nom}</strong>
                        <span class="badge badge-{sent}">{sent}</span>
                    </div>
                    <p style="margin: 0.3rem 0; font-size: 1.05rem; color: #e2e8f0;">«{r.opinion_original}»</p>
                    <p style="color: #94A3B8; font-size: 0.9rem; margin-bottom: 0.3rem;"><em>{r.razon}</em></p>
                    <div style="font-size: 0.75rem; color: #64748b;">
                        📅 {r.fecha_utc} &nbsp;|&nbsp; 🆔 <code>{r.id[:8]}...</code> &nbsp;|&nbsp; 🤖 Modelo: {r.modelo}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No se encontraron dictámenes para los filtros seleccionados.")
