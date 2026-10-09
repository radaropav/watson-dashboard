import os
import requests
import pandas as pd
import streamlit as st

# ==========================================
# 1. CONFIGURACIÓN DE PÁGINA E INTERFAZ PREMIUM
# ==========================================
st.set_page_config(
    page_title="Mesa Algorítmica Watson Ultra",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS Premium de la Mesa Algorítmica Watson
estilo_css_premium = """
<style>
    body, .stApp {
        background-color: #0b0d17 !important;
        background-image: radial-gradient(circle at 50% 50%, #151932 0%, #070913 100%) !important;
        color: #e2e8f0 !important;
        font-family: 'Inter', sans-serif !important;
    }
    [data-testid="stSidebar"] {
        background-color: #0d1124 !important;
        border-right: 1px solid #1f294d !important;
    }
    .card-indicador {
        background: rgba(20, 26, 54, 0.6) !important;
        border: 1px solid #242f63 !important;
        backdrop-filter: blur(12px) !important;
        border-radius: 16px !important;
        padding: 24px !important;
        margin-bottom: 16px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37) !important;
    }
    .metric-val {
        font-size: 32px !important;
        font-weight: 700 !important;
        color: #8b5cf6 !important;
        font-family: 'JetBrains Mono', monospace !important;
    }
    .metric-label {
        font-size: 13px !important;
        color: #94a3b8 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }
    div.stButton > button {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }
    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 0 20px rgba(124, 58, 237, 0.6) !important;
    }
</style>
"""
st.markdown(estilo_css_premium, unsafe_allow_html=True)

# ==========================================
# 2. GESTIÓN DE CREDENCIALES (SECRETS EXACTOS)
# ==========================================
URL_RAW = st.secrets.get("URL_SUPABASE_TABLA", os.getenv("URL_SUPABASE_TABLA", ""))
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", os.getenv("SUPABASE_KEY", ""))

if not URL_RAW or not SUPABASE_KEY:
    st.error("🚨 Error Crítico: No se encontraron 'URL_SUPABASE_TABLA' o 'SUPABASE_KEY' en Secrets.")
    st.stop()

# Formateo automático de URL para la API REST nativa de Supabase
URL_LIMPIA = str(URL_RAW).strip().rstrip("/")
SUPABASE_REST_URL = URL_LIMPIA if URL_LIMPIA.endswith("/rest/v1") else f"{URL_LIMPIA}/rest/v1"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# ==========================================
# 3. CONEXIÓN Y CONSULTAS A SUPABASE
# ==========================================
@st.cache_data(ttl=2)
def consultar_tabla(tabla: str):
    url = f"{SUPABASE_REST_URL}/{tabla}"
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                return pd.DataFrame(data)
        return pd.DataFrame()
    except Exception:
        return pd.DataFrame()

def enviar_actualizacion_tactica(payload: dict):
    # Apunta exactamente a la fila maestra ID 1 de tu control
    url = f"{SUPABASE_REST_URL}/control_bot?id=eq.1"
    headers_patch = {**HEADERS, "Prefer": "return=minimal"}
    try:
        response = requests.patch(url, headers=headers_patch, json=payload)
        if response.status_code == 200 or response.status_code == 204:
            return True
        return False
    except Exception:
        return False

# Carga de datos reales mapeados con tu base de datos
df_control = consultar_tabla("control_bot")
df_trades = consultar_tabla("historial_trades")
df_mechazos = consultar_tabla("registro_mechazos")

conexion_exitosa = not df_control.empty

# ==========================================
# 4. DISEÑO DE INTERFAZ GENERAL (BARRA LATERAL DE INFRAESTRUCTURA)
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='color:#8b5cf6;'>WATSON QUANT</h2>", unsafe_allow_html=True)
    st.selectbox("Selección de Infraestructura", ["Bot 1 - Multiactivo (Frankfurt)", "Bot 2 - Volatilidad (Bifurcación)"])
    st.markdown("---")
    st.markdown("### Telemetría de Red")
    
    val_estado = "CONECTADO" if conexion_exitosa else "FALLO_RE"
    color_estado = "#10b981" if conexion_exitosa else "#ef4444"
    st.markdown(f'<div class="card-indicador"><div class="metric-label">Estado en Nube</div><div class="metric-val" style="color:{color_estado};">{val_estado}</div></div>', unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #ffffff;'>⚡ MESA ALGORÍTMICA WATSON ULTRA</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8;'>Consola de Sincronización Estricta con Servidores en Frankfurt</p>", unsafe_allow_html=True)
st.markdown("---")

col_izq, col_der = st.columns([1.2, 1])

# --- Columna Izquierda: Actividad Real del VPS ---
with col_izq:
    st.markdown("### 📊 Monitoreo de Actividad y Mitigación")
    
    c1, c2 = st.columns(2)
    with c1:
        total_mechazos = len(df_mechazos) if not df_mechazos.empty else 0
        st.markdown(f'<div class="card-indicador"><div class="metric-label">Falsas Rupturas Evitadas</div><div class="metric-val">{total_mechazos} Mechazos</div></div>', unsafe_allow_html=True)
    with c2:
        # El bot registra en 'perdida_evitada' un valor fijo de 5.50. Se calcula la sumatoria real acumulada.
        total_ahorrado = 0.0
        if not df_mechazos.empty and 'perdida_evitada' in df_mechazos.columns:
            total_ahorrado = df_mechazos['perdida_evitada'].astype(float).sum()
        st.markdown(f'<div class="card-indicador"><div class="metric-label">Capital Salvaguardado</div><div class="metric-val">${total_ahorrado:,.2f}</div></div>', unsafe_allow_html=True)

    st.markdown("#### 📈 Historial Reciente de Operaciones Real (Supabase)")
    if df_trades.empty:
        st.info("ℹ️ Esperando ejecuciones de órdenes desde el VPS... Sin operaciones registradas en 'historial_trades'.")
    else:
        st.dataframe(df_trades, use_container_width=True)

# --- Columna Derecha: Consola Táctica de Parámetros ---
with col_der:
    st.markdown("### ⚙️ Panel de Infraestructura Táctica")
    
    # Estructura interna de contingencia garantizada
    config_actual = {
        "estado": "OFF",
        "apalancamiento": 10,
        "margen_maximo_usdt": 100.0
    }
    
    if not conexion_exitosa:
        st.warning("⚠️ Sin comunicación con la tabla de control en Supabase. Usando parámetros locales de respaldo.")
    else:
        try:
            if len(df_control) > 0:
                fila_real = df_control.iloc[0]
                # AJUSTE CRÍTICO: Lee la columna 'estado' exactamente como la busca tu bot
                config_actual["estado"] = str(fila_real.get("estado", "OFF")).upper()
                config_actual["apalancamiento"] = int(fila_real.get("apalancamiento", 10))
                config_actual["margen_maximo_usdt"] = float(fila_real.get("margen_maximo_usdt", 100.0))
        except Exception:
            pass

    estado_actual_bot = config_actual["estado"]
    apalancamiento_actual = config_actual["apalancamiento"]
    margen_maximo = config_actual["margen_maximo_usdt"]

    with st.container():
        st.markdown('#### Configuración Operativa Real')
        
        # HOMOLOGACIÓN TOTAL: Las opciones son exactamente los estados que tu bot procesa
        nuevo_estado = st.selectbox(
            "Modificar Estado Operativo Watson (Mapeo Directo):",
            options=["PREDADOR", "APLANAMIENTO", "OFF"],
            index=["PREDADOR", "APLANAMIENTO", "OFF"].index(estado_actual_bot) if estado_actual_bot in ["PREDADOR", "APLANAMIENTO", "OFF"] else 2
        )
        
        nuevo_apalancamiento = st.slider(
            "Apalancamiento de Posiciones (LEVERAGE):", 
            min_value=1, 
            max_value=20, 
            value=apalancamiento_actual
        )
        
        nuevo_margen = st.number_input(
            "Margen Límite de Exposición (USDT):", 
            min_value=10.0, 
            max_value=100000.0, 
            value=margen_maximo,
            step=50.0
        )
        
        if st.button("🚀 Inyectar Parámetros de Control", use_container_width=True):
            if not conexion_exitosa:
                st.error("❌ Error de envío: No hay conexión activa con la base de datos.")
            else:
                # payload estructurado con la columna 'estado' exacta para tu función leer_comando_supabase()
                payload = {
                    "estado": nuevo_estado,
                    "apalancamiento": nuevo_apalancamiento,
                    "margen_maximo_usdt": nuevo_margen
                }
                if enviar_actualizacion_tactica(payload):
                    st.balloons()
                    st.rerun()

st.markdown("---")
st.caption("Mesa Algorítmica Watson Ultra • DigitalOcean VPS • Conectores Sincronizados v2.0")
