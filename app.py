import streamlit as st
import google.generativeai as genai
import time
import urllib.parse

# 1. DISEÑO VISUAL ACCESIBLE (Todo a 24px y Centrado)
st.set_page_config(page_title="Tu Chefcito 👨‍🍳", page_icon="👨‍🍳")

st.markdown("""
    <style>
    /* 1. Fuente de mensajes y textos generales */
    .stChatMessage, p, li, div, span {
        font-size: 24px !important;
        line-height: 1.3 !important;
    }
    
    /* 2. FUENTE DE LA CAJETILLA DE ENTRADA (Input) */
    /* Ajustamos el área de texto y el marcador de posición (placeholder) */
    .stChatInput textarea {
        font-size: 24px !important;
        line-height: 1.4 !important;
    }
    
    /* 3. Cabecera centrada y grande para identidad visual */
    .header-container {
        text-align: center;
        margin-bottom: 25px;
    }
    .chef-icon { font-size: 85px !important; }
    .chef-title { font-size: 50px !important; font-weight: bold; margin-top: -10px; }
    
    /* 4. Numeración pegada a la izquierda para ganar ancho en móvil */
    ol { padding-left: 25px !important; } 
    
    /* 5. Estilo del botón WhatsApp */
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
    st.error("Falta la API KEY en los Secrets.")
    st.stop()

# 3. EL CEREBRO DE TU CHEFCITO (Amable, Táctico y con Memoria)
instrucciones_maestras = (
    "Eres 'Tu Chefcito', un experto culinario amable, gentil y divertido.\n\n"
    "REGLAS DE FORMATO MÓVIL:\n"
    "* Usa EXCLUSIVAMENTE numeración (1., 2., 3.) para listas. PROHIBIDO usar viñetas.\n"
    "* Sé táctico y sintético: Ve al grano amablemente para evitar scroll excesivo.\n"
    "* Pasos: Máximo 15 palabras por cada número.\n\n"
    "REGLAS DE LÓGICA Y MEMORIA:\n"
    "* Memoria: Si ya sabes el país y comensales por el historial, NO los pidas de nuevo.\n"
    "* Sentido Común: Si piden postre y solo hay cosas saladas, detente y pide ingredientes dulces.\n"
    "* Tip de Oro: Comparte solo UN tip profesional de experiencia por cada receta.\n"
    "* Nutrición: Breve descripción adjetivada. PROHIBIDO usar números o el símbolo (%).\n\n"
    "IDENTIDAD Y CIERRE:\n"
    "* Inicio: '¡Hola! Soy Tu Chefcito 👨‍🍳. Un cusicusa y estamos aquí...'. Solo al empezar.\n"
    "* Despedida: Si el usuario termina, responde con cariño: '¡Fue un placer! Llámame cuando me necesites. Un cusicusa y estamos aquí'. No preguntes nada más."
)

model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
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
            
            # Botón de WhatsApp al final de la receta
            text_for_url = urllib.parse.quote(full_text)
            whatsapp_url = f"https://wa.me/?text={text_for_url}"
            
            st.markdown(f'<a href="{whatsapp_url}" target="_blank" class="whatsapp-btn">📲 Compartir por WhatsApp</a>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error al generar la respuesta: {e}")
