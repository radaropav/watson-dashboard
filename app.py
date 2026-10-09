import os
import requests
import hmac
import hashlib
import time
import streamlit as str_dynamic
import plotly.graph_objects as go
from dotenv import load_dotenv

load_dotenv()

str_dynamic.set_page_config(
    page_title="Mesa Algorítmica Watson Ultra",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    .stSelectbox [data-baseweb="select"] {
        background-color: #141a36 !important;
        border: 1px solid #242f63 !important;
        color: white !important;
    }
</style>
"""
str_dynamic.markdown(estilo_css_premium, unsafe_allow_html=True)

API_KEY_BINANCE = os.environ.get("BINANCE_API_KEY")
SECRET_KEY_BINANCE = os.environ.get("BINANCE_SECRET_KEY")
URL_BASE_SUPABASE = os.environ.get("URL_SUPABASE_TABLA")
KEY_MAESTRA_SUPABASE = os.environ.get("SUPABASE_KEY")

def generar_firma_binance(query_string):
    return hmac.new(SECRET_KEY_BINANCE.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

def obtener_balance_futuros_real():
    if not API_KEY_BINANCE or not SECRET_KEY_BINANCE:
        return {"total": 0.0, "disponible": 0.0, "mantenimiento": 0.0}
    
    timestamp = int(time.time() * 1000)
    query_string = f"timestamp={timestamp}&recvWindow=10000"
    firma = generar_firma_binance(query_string)
    
    endpoint_final = "https://binance.com"
    headers = {"X-MBX-APIKEY": API_KEY_BINANCE}
    params = {"timestamp": timestamp, "recvWindow": 10000, "signature": firma}
    
    try:
        respuesta = requests.get(endpoint_final, headers=headers, params=params, timeout=8)
        if respuesta.status_code == 200:
            datos = respuesta.json()
            return {
                "total": float(datos.get("totalWalletBalance", 0.0)),
                "disponible": float(datos.get("maxWithdrawAmount", 0.0)),
                "mantenimiento": float(datos.get("totalMaintMargin", 0.0))
            }
    except Exception:
        pass
    return {"total": 0.0, "disponible": 0.0, "mantenimiento": 0.0}

def obtener_headers_supabase():
    return {
        "apikey": KEY_MAESTRA_SUPABASE,
        "Authorization": f"Bearer {KEY_MAESTRA_SUPABASE}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

def consulting_master_row(instancia_id):
    if not URL_BASE_SUPABASE or not KEY_MAESTRA_SUPABASE:
        return {"estado": "MODO_LOCAL", "apalancamiento": 10, "porcentaje_capital": 35}
    
    headers = obtener_headers_supabase()
    endpoint = f"{URL_BASE_SUPABASE}?id=eq.{instancia_id}"
    
    try:
        respuesta = requests.get(endpoint, headers=headers, timeout=6)
        if respuesta.status_code == 200 and len(respuesta.json()) > 0:
            return respuesta.json()[0]
    except Exception:
        pass
    return {"estado": "FALLO_RED", "apalancamiento": 10, "porcentaje_capital": 35}

def actualizar_parametro_supabase(instancia_id, payload):
    if not URL_BASE_SUPABASE or not KEY_MAESTRA_SUPABASE:
        return False
    
    headers = obtener_headers_supabase()
    endpoint = f"{URL_BASE_SUPABASE}?id=eq.{instancia_id}"
    
    try:
        respuesta = requests.patch(endpoint, headers=headers, json=payload, timeout=6)
        return respuesta.status_code in [200, 201, 204]
    except Exception:
        return False

def consultar_metricas_tabla(nombre_tabla):
    if not URL_BASE_SUPABASE or not KEY_MAESTRA_SUPABASE:
        return []
    
    headers = obtener_headers_supabase()
    base_endpoint = URL_BASE_SUPABASE.split("?") if "?" in URL_BASE_SUPABASE else URL_BASE_SUPABASE
    endpoint = base_endpoint.replace("control_bot", nombre_tabla)
    
    try:
        respuesta = requests.get(endpoint, headers=headers, timeout=6)
        if respuesta.status_code == 200:
            return respuesta.json()
    except Exception:
        pass
    return []

str_dynamic.sidebar.markdown("<h2 style='color:#8b5cf6; text-align:center;'>WATSON QUANT</h2>", unsafe_allow_html=True)
str_dynamic.sidebar.markdown("---")

instancia_seleccionada = str_dynamic.sidebar.selectbox(
    "SELECCIÓN DE INFRAESTRUCTURA",
    ["Bot Depredador Estándar (4H)", "Bot Watson Pánico (15m)"]
)

id_instancia_actual = 1 if instancia_seleccionada == "Bot Depredador Estándar (4H)" else 2
activos_actuales = ["BTC", "ETH", "SOL", "BNB", "XRP"] if id_instancia_actual == 1 else ["BTC", "ETH", "SOL"]

str_dynamic.sidebar.markdown("<br><p class='metric-label'>Telemetría de Cuenta</p>", unsafe_allow_html=True)
balance_real = obtener_balance_futuros_real()

str_dynamic.sidebar.markdown(f"""
<div class='card-indicador'>
    <p class='metric-label'>Balance Total USDT</p>
    <p class='metric-val'>${balance_real['total']:.2f}</p>
</div>
<div class='card-indicador'>
    <p class='metric-label'>Disponible Margen</p>
    <p class='metric-val' style='color:#10b981;'>${balance_real['disponible']:.2f}</p>
</div>
""", unsafe_allow_html=True)

config_remota = consulting_master_row(id_instancia_actual)

str_dynamic.markdown("<h1 style='margin-bottom:0;'>Mesa Algorítmica Watson Elite</h1>", unsafe_allow_html=True)
str_dynamic.markdown(f"<p style='color:#94a3b8; font-size:14px; letter-spacing:1px;'>NÚCLEO MAESTRO ACTIVO: {instancia_seleccionada.upper()}</p>", unsafe_allow_html=True)
str_dynamic.markdown("---")

col_izq, col_der = str_dynamic.columns(2)

with col_izq:
    str_dynamic.markdown("### Rendimiento Cuantitativo Acumulado")
    datos_trades = consultar_metricas_tabla("historial_trades")
    
    if not datos_trades:
        str_dynamic.markdown(f"""
        <div style='background:rgba(20,24,50,0.4); border:1px dashed #242f63; padding:40px; border-radius:12px; text-align:center;'>
            <p style='color:#64748b; font-size:15px; margin:0;'>
                📊 Modo Pre-Evaluación de Mercado: Esperando registros reales de la tabla 'historial_trades' en Supabase para compilar la curva de ROI.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        precios_ejecutados = [float(t.get("precio", 0.0)) for t in datos_trades]
        fig_equity = go.Figure()
        fig_equity.add_trace(go.Scatter(
            y=precios_ejecutados,
            mode='lines+markers',
            line=dict(color='#7c3aed', width=3, shape='spline'),
            marker=dict(size=6, color='#10b981'),
            fill='tozeroy',
            fillcolor='rgba(124, 58, 237, 0.1)'
        ))
        fig_equity.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(showgrid=False, color='#475569'),
            yaxis=dict(showgrid=True, gridcolor='#1e293b', color='#475569')
        )
        str_dynamic.plotly_chart(fig_equity, use_container_width=True)

    str_dynamic.markdown("<br>### Monitoreo de Actividad y Mitigación", unsafe_allow_html=True)
    c1, c2, c3 = str_dynamic.columns(3)
    
    with c1:
        estado_actual_txt = str(config_remota.get("estado", "OFF")).upper()
        color_estado = "#10b981" if estado_actual_txt in ["PREDADOR", "APLANAMIENTO"] else "#ef4444"
        str_dynamic.markdown(f"""
        <div class='card-indicador'>
            <p class='metric-label'>Estado en Nube</p>
            <p class='metric-val' style='color:{color_estado};'>{estado_actual_txt}</p>
        </div>
        """, unsafe_allow_html=True)
        
    with c2:
        datos_mechazos = consultar_metricas_tabla("registro_mechazos")
        str_dynamic.markdown(f"""
        <div class='card-indicador'>
            <p class='metric-label'>Falsas Rupturas</p>
            <p class='metric-val'>{len(datos_mechazos)} Mechazos</p>
        </div>
        """, unsafe_allow_html=True)
        
    with c3:
        suma_ahorrada = sum([float(m.get("perdida_estimada_ahorrada", 0.0)) for m in datos_mechazos])
        str_dynamic.markdown(f"""
        <div class='card-indicador'>
            <p class='metric-label'>Capital Salvaguardado</p>
            <p class='metric-val' style='color:#10b981;'>${suma_ahorrada:.2f}</p>
        </div>
        """, unsafe_allow_html=True)

with col_der:
    str_dynamic.markdown("### Consola de Infraestructura Táctica")
    str_dynamic.markdown("<p class='metric-label'>Canasta del Módulo</p>", unsafe_allow_html=True)
