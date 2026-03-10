import streamlit as st
import google.generativeai as genai
import time
import urllib.parse

# 1. DISEÑO VISUAL ACCESIBLE (24px, Alineación Izquierda Total)
st.set_page_config(page_title="Tu Chefcito 👨‍🍳", page_icon="👨‍🍳")

st.markdown("""
    <style>
    /* Fuente a 24px para todo el contenido */
    .stChatMessage, p, li, div, span {
        font-size: 24px !important;
        line-height: 1.5 !important;
        text-align: left !important;
    }
    
    /* Fuente a 24px en la cajetilla de entrada */
    .stChatInput textarea {
        font-size: 24px !important;
    }

    /* Alineación extrema a la izquierda (Sin burbujas ni sangrías) */
    [data-testid="stChatMessage"] {
        background-color: transparent !important;
        padding-left: 0px !important;
        margin-left: 0px !important;
    }
    [data-testid="stChatMessageContent"] {
        margin-left: 0px !important;
        padding-left: 0px !important;
    }

    /* Cabecera centrada e icónica */
    .header-container {
        text-align: center;
        margin-bottom: 20px;
    }
    .chef-icon { font-size: 80px !important; }
    .chef-title { font-size: 45px !important; font-weight: bold; margin-top: -10px; }
    
    /* Botón WhatsApp */
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

# 2. CONEXIÓN API
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Falta la API KEY en los Secrets de Streamlit.")
    st.stop()

# 3. EL CEREBRO DEL CHEF: MENTOR GENTIL Y TÁCTICO (ORDEN VERTICAL)
instrucciones_maestras = (
    "Eres 'Tu Chefcito', un mentor de cocina amable, gentil y divertido. \n\n"
    "REGLA DE ORO DE FORMATO (PARA MÓVIL):\n"
    "* Usa estas secciones en negrita: **Para comprar**, **Preparación**, **Tip de Oro**, **Información Nutricional**.\n"
    "* CADA EMOJI DEBE IR EN UNA LÍNEA NUEVA E INDEPENDIENTE. USA UN SALTO DE LÍNEA DOBLE DESPUÉS DE CADA LÍNEA.\n"
    "  📍 Para cada ingrediente.\n"
    "  🔥 Para cada paso de preparación.\n"
    "  💡 Para el Tip de Oro.\n"
    "* PROHIBIDO amontonar emojis o escribir en forma de párrafo.\n\n"
    "TONO Y BREVEDAD:\n"
    "* Sé un mentor táctico: máximo 15 PALABRAS por cada línea de emoji. Ve al grano.\n"
    "* Sé divertido: usa '¡Oído cocina!' o '¡A los fogones!' solo al inicio o cierre.\n"
    "* 'Información Nutricional' solo va UNA VEZ al final (sin números ni %). \n"
    "* Cierre único: 'Un cusicusa y estamos aquí'.\n\n"
    "MEMORIA:\n"
    "* Si ya sabes el país y comensales por el historial, no los vuelvas a pedir."
)

model = genai.GenerativeModel(
    model_name='gemini-2.5-flash', # Tu motor estable
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
            
            # Botón de WhatsApp
            text_for_url = urllib.parse.quote(full_text)
            whatsapp_html = f'<a href="https://wa.me/?text={text_for_url}" target="_blank" class="whatsapp-btn">📲 Compartir por WhatsApp</a>'
            st.markdown(whatsapp_html, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error al generar la respuesta: {e}")
