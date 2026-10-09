import streamlit as st
import pandas as pd
import requests
import os

# ==========================================
# 1. CONFIGURACIÓN DE PÁGINA E INTERFAZ
# ==========================================
st.set_page_config(
    page_title="Control AlgoCuant Watson - Maestro",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🤖 CONTROL ALGOCUANT WATSON")
st.subheader("Panel Táctico de Monitoreo, Control de Riesgo y Bifurcación")

# ==========================================
# 2. GESTIÓN MULTI-VARIABLE DE CREDENCIALES
# ==========================================
# Intenta cargar buscando variaciones comunes en Secrets o Variables de Entorno (.env)
SUPABASE_URL = (
    st.secrets.get("SUPABASE_URL") or 
    st.secrets.get("supabase_url") or 
    st.secrets.get("supabase", {}).get("url") or 
    os.getenv("SUPABASE_URL") or 
    os.getenv("supabase_url") or ""
)

SUPABASE_KEY = (
    st.secrets.get("SUPABASE_KEY") or 
    st.secrets.get("supabase_key") or 
    st.secrets.get("supabase", {}).get("key") or 
    os.getenv("SUPABASE_KEY") or 
    os.getenv("supabase_key") or ""
)

# Si fallan todas las búsquedas automáticas, te muestra qué nombres intentó buscar
if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("🚨 Error Crítico: No se encontraron las credenciales en Secrets.")
    st.info("💡 Asegúrate de que en la configuración de **Secrets de Streamlit Cloud** estén declaradas exactamente así:\n"
            "```toml\n"
            "SUPABASE_URL = \"tu_url_aqui\"\n"
            "SUPABASE_KEY = \"tu_llave_aqui\"\n"
            "```\n"
            "O de esta forma si usas bloques:\n"
            "```toml\n"
            "[supabase]\n"
            "url = \"tu_url_aqui\"\n"
            "key = \"tu_llave_aqui\"\n"
            "```")
    st.stop()

# Limpieza segura de la URL
SUPABASE_URL = str(SUPABASE_URL).strip().rstrip("/")

# Cabeceras globales para la API de Supabase
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# ==========================================
# 3. FUNCIONES DE CONEXIÓN A BASE DE DATOS
# ==========================================
@st.cache_data(ttl=10)
def consultar_tabla(tabla: str):
    """Consulta datos de Supabase de manera limpia y directa."""
    url = f"{SUPABASE_URL}/rest/v1/{tabla}"
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            return pd.DataFrame(response.json())
        else:
            return pd.DataFrame()
    except requests.exceptions.RequestException:
        return pd.DataFrame()

def enviar_actualizacion_tactica(payload: dict):
    """Envía actualizaciones mediante PATCH a la tabla 'control_bot' para el ID 1."""
    url = f"{SUPABASE_URL}/rest/v1/control_bot?id=eq.1"
    headers_patch = {**HEADERS, "Prefer": "return=minimal"}
    
    try:
        response = requests.patch(url, headers=headers_patch, json=payload)
        if response.status_code == 200 or response.status_code == 204:
            st.success("✅ Parámetros tácticos actualizados en Supabase con éxito.")
            return response
        else:
            st.error(f"❌ Error al actualizar control: Código {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"📡 FALLO_RED Crítico en Consola Táctica (PATCH): {e}")
        return None

# ==========================================
# 4. CARGA Y PROCESAMIENTO DE DATOS REALES
# ==========================================
df_control = consultar_tabla("control_bot")
df_trades = consultar_tabla("historial_trades")
df_mechazos = consultar_tabla("registro_mechazos")

# ==========================================
# 5. MAQUETACIÓN DEL DASHBOARD (2 COLUMNAS)
# ==========================================
col_izquierda, col_derecha = st.columns(2)

# ------------------------------------------
# COLUMNA IZQUIERDA: MÉTRICAS E HISTORIAL
# ------------------------------------------
with col_izquierda:
    st.header("📊 Métricas de Rendimiento Real (USDT)")
    
    st.subheader("📈 Historial Reciente de Operaciones")
    if df_trades.empty:
        st.info("ℹ️ Esperando datos reales de operaciones desde Binance... La tabla en Supabase está vacía actualmente.")
    else:
        st.dataframe(df_trades, use_container_width=True)
        
    st.subheader("🛡️ Mitigación de Riesgos e Impacto")
    if df_mechazos.empty:
        st.warning("No se registran mitigaciones activas en 'registro_mechazos'.")
    else:
        columnas_disponibles = df_mechazos.columns.tolist()
        columna_objetivo = 'perdida_estimada_ahorrada'
        
        if columna_objetivo in columnas_disponibles:
            total_ahorrado = df_mechazos[columna_objetivo].astype(float).sum()
            st.metric(label="💰 Pérdida Total Estimada Ahorrada", value=f"{total_ahorrado:,.2f} USDT")
            st.dataframe(df_mechazos, use_container_width=True)
        else:
            st.error(f"⚠️ Error de esquema: No se encuentra la columna '{columna_objetivo}' en la base de datos.")
            st.dataframe(df_mechazos, use_container_width=True)

# ------------------------------------------
# COLUMNA DERECHA: CONSOLA TÁCTICA DE CONTROL
# ------------------------------------------
with col_derecha:
    st.header("⚙️ Consola Táctica")
    
    if df_control.empty:
        st.warning("⚠️ No se pudieron cargar los estados de control desde 'control_bot'. Verifique la conexión o las credenciales.")
    else:
        config_actual = df_control.iloc[0]
        
        estado_bot = config_actual.get("estado_bot", "INACTIVO")
        apalancamiento_actual = int(config_actual.get("apalancamiento", 1))
        margen_maximo = float(config_actual.get("margen_maximo_usdt", 100.0))
        
        st.subheader("Control Operativo")
        
        nuevo_estado = st.selectbox(
            "Estado del Ecosistema Watson:",
            options=["ACTIVO", "PAUSADO", "INACTIVO", "MANTENIMIENTO"],
            index=["ACTIVO", "PAUSADO", "INACTIVO", "MANTENIMIENTO"].index(estado_bot) if estado_bot in ["ACTIVO", "PAUSADO", "INACTIVO", "MANTENIMIENTO"] else 2
        )
        
        nuevo_apalancamiento = st.slider(
            "Multiplicador de Apalancamiento:", 
            min_value=1, 
            max_value=20, 
            value=apalancamiento_actual
        )
        
        nuevo_margen = st.number_input(
            "Margen Máximo Asignado (USDT):", 
            min_value=10.0, 
            max_value=100000.0, 
            value=margen_maximo,
            step=50.0
        )
        
        if st.button("🚀 Enviar Cambios Estratégicos", use_container_width=True):
            payload_actualizacion = {
                "estado_bot": nuevo_estado,
                "apalancamiento": nuevo_apalancamiento,
                "margen_maximo_usdt": nuevo_margen
            }
            
            resultado = enviar_actualizacion_tactica(payload_actualizacion)
            if resultado:
                st.balloons()
                st.rerun()

# ==========================================
# 6. PIE DE PÁGINA INFORMATIVO
# ==========================================
st.markdown("---")
st.caption("Ecosistema Algocuant Watson • VPS DigitalOcean Activo • Repositorio Corporativo Privado • Supabase DB")
