import streamlit as st
import google.generativeai as genai
import time
import urllib.parse

# 1. DISEÑO VISUAL PREMIUM (24px, Alineación Izquierda y Logo)
st.set_page_config(page_title="Tu Chefcito 👨‍🍳", page_icon="👨‍🍳")

st.markdown("""
    <style>
    /* 1. Todo el contenido a 24px para máxima claridad */
    .stChatMessage, p, li, div, span {
        font-size: 24px !important;
        line-height: 1.5 !important;
        text-align: left !important;
    }
    
    /* 2. Cajetilla de entrada a 24px */
    .stChatInput textarea {
        font-size: 24px !important;
    }

    /* 3. Alineación 'Zero Margin' (Texto pegado al borde izquierdo) */
    [data-testid="stChatMessage"] {
        background-color: transparent !important;
        padding-left: 0px !important;
        margin-left: 0px !important;
    }
    [data-testid="stChatMessageContent"] {
        margin-left: 0px !important;
        padding-left: 0px !important;
    }

    /* 4. Cabecera centrada para el logo */
    .header-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        margin-bottom: 30px;
    }
    
    /* 5. Botón WhatsApp sofisticado */
    .whatsapp-btn {
        display: inline-block;
        padding: 14px 25px;
        background-color: #25D366;
        color: white !important;
        text-decoration: none;
        border-radius: 12px;
        font-size: 20px;
        font-weight: bold;
        margin-top: 15px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# Renderizado de Cabecera: Solo el Logo
st.markdown('<div class="header-container">', unsafe_allow_html=True)
try:
    st.image("logo.png", width=250) 
except:
    st.warning("⚠️ Sube tu archivo 'logo.png' a GitHub.")
st.markdown('</div>', unsafe_allow_html=True)

# 2. CONEXIÓN API Y CONFIGURACIÓN DE SEGURIDAD
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Falta la API KEY en los Secrets de Streamlit.")
    st.stop()

# Ajuste de Seguridad para evitar bloqueos por términos culinarios
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

# 3. EL CEREBRO DEL CHEF: MENTOR GENTIL Y TÁCTICO
instrucciones_maestras = (
    "Eres 'Tu Chefcito', un mentor de cocina amable, gentil y divertido. \n\n"
    "REGLA DE IDENTIDAD:\n"
    "* El usuario es el 'cocinero' o 'cocinera'. NUNCA llames al usuario 'Chefcito'.\n"
    "* Si el usuario te da las gracias, responde: 'De nada' o 'Con todo gusto, cocinero(a)'.\n\n"
    "REGLA DE FORMATO VISUAL (ESTRICTA):\n"
    "* Usa estas secciones en negrita: **Para comprar**, **Preparación**, **Tip de Oro**, **Información Nutricional**.\n"
    "* SALTO DE LÍNEA POST-TÍTULO: Tras el título en negrita, DEJA UNA LÍNEA EN BLANCO antes del primer emoji.\n"
    "* DICCIONARIO DE EMOJIS
