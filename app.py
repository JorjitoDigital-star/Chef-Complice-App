import streamlit as st
import google.generativeai as genai
import time

# 1. ESTILO VISUAL: Optimizado para lectura clara en móviles (24px)
st.set_page_config(page_title="Tu Chefcito 👨‍🍳", page_icon="👨‍🍳")

st.markdown("""
    <style>
    .stChatMessage, p, li, div {
        font-size: 24px !important;
        line-height: 1.6 !important;
        color: #1A1A1A;
    }
    .recetario-chef {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 12px;
        border-left: 10px solid #E63946;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

st.title("👨‍🍳 Tu Chefcito")

# 2. CONFIGURACIÓN DE SEGURIDAD Y API
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Error: Configura la GOOGLE_API_KEY en los Secrets.")
    st.stop()

# Ajuste de seguridad para evitar el "Chispazo" (Filtros sensibles)
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

@st.cache_resource
def configurar_modelo():
    # Usamos Gemini 1.5 Flash para máxima velocidad y cuota alta (1,500 gratis/día o pago)
    return genai.GenerativeModel(
        model_name='gemini-1.5-flash',
        safety_settings=safety_settings
    )

model = configurar_modelo()

# 3. GESTIÓN DE LA CONVERSACIÓN
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Presentación con Guía específica según lo solicitado
    bienvenida = (
        "¡Hola! Soy **Tu Chefcito** 👨‍🍳. Para ayudarte a cocinar algo increíble hoy, por favor dime:\n\n"
        "* ¿En qué **país o región** estás?\n"
        "* ¿Qué **ingredientes** tienes a la mano?\n"
        "* ¿Para **cuántos comensales** vamos a cocinar?"
    )
    st.session_state.messages.append({"role": "assistant", "content": bienvenida})

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

# 4. LÓGICA DE RESPUESTA "HUMANA Y MINIMALISTA"
if prompt := st.chat_input("Escribe aquí tus ingredientes..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # INSTRUCCIONES MAESTRAS (SYSTEM PROMPT)
        instrucciones = (
            "Eres 'Tu Chefcito', un experto culinario cálido y recursivo. Habla siempre en PRIMERA PERSONA ('Yo te ayudo', 'Te sugiero').\n\n"
            "REGLAS DE ORO:\n"
            "* Usa viñetas para los párrafos y listas.\n"
            "* NO te saludes a ti mismo. Sé directo.\n"
            "* COMBINA Nutrición y Equilibrio 50/25/25 en una sola sección breve.\n"
            "* PASOS SENSORIALES: Describe colores, aromas y texturas de forma concisa (máximo 2 líneas por paso).\n"
            "* GRAMÁTICA: Escribe de forma natural. PROHIBIDO separar sílabas con espacios (ej. NO 'Estof ado').\n"
            "* MEMORIA: Si ya sabes los comensales o el país, no los vuelvas a preguntar.\n"
            "* CIERRE: Termina siempre con: '¿Desea que le asista con algún otro platillo?'.\n"
            "* DESPEDIDA: Si el usuario agradece o termina, despídete con mucha cordialidad recordándole que siempre estarás para ayudarle.\n"
        )
        
        try:
            # Conversión de historial para compatibilidad con Gemini
            historial_google = []
            for m in st.session_state.messages[:-1]:
                rol = "user" if m["role"] == "user" else "model"
                historial_google.append({"role": rol, "parts": [m["content"]]})

            chat = model.start_chat(history=historial_google)
            response = chat.send_message(instrucciones + prompt, stream=True)
            
            def stream_data():
                for chunk in response:
                    if chunk.text:
                        # Limpieza final de espacios dobles para evitar errores visuales
                        texto = chunk.text.replace("  ", " ")
                        for word in texto.split(" "):
                            yield word + " "
                            time.sleep(0.01)

            full_text = st.write_stream(stream_data())
            
            # Formato de tarjeta visual para recetas
            if "Equilibrio" in full_text:
                output = f'<div class="recetario-chef">{full_text}</div>'
            else:
                output = full_text
                
            st.session_state.messages.append({"role": "assistant", "content": output})
            
        except Exception as e:
            st.error(f"¡Vaya! Hubo un pequeño chispazo en el fogón. ¿Podrías repetirme eso? (Error: {e})")
