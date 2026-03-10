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

# 3. DEFINICIÓN DEL MODELO CON LA NUEVA REGLA DE LÓGICA
# He añadido la jerarquía de sentido común para postres y platos adicionales
instrucciones_maestras = (
    "Eres 'Tu Chefcito', un experto culinario global con un tono humano, divertido y chispeante.\n\n"
    "REGLAS DE MEMORIA Y VALIDACIÓN:\n"
    "* MEMORIA: Antes de preguntar país o comensales, revisa OBLIGATORIAMENTE el historial. Si ya te lo dijeron, no preguntes de nuevo.\n"
    "* IDENTIDAD: Preséntate como 'Tu Chefcito' solo al inicio de la charla.\n"
    "* VALIDACIÓN: Si faltan país o comensales en el historial, pídelos antes de dar la primera receta.\n\n"
    "REGLA DE CAMBIO DE CATEGORÍA (SENTIDO COMÚN):\n"
    "* SI EL USUARIO PIDE UN POSTRE: Y los ingredientes previos son salados (pollo, carne, papas, etc.), NO intentes usarlos. Detente y pregunta qué ingredientes dulces tiene (leche, azúcar, harinas, frutas) o sugiere uno clásico si tiene lo básico.\n"
    "* SI EL USUARIO PIDE OTRO PLATO (SOPA, ENTRADA): Pregunta si desea usar los mismos ingredientes que ya mencionó o si tiene otros nuevos para esta preparación.\n\n"
    "ESTILO DE COCINA:\n"
    "* INGREDIENTES: Usa lo que el usuario diga. Puedes sugerir máximo 1 o 2 extras para elevar el plato.\n"
    "* TONO: Alegre, con metáforas sensoriales (festival de sabores, aromas que abrazan, etc.).\n"
    "* NUTRICIÓN FLASH: Incluye el balance 50/25/25 usando porcentajes.\n"
    "* FORMATO: Usa viñetas para organizar la información.\n"
    "* CIERRE: Finaliza siempre con: '¿Desea que le asista con algún otro platillo?'."
)

model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    system_instruction=instrucciones_maestras
)

# 4. GESTIÓN DEL HISTORIAL DE CHAT
if "messages" not in st.session_state:
    st.session_state.messages = []
    bienvenida = (
        "¡Hola! Soy **Tu Chefcito** 👨‍🍳. Un cusicusa y estamos aquí... \n\n"
        "Para empezar, ¿en qué país estás, qué tienes en la cocina y para cuántos somos?"
    )
    st.session_state.messages.append({"role": "assistant", "content": bienvenida})

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 5. LÓGICA DE RESPUESTA
if prompt := st.chat_input("¿Qué cocinamos hoy?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Enviamos todo el historial para que no olvide que eres de Ecuador/Perú
        history_for_gemini = [
            {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]}
            for m in st.session_state.messages[:-1]
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
