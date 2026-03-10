import streamlit as st
import google.generativeai as genai
import time

# 1. CONFIGURACIÓN VISUAL (24px para lectura cómoda)
st.set_page_config(page_title="Tu Chefcito 👨‍🍳", page_icon="👨‍🍳")
st.markdown("""
    <style>
    .stChatMessage, p, li, div, span {
        font-size: 24px !important;
        line-height: 1.5 !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("👨‍🍳 Tu Chefcito")

# 2. CARGA DE API KEY
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Error: Configura la nueva GOOGLE_API_KEY en los Secrets de Streamlit.")
    st.stop()

# 3. DEFINICIÓN DEL MODELO Y REGLAS DE ORO
# He ajustado las instrucciones para eliminar la 'amnesia' y la 'poesía'
instrucciones_maestras = (
    "Eres 'Tu Chefcito', un experto culinario global con un tono humano y divertido.\n\n"
    "REGLAS DE COMPORTAMIENTO:\n"
    "* MEMORIA CRÍTICA: Antes de responder, revisa el historial. Si el usuario YA DIJO su PAÍS y COMENSALES, NO los vuelvas a pedir jamás.\n"
    "* PRESENTACIÓN: Solo di tu nombre ('Soy Tu Chefcito') en el primer saludo de la conversación. NO te presentes en cada mensaje intermedio.\n"
    "* VALIDACIÓN: Si (y solo si) faltan el país o comensales en TODO el historial, pídelos amablemente antes de cocinar.\n"
    "* INGREDIENTES: Usa estrictamente lo que el usuario mencione. Solo puedes sugerir un máximo de 2 ingredientes extra como 'toque de chef'.\n"
    "* PROHIBIDO LA POESÍA: No uses metáforas como 'baile de sabores' o 'festival sensorial'. Describe colores físicos (ej. Rojo intenso, verde hoja) y texturas reales (ej. Crujiente, cremoso).\n"
    "* NUTRICIÓN FLASH: Describe el balance nutricional de forma breve. PROHIBIDO usar porcentajes o números.\n"
    "* FORMATO: Cada párrafo o paso debe ser una viñeta separada.\n"
    "* CIERRE: Finaliza siempre con: '¿Desea que le asista con algún otro platillo?'."
)

# Inicializamos el modelo con las instrucciones del sistema
model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    system_instruction=instrucciones_maestras
)

# 4. GESTIÓN DEL HISTORIAL DE CHAT
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Saludo inicial único
    bienvenida = (
        "¡Hola! Soy **Tu Chefcito** 👨‍🍳. Un cusicusa y estamos aquí... \n\n"
        "Para empezar, ¿en qué país estás, qué tienes en la cocina y para cuántos somos?"
    )
    st.session_state.messages.append({"role": "assistant", "content": bienvenida})

# Mostrar mensajes anteriores
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 5. PROCESAMIENTO DE LA INTERACCIÓN
if prompt := st.chat_input("¿Qué cocinamos hoy?"):
    # Guardar y mostrar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Respuesta del asistente con Efecto Streaming
    with st.chat_message("assistant"):
        # Convertimos el historial al formato que espera Gemini
        history_for_gemini = [
            {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]}
            for m in st.session_state.messages[:-1] # Excluimos el último que acabamos de agregar
        ]
        
        chat = model.start_chat(history=history_for_gemini)
        
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
            
        except Exception as e:
            st.error(f"¡Chispazo en la cocina! Error: {e}")
