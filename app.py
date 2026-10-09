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

# Estilos CSS Premium originales de la Mesa Algorítmica Watson
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
# 2. GESTIÓN DE CREDENCIALES
# ==========================================
URL_RAW = st.secrets.get("URL_SUPABASE_TABLA", os.getenv("URL_SUPABASE_TABLA", ""))
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", os.getenv("SUPABASE_KEY", ""))
BINANCE_API_KEY = st.secrets.get("BINANCE_API_KEY", os.getenv("BINANCE_API_KEY", ""))
BINANCE_SECRET_KEY = st.secrets.get("BINANCE_SECRET_KEY", os.getenv("BINANCE_SECRET_KEY", ""))

if not URL_RAW or not SUPABASE_KEY:
    st.error("🚨 Error Crítico: No se encontraron 'URL_SUPABASE_TABLA' o 'SUPABASE_KEY' en Secrets.")
    st.stop()

# FORMATEO AUTOMÁTICO: Limpia la URL y asegura la estructura de la API REST de Supabase
URL_LIMPIA = str(URL_RAW).strip().rstrip("/")
if not URL_LIMPIA.endswith("/rest/v1"):
    SUPABASE_REST_URL = f"{URL_LIMPIA}/rest/v1"
else:
    SUPABASE_REST_URL = URL_LIMPIA

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# ==========================================
# 3. CONEXIÓN Y CONSULTAS A BASE DE DATOS
# ==========================================
@st.cache_data(ttl=3)
def consultar_tabla(tabla: str):
    url = f"{SUPABASE_REST_URL}/{tabla}"
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            return pd.DataFrame(response.json())
        return pd.DataFrame()
    except Exception:
        return pd.DataFrame()

def enviar_actualizacion_tactica(payload: dict):
    url = f"{SUPABASE_REST_URL}/control_bot?id=eq.1"
    headers_patch = {**HEADERS, "Prefer": "return=minimal"}
    try:
        response = requests.patch(url, headers=headers_patch, json=payload)
        if response.status_code == 200 or response.status_code == 204:
            st.success("✅ Parámetros tácticos sincronizados.")
            return True
        return False
    except Exception:
        return False

# Carga de datos real
df_control = consultar_tabla("control_bot")
df_trades = consultar_tabla("historial_trades")
df_mechazos = consultar_tabla("registro_mechazos")

# Determinar dinámicamente el estado de la conexión de red
conexion_exitosa = not df_control.empty

# ==========================================
# 4. DISEÑO DE INTERFAZ GENERAL (SIDEBAR + 2 COLUMNAS)
# ==========================================

with st.sidebar:
    st.markdown("<h2 style='color:#8b5cf6;'>WATSON QUANT</h2>", unsafe_allow_html=True)
    st.selectbox("Selección de Infraestructura", ["Bot Depredador Estándar (4H)", "Bot Watson Ultra Custom"])
    st.markdown("---")
    st.markdown("### Telemetría de Cuenta")
    st.markdown('<div class="card-indicador"><div class="metric-label">Balance Total USDT</div><div class="metric-val">$0.00</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="card-indicador"><div class="metric-label">Disponible Margen</div><div class="metric-val">$0.00</div></div>', unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #ffffff;'>⚡ MESA ALGORÍTMICA WATSON ULTRA</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8;'>Ecosistema de Monitoreo Táctico, Control de Riesgo y Bifurcación en Nube</p>", unsafe_allow_html=True)
st.markdown("---")

col_izq, col_der = st.columns([1.2, 1])

# --- Columna Izquierda: Actividad y Mitigación ---
with col_izq:
    st.markdown("### 📊 Monitoreo de Actividad y Mitigación")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        # Dinámico: Muestra OK si conectó con la tabla o FALLO_RE si no
        val_estado = "CONECTADO" if conexion_exitosa else "FALLO_RE"
        color_estado = "#10b981" if conexion_exitosa else "#ef4444"
        st.markdown(f'<div class="card-indicador"><div class="metric-label">Estado en Nube</div><div class="metric-val" style="color:{color_estado};">{val_estado}</div></div>', unsafe_allow_html=True)
    with c2:
        total_mechazos = len(df_mechazos) if not df_mechazos.empty else 0
        st.markdown(f'<div class="card-indicador"><div class="metric-label">Falsas Rupturas</div><div class="metric-val">{total_mechazos} Mechazos</div></div>', unsafe_allow_html=True)
    with c3:
        total_ahorrado = 0.0
        if not df_mechazos.empty and 'perdida_estimada_ahorrada' in df_mechazos.columns:
            total_ahorrado = df_mechazos['perdida_estimada_ahorrada'].astype(float).sum()
        st.markdown(f'<div class="card-indicador"><div class="metric-label">Capital Salvaguardado</div><div class="metric-val">${total_ahorrado:,.2f}</div></div>', unsafe_allow_html=True)

    st.markdown("#### 📈 Historial Reciente de Operaciones Real")
    if df_trades.empty:
        st.info("ℹ️ Esperando ejecuciones de órdenes desde Binance... Sin operaciones registradas en Supabase.")
    else:
        st.dataframe(df_trades, use_container_width=True)

# --- Columna Derecha: Consola Táctica ---
with col_der:
    st.markdown("### ⚙️ Panel de Infraestructura Táctica")
    
    if not conexion_exitosa:
        st.error("⚠️ Error de Red / Credenciales: No se pudo extraer la fila de configuración de 'control_bot'.")
        estado_bot = "INACTIVO"
        apalancamiento_actual = 1
        margen_maximo = 100.0
    else:
        config_actual = df_control.iloc[0]
        estado_bot = config_actual.get("estado_bot", "INACTIVO")
        apalancamiento_actual = int(config_actual.get("apalancamiento", 1))
        margen_maximo = float(config_actual.get("margen_maximo_usdt", 100.0))

    st.markdown('<div class="card-indicador">', unsafe_allow_html=True)
    st.markdown("#### Configuración Operativa Real")
    
    nuevo_estado = st.selectbox(
        "Modificar Estado Operativo Watson:",
        options=["ACTIVO", "PAUSADO", "INACTIVO", "MANTENIMIENTO"],
        index=["ACTIVO", "PAUSADO", "INACTIVO", "MANTENIMIENTO"].index(estado_bot) if estado_bot in ["ACTIVO", "PAUSADO", "INACTIVO", "MANTENIMIENTO"] else 2
    )
    
    nuevo_apalancamiento = st.slider(
        "Apalancamiento de Posiciones:", 
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
            st.error("❌ No se pueden guardar los cambios porque no hay conexión establecida con la base de datos.")
        else:
            payload = {
                "estado_bot": nuevo_estado,
                "apalancamiento": nuevo_apalancamiento,
                "margen_maximo_usdt": nuevo_margen
            }
            if enviar_actualizacion_tactica(payload):
                st.balloons()
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# Pie de página
st.markdown("---")
st.caption("Mesa Algorítmica Watson Ultra • DigitalOcean VPS • Conectores Supabase v1.1")
