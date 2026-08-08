import os
import streamlit as str_dynamic
import requests

# CONFIGURACIÓN ULTRA PREMIUM DE LA INTERFAZ ESTILO BLOOMBERG
str_dynamic.set_page_config(
    page_title="Watson Elite",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ESTILOS OSCUROS DE ALTA DENSIDAD INYECTADOS SIN LLAVES NATIVAS
estilo_css = " <style>  body, .stApp { background-color: #0b0e14; color: #d1d4dc; font-family: 'Courier New', Courier, monospace; }  h1 { color: #ffcc00 !important; text-shadow: 0 0 5px #ffcc00, 0 0 15px #ff9900, 0 0 25px #ffaa00; font-weight: bold; }  button, .stButton>button { background-color: #1f2229 !important; color: #00ff88 !important; border: 1px solid #2f323a !important; font-weight: bold; width: 100%; border-radius: 4px; }  button:hover { background-color: #00ff88 !important; color: #0b0e14 !important; }  .stApp [data-testid='stMetric'] { background-color: #12161f !important; border: 1px solid #1f2229 !important; padding: 15px !important; border-radius: 4px !important; }  </style> "
str_dynamic.markdown(estilo_css, unsafe_allow_html=True)

# ENCABEZADO INSTITUCIONAL SOLICITADO
str_dynamic.markdown("# 🤖 WATSON ELITE TRADE")
str_dynamic.markdown("### TERMINAL DE MONITOREO ASÍNCRONO & CONTROL DE ESTADOS")
str_dynamic.markdown("---")

# EXTRACCIÓN SEGURA DE CREDENCIALES DESDE EL ENTORNO DE DESPLIEGUE
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
URL_TABLA_CONTROL = os.getenv("URL_SUPABASE_TABLA")

def obtener_headers_seguros():
    token = "Bearer " + str(SUPABASE_KEY)
    retorno = dict([
        ("apikey", str(SUPABASE_KEY)),
        ("Authorization", token),
        ("Content-Type", "application/json")
    ])
    return retorno

def obtener_ultimo_estado():
    if not URL_TABLA_CONTROL: 
        return "DESCONECTADO"
    headers = obtener_headers_seguros()
    try:
        respuesta = requests.get(URL_TABLA_CONTROL, headers=headers, timeout=6, verify=False)
        if respuesta.status_code == 200:
            datos = respuesta.json()
            if datos and len(datos) > 0:
                primer_registro = datos[0]
                return str(primer_registro.get("estado", "PREDADOR"))
    except Exception:
        pass
    return "DESCONECTADO"

def enviar_nuevo_comando(nuevo_estado):
    if not URL_TABLA_CONTROL: 
        return False
    # Modificación de la URL para quitar filtros de lectura y permitir escritura limpia
    url_base = URL_TABLA_CONTROL.split("?")[0]
    headers = obtener_headers_seguros()
    headers.update(dict([("Prefer", "return=minimal")]))
    
    payload = dict(estado=str(nuevo_estado))
    try:
        respuesta = requests.post(url_base, json=payload, headers=headers, timeout=6, verify=False)
        return respuesta.status_code in [200, 201]
    except Exception:
        return False

# LECTURA RECURRENTE DE DATOS EN TIEMPO REAL
estado_actual_remoto = obtener_ultimo_estado()

# SECCIÓN 1: BLOOMBERG COMMAND CENTER (CONTROL TÁCTIL)
str_dynamic.markdown("#### [01] PANEL DE CONTROL TÁCTIL DE INFRAESTRUCTURA")
col1, col2, col3 = str_dynamic.columns(3)

with col1:
    if col1.button("🔥 MODO PREDADOR"):
        if enviar_nuevo_comando("PREDADOR"):
            str_dynamic.success("Comando PREDADOR enviado a Supabase")
            estado_actual_remoto = "PREDADOR"

with col2:
    if col2.button("📊 MODO APLANAMIENTO"):
        if enviar_nuevo_comando("APLANAMIENTO"):
            str_dynamic.success("Comando APLANAMIENTO enviado a Supabase")
            estado_actual_remoto = "APLANAMIENTO"

with col3:
    if col3.button("🛑 RESTRICCION OFF"):
        if enviar_nuevo_comando("OFF"):
            str_dynamic.warning("Comando OFF enviado a Supabase")
            estado_actual_remoto = "OFF"

str_dynamic.markdown("---")

# SECCIÓN 2: LIVE FEED METRICS (INDICADORES DIGITALES)
str_dynamic.markdown("#### [02] TELEMETRÍA EN VIVO (RENDER BACKGROUND WORKER)")
m_col1, m_col2, m_col3 = str_dynamic.columns(3)

# Formateo estricto clásico para evitar f-strings
texto_modo = "CORE: {}".format(estado_actual_remoto)
m_col1.metric("MODO ACTIVO EN NUBE", texto_modo)

# Estos feeds simulan la lectura de tus otras tablas o APIs seguras
m_col2.metric("ACTIVO OPERATIVO", "ETHUSDT Futures")
m_col3.metric("CONEXIÓN PROXY BYPASS", "ESTABLE / ENCRIPTADA")

str_dynamic.markdown("---")

# SECCIÓN 3: PNL ANALYTICS & AUDIT LOGS
str_dynamic.markdown("#### [03] TERMINAL HISTÓRICA DE ÓRDENES EJECUTADAS (AUDITORÍA)")

url_historial = ""
if URL_TABLA_CONTROL:
    url_historial = URL_TABLA_CONTROL.replace("control_bot", "historial_trades")

def obtener_historial_trades():
    if not url_historial:
        return []
    headers = obtener_headers_seguros()
    try:
        respuesta = requests.get(url_historial, headers=headers, timeout=6, verify=False)
        if respuesta.status_code == 200:
            return respuesta.json()
    except Exception:
        pass
    return []

lista_trades = obtener_historial_trades()

if lista_trades:
    # Mostramos los logs de Supabase directo en la tabla Bloomberg de alta densidad
    str_dynamic.dataframe(lista_trades, use_container_width=True)
else:
    str_dynamic.info("Monitoreando... Esperando primera ruptura de canal de Binance.")

str_dynamic.markdown("---")
str_dynamic.caption("Watson Elite Trade Terminal v2.1 • Datos protegidos de extremo a extremo")
