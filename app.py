import streamlit as st
import google.generativeai as genai
import time
import urllib.parse

# 1. DISEÑO DE INTERFAZ MÓVIL (Centrado y 24px)
st.set_page_config(page_title="Tu Chefcito 👨‍🍳", page_icon="👨‍🍳")

st.markdown("""
    <style>
    /* Estilo para lectura cómoda en móviles */
    .stChatMessage, p, li, div, span {
        font-size: 24px !important;
        line-height: 1.3 !important;
    }
    /* Cabecera centrada */
    .header-container {
        text-align: center;
        margin-bottom: 20px;
    }
    .chef-icon { font-size: 80px !important; }
    .chef-title { font-size: 45px !important; font-weight: bold; }
    /* Ajuste de numeración para ganar espacio horizontal */
    ol { padding-left: 25px !important; } 
    
    /* Estilo de los botones de compartir */
    .share-btn {
        display: inline-block;
        padding: 10px 20px;
        background-color: #25D366;
        color: white !important;
        text-decoration: none;
        border-radius: 10px;
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .copy-btn {
        background-color: #f0f2f6;
        color: #31333F;
        border: 1px solid #dcdde1;
        cursor: pointer;
        padding: 10px 20px;
        border-radius: 10px;
        font-size: 18px;
        font-weight: bold;
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
    st.error("Falta la API KEY en Secrets.")
    st.stop()

# 3. EL CEREBRO TÁCTICO, AMABLE Y GENTIL
instrucciones_maestras = (
    "Eres 'Tu Chefcito', un experto culinario amable, gentil y divertido. \n\n"
    "REGLAS DE FORMATO MÓVIL:\n"
    "* Usa ÚNICAMENTE numeración (1., 2., 3.) para listas. PROHIBIDO usar viñetas (*).\n"
    "* Sé un 10% más sintético para evitar scroll excesivo. Ve al grano con amabilidad.\n"
    "* Pasos: Máximo 15 palabras por cada número. \n\n"
    "REGLAS DE LÓGICA Y MEMORIA:\n"
    "* Memoria: Si ya sabes el país y comensales por el historial, no los pidas de nuevo.\n"
    "* Sentido Común: Si piden postre y solo hay cosas saladas, detente y pide ingredientes dulces.\n"
    "* Tip de Oro: Da solo UN tip profesional de experiencia por receta. \n"
    "* Nutrición: Breve descripción adjetivada. PROHIBIDO usar números o el símbolo (%).\n\n"
    "IDENTIDAD Y CIERRE:\n"
    "* Inicio: '¡Hola! Soy Tu Chefcito 👨‍🍳. Un cusicusa y estamos aquí...'. Solo al empezar.\n"
    "* Despedida: Si el usuario termina, di con cariño: '¡Fue un placer! Llámame cuando me necesites. Un cusicusa y estamos aquí'. No preguntes nada más."
)

model = genai.GenerativeModel(
    model_name='gemini-2.5-flash', # Mantengo el nombre que te funcionó
    system_instruction=instrucciones_maestras
)

# 4. GESTIÓN DE CHAT
if "messages" not in st.session_state:
    st.session_state.messages = []
    bienvenida = "¡Hola! Soy **Tu Chefcito** 👨‍🍳. Un cusicusa y estamos aquí... \n\n¿En qué país estás, qué tienes en la cocina y para cuántos somos?"
    st.session_state.messages.append({"role": "assistant", "content": bienvenida})

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 5. INTERACCIÓN Y FUNCIONES
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
            
            # --- SECCIÓN DE COMPARTIR (Sin Correo y con Copiar arreglado) ---
            text_for_url = urllib.parse.quote(full_text)
            
            # Reemplazamos el botón de Copiar por uno con JavaScript para que funcione en móviles
            st.markdown(f"""
                <div style="display: flex; gap: 10px; margin-top: 15px;">
                    <a href="https://wa.me/?text={text_for_url}" target="_blank" class="share-btn">📲 WhatsApp</a>
                    <button onclick="navigator.clipboard.writeText(`{full_text.replace('`', "'")}`).then(() => alert('¡Receta copiada al portapapeles!'))" class="copy-
