import streamlit as st
import google.generativeai as genai
import time
import urllib.parse

# 1. DISEÑO DE INTERFAZ MÓVIL (Centrado y 24px)
st.set_page_config(page_title="Tu Chefcito 👨‍🍳", page_icon="👨‍🍳")

# CSS para centrar cabecera y ajustar texto en móviles
st.markdown("""
    <style>
    .stChatMessage, p, li, div, span {
        font-size: 24px !important;
        line-height: 1.3 !important;
    }
    .header-container {
        text-align: center;
        margin-bottom: 20px;
    }
    .chef-icon { font-size: 80px !important; }
    .chef-title { font-size: 45px !important; font-weight: bold; }
    /* Ajuste para que la numeración pegue a la izquierda */
    ol { padding-left: 25px !important; } 
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

# 3. EL CEREBRO TÁCTICO Y AMABLE
instrucciones_maestras = (
    "Eres 'Tu Chefcito', un experto culinario amable, gentil y divertido. \n\n"
    "REGLAS DE FORMATO MÓVIL:\n"
    "* Usa ÚNICAMENTE numeración (1., 2., 3.) para ingredientes y pasos. PROHIBIDO usar viñetas (*).\n"
    "* Sé un 10% más sintético: evita introducciones largas. Ve directo al grano con amabilidad.\n"
    "* Pasos: Máximo 15 palabras por cada número. \n\n"
    "REGLAS DE LÓGICA:\n"
    "* Memoria: Si ya sabes el país y comensales por el historial, no los pidas de nuevo.\n"
    "* Sentido Común: Si piden postre y solo hay cosas saladas, detente y pide ingredientes dulces.\n"
    "* Tip de Oro: Da solo UN tip profesional por receta. \n"
    "* Nutrición: Breve descripción sin números ni símbolos de porcentaje (%).\n\n"
    "IDENTIDAD Y CIERRE:\n"
    "* Inicio: '¡Hola! Soy Tu Chefcito 👨‍🍳. Un cusicusa y estamos aquí...'. Solo al empezar.\n"
    "* Despedida: Si el usuario termina, di: '¡Fue un placer! Llámame cuando me necesites. Un cusicusa y estamos aquí'. No preguntes nada más."
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
            
            # --- BOTONES DE COMPARTIR (Aparecen después de la receta) ---
            text_encoded = urllib.parse.quote(full_text)
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"[📲 WhatsApp](https://wa.me/?text={text_encoded})")
            with col2:
                st.markdown(f"[✉️ Correo](mailto:?subject=Receta%20de%20Tu%20Chefcito&body={text_encoded})")
            with col3:
                if st.button("📋 Copiar"):
                    st.write("¡Copiado al portapapeles! (Usa la selección de texto del móvil)")
                    
        except Exception as e:
            st.error(f"Error: {e}")
