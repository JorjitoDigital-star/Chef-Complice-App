import streamlit as st
import google.generativeai as genai
import time
import urllib.parse

# 1. DISEÑO VISUAL PARA MÓVILES (Logo centrado y 24px)
st.set_page_config(page_title="Tu Chefcito 👨‍🍳", page_icon="👨‍🍳")

st.markdown("""
    <style>
    /* Estilo de lectura cómoda */
    .stChatMessage, p, li, div, span {
        font-size: 24px !important;
        line-height: 1.3 !important;
    }
    /* Cabecera centrada y grande */
    .header-container {
        text-align: center;
        margin-bottom: 25px;
    }
    .chef-icon { font-size: 85px !important; }
    .chef-title { font-size: 50px !important; font-weight: bold; margin-top: -10px; }
    
    /* Numeración pegada a la izquierda */
    ol { padding-left: 25px !important; } 
    
    /* Diseño de botones de compartir */
    .share-btn {
        display: inline-block;
        padding: 12px 20px;
        background-color: #25D366;
        color: white !important;
        text-decoration: none;
        border-radius: 12px;
        font-size: 18px;
        font-weight: bold;
    }
    .copy-btn {
        display: inline-block;
        padding: 12px 20px;
        background-color: #f0f2f6;
        color: #31333F;
        border: 1px solid #dcdde1;
        border-radius: 12px;
        font-size: 18px;
        font-weight: bold;
        cursor: pointer;
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
    st.error("Falta la API KEY en Secrets de Streamlit.")
    st.stop()

# 3. EL CEREBRO DE TU CHEFCITO (Amable y Táctico)
instrucciones_maestras = (
    "Eres 'Tu Chefcito', un experto culinario amable, gentil y divertido. \n\n"
    "REGLAS DE FORMATO MÓVIL:\n"
    "* Usa EXCLUSIVAMENTE numeración (1., 2., 3.) para listas. PROHIBIDO usar viñetas (*).\n"
    "* Sé un 10% más sintético: Ve al grano amablemente para evitar scroll excesivo.\n"
    "* Pasos: Máximo 15 palabras por cada número.\n\n"
    "REGLAS DE LÓGICA Y MEMORIA:\n"
    "* Memoria: Si ya sabes el país y comensales por el historial, no los pidas de nuevo.\n"
    "* Sentido Común: Si piden postre y solo hay cosas saladas, detente amablemente y pide ingredientes dulces.\n"
    "* Tip de Oro: Da solo UN tip profesional de experiencia por receta.\n"
    "* Nutrición: Breve descripción adjetivada. PROHIBIDO usar números o el símbolo (%).\n\n"
    "IDENTIDAD Y CIERRE:\n"
    "* Inicio: '¡Hola! Soy Tu Chefcito 👨‍🍳. Un cusicusa y estamos aquí...'. Solo al empezar.\n"
    "* Despedida: Si el usuario agradece o termina, responde con cariño: '¡Fue un placer! No dudes en llamarme cuando necesites otra mano en la cocina. Un cusicusa y estamos aquí'. No preguntes nada más."
)

model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    system_instruction=instrucciones_maestras
)

# 4. GESTIÓN DE CHAT
if "messages" not in st.session_state:
    st.session_state.messages = []
    bienvenida = "¡Hola! Soy **Tu Chefcito** 👨‍🍳. Un cusicusa y estamos aquí... \n\n¿En qué país estás, qué tienes y para cuántos cocinamos?"
    st.session_state.messages.append({"role": "assistant", "content": bienvenida})

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 5. INTERACCIÓN Y FUNCIONES DE COMPARTIR
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
        
        # --- BLOQUE TRY/EXCEPT CORREGIDO POR TU COLEGA ---
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
            
            # --- SECCIÓN DE COMPARTIR (Sin errores de comillas) ---
            text_for_url = urllib.parse.quote(full_text)
            clean_text = full_text.replace("'", "\\'").replace("\n", "\\n")
            
            # Usamos .format() para evitar el conflicto de llaves del f-string
            button_html = """
            <div style="display: flex; gap: 10px; margin-top: 15px;">
                <a href="https://wa.me/?text={0}" target="_blank" class="share-btn">📲 WhatsApp</a>
                <button onclick="navigator.clipboard.writeText('{1}').then(() => alert('¡Receta copiada al portapapeles!'))" class="copy-btn">📋 Copiar Receta</button>
            </div>
            """.format(text_for_url, clean_text)
            
            st.markdown(button_html, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error al generar la respuesta: {e}")
