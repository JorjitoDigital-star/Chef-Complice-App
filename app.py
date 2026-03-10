import streamlit as st
import google.generativeai as genai
import time
import urllib.parse

# 1. DISEÑO VISUAL PREMIUM (Logo, 24px y Alineación Izquierda)
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

    /* 4. Cabecera centrada para el logo (Sin título de texto) */
    .header-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        margin-bottom: 30px; /* Un poco más de espacio abajo */
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

# Renderizado de Cabecera: Solo el Logo (Limpio y minimalista)
st.markdown('<div class="header-container">', unsafe_allow_html=True)
try:
    # Mostramos tu logo de 2000px con un ancho visual elegante
    st.image("logo.png", width=250) 
except:
    st.warning("⚠️ Sube tu archivo 'logo.png' a GitHub para verlo aquí.")
st.markdown('</div>', unsafe_allow_html=True)

# 2. CONEXIÓN API
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Falta la API KEY en los Secrets de Streamlit.")
    st.stop()

# 3. EL CEREBRO DEL CHEF: MENTOR GENTIL, DIVERTIDO Y TÁCTICO
instrucciones_maestras = (
    "Eres 'Tu Chefcito', un mentor de cocina amable, gentil y divertido. \n\n"
    "REGLA DE IDENTIDAD:\n"
    "* El usuario es el 'cocinero' o 'cocinera'. NUNCA llames al usuario 'Chefcito'.\n"
    "* Si el usuario te da las gracias, responde: 'De nada' o 'Con todo gusto, cocinero(a)'.\n\n"
    "REGLA DE FORMATO VISUAL (ESTRICTA):\n"
    "* Usa estas secciones en negrita: **Para comprar**, **Preparación**, **Tip de Oro**, **Información Nutricional**.\n"
    "* SALTO DE LÍNEA POST-TÍTULO: Tras el título en negrita, DEJA UNA LÍNEA EN BLANCO antes del primer emoji.\n"
    "* DICCIONARIO DE EMOJIS ESTRICTO:\n"
    "  📍 SOLO para ingredientes (en **Para comprar**).\n"
    "  🔥 SOLO para pasos de cocina (en **Preparación**).\n"
    "  💡 SOLO para consejos (en **Tip de Oro**).\n"
    "* CADA EMOJI DEBE SER UN PÁRRAFO INDEPENDIENTE CON UNA LÍNEA EN BLANCO ENTRE ELLOS.\n"
    "* PROHIBIDO usar números o viñetas normales (*).\n\n"
    "TONO Y BREVEDAD:\n"
    "* Máximo 15 PALABRAS por cada línea de emoji. Sé táctico.\n"
    "* Sé divertido: usa '¡Oído cocina!' o '¡A los fogones!' brevemente.\n"
    "* 'Información Nutricional' se mantiene como descripción breve al final.\n"
    "* Cierre único: 'Un cusicusa y estamos aquí'.\n\n"
    "MEMORIA:\n"
    "* Si ya sabes el país y comensales por el historial, no los vuelvas a pedir."
)

model = genai.GenerativeModel(
    model_name='gemini-2.5-flash', # Tu motor estable de 2026
    system_instruction=instrucciones_maestras
)

# 4. GESTIÓN DE CHAT
if "messages" not in st.session_state:
    st.session_state.messages = []
    bienvenida = "¡Hola! Soy **Tu Chefcito** 👨‍🍳. Un cusicusa y estamos aquí... \n\n¿En qué país estás, qué ingredientes tienes y para cuántos cocinamos?"
    st.session_state.messages.append({"role": "assistant", "content": bienvenida})

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 5. INTERACCIÓN Y COMPARTIR
if prompt := st.chat_input("Dime tus ingredientes..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        history = [
            {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]}
            for m in st.session_state.messages[:-1]
        ]
        chat = model.start_chat(history=history)
        
        try:
            response = chat.send_message(prompt, stream=True)
            placeholder = st.empty()
            full_text = ""
            for chunk in response:
                if chunk.text:
                    full_text += chunk.text
                    placeholder.markdown(full_text + "▌")
                    time.sleep(0.01)
            placeholder.markdown(full_text)
            st.session_state.messages.append({"role": "assistant", "content": full_text})
            
            # Botón de WhatsApp (CORREGIDO: Paréntesis cerrado correctamente)
            text_for_url = urllib.parse.quote(full_text)
            whatsapp_html = f'<a href="https://wa.me/?text={text_for_url}" target="_blank" class="whatsapp-btn">📲 Compartir por WhatsApp</a>'
            st.markdown(whatsapp_html, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error: {e}")
