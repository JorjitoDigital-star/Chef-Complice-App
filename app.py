import streamlit as st
import google.generativeai as genai
import time
import urllib.parse

# 1. DISEÑO VISUAL MÓVIL (Alineación izquierda extrema y 24px)
st.set_page_config(page_title="Tu Chefcito 👨‍🍳", page_icon="👨‍🍳")

st.markdown("""
    <style>
    /* 1. Todo el texto a 24px para máxima legibilidad */
    .stChatMessage, p, li, div, span {
        font-size: 24px !important;
        line-height: 1.4 !important;
        text-align: left !important;
    }
    
    /* 2. Cajetilla de entrada a 24px */
    .stChatInput textarea {
        font-size: 24px !important;
    }

    /* 3. Alineación 'Zero Margin' para ganar espacio lateral */
    [data-testid="stChatMessage"] {
        background-color: transparent !important;
        padding-left: 0px !important;
        margin-left: 0px !important;
    }
    [data-testid="stChatMessageContent"] {
        margin-left: 0px !important;
        padding-left: 0px !important;
    }

    /* 4. Cabecera de identidad centrada */
    .header-container {
        text-align: center;
        margin-bottom: 20px;
    }
    .chef-icon { font-size: 80px !important; }
    .chef-title { font-size: 45px !important; font-weight: bold; margin-top: -10px; }
    
    /* 5. Botón de WhatsApp estilizado */
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
    
    <div class="header-container">
        <div class="chef-icon">👨‍🍳</div>
        <div class="chef-title">Tu Chefcito</div>
    </div>
    """, unsafe_allow_html=True)

# 2. CONEXIÓN API (Usando el motor 2.5 estable)
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Falta la API KEY en los Secrets de Streamlit.")
    st.stop()

# 3. EL CEREBRO DE TU CHEFCITO (Formato de Emojis y Negritas)
instrucciones_maestras = (
    "Eres 'Tu Chefcito', un experto amable y divertido.\n\n"
    "REGLAS DE FORMATO (ESTRICTAS):\n"
    "* Usa estas secciones en negrita: **Para comprar**, **Preparación**, **Tip de Oro**, **Información Nutricional**.\n"
    "* PROHIBIDO usar números (1., 2.) o viñetas de punto (*).\n"
    "* Cada instrucción DEBE empezar con su emoji en una NUEVA LÍNEA:\n"
    "  📍 Para ingredientes (debajo de **Para comprar**).\n"
    "  🔥 Para pasos (debajo de **Preparación**).\n"
    "  💡 Para el tip (debajo de **Tip de Oro**).\n\n"
    "REGLAS DE TONO Y BREVEDAD:\n"
    "* Sé 10% más sintético: evita introducciones largas. Ve al grano con alegría.\n"
    "* Máximo 15 palabras por cada línea de emoji.\n"
    "* Usa 'Un cusicusa y estamos aquí' solo para saludar o despedir.\n\n"
    "REGLAS DE LÓGICA Y MEMORIA:\n"
    "* Si ya conoces el país y comensales, no los pidas de nuevo.\n"
    "* Nutrición: Descripción breve, adjetivada y SIN números ni porcentajes."
)

model = genai.GenerativeModel(
    model_name='gemini-2.5-flash', # Motor estable confirmado por Jorge
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

# 5. INTERACCIÓN Y WHATSAPP
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
        
        # Estructura try/except perfectamente alineada para evitar SyntaxError
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
            
            # Botón de WhatsApp al margen izquierdo
            text_for_url = urllib.parse.quote(full_text)
            whatsapp_html = '<a href="https://wa.me/?text={0}" target="_blank" class="whatsapp-btn">📲 Compartir por WhatsApp</a>'.format(text_for_url)
            st.markdown(whatsapp_html, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error al generar la respuesta: {e}")
