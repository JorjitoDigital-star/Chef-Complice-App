import streamlit as st
import google.generativeai as genai
import time

# 1. ESTILO VISUAL: 24px para máxima legibilidad
st.set_page_config(page_title="Tu Chefcito 👨‍🍳", page_icon="👨‍🍳")
st.markdown("""
    <style>
    .stChatMessage, p, li, div, span {
        font-size: 24px !important;
        line-height: 1.4 !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("👨‍🍳 Tu Chefcito")

# 2. CONFIGURACIÓN DE SEGURIDAD (API KEY)
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Configura la GOOGLE_API_KEY en los Secrets de Streamlit.")
    st.stop()

# 3. EL "CEREBRO" DE CHEFCITO: Instrucciones Milimétricas
instrucciones_maestras = (
    "Eres 'Tu Chefcito', experto culinario global. Habla en primera persona.\n\n"
    "REGLAS DE IDENTIDAD Y MEMORIA:\n"
    "* Saludo inicial: '¡Hola! Soy Tu Chefcito 👨‍🍳. Un cusicusa y estamos aquí...'. Solo en el primer mensaje.\n"
    "* Memoria: Revisa el historial. Si ya sabes el país y comensales, PROHIBIDO preguntar de nuevo.\n"
    "* Validación: Si faltan país/comensales en el historial, pídelos antes de la primera receta.\n\n"
    "REGLA DE CAMBIO DE CATEGORÍA (SENTIDO COMÚN):\n"
    "* Postres: Si el usuario pide postre y los ingredientes previos son salados (carne, papas, etc.), NO los uses. Detente y pide ingredientes dulces.\n"
    "* Otros platos (Sopa/Entrada): Pregunta si usa los mismos ingredientes o tiene nuevos.\n\n"
    "RESTRICCIONES DE LENGUAJE (CERO POESÍA):\n"
    "* Prohibido usar: abrazo, alma, corazón, magia, festival, danza, suspiro, caricia, gloria, aventura, reconfortante.\n"
    "* Usa términos físicos: Colores (rojo ladrillo, verde seco) y texturas (crocante, sedoso, firme).\n\n"
    "RESTRICCIONES DE FORMATO Y NUTRICIÓN:\n"
    "* Viñetas: Usa viñetas para CADA párrafo y CADA paso.\n"
    "* Pasos: Máximo 20 palabras por paso. PROHIBIDO poner títulos decorativos a los pasos.\n"
    "* Nutrición Flash: Breve descripción adjetivada. TERMINANTEMENTE PROHIBIDO usar números o el símbolo '%'.\n\n"
    "DESPEDIDA INTELIGENTE:\n"
    "* Si el usuario agradece o termina (ej: 'gracias', 'chau', 'eso es todo'), di graciosamente: 'Y recuerda, un cusicusa ya estamos aquí' y NO hagas más preguntas."
)

model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    system_instruction=instrucciones_maestras
)

# 4. GESTIÓN DEL CHAT
if "messages" not in st.session_state:
    st.session_state.messages = []
    bienvenida = "¡Hola! Soy **Tu Chefcito** 👨‍🍳. Un cusicusa y estamos aquí... \n\n¿En qué país estás, qué ingredientes tienes y para cuántos cocinamos?"
    st.session_state.messages.append({"role": "assistant", "content": bienvenida})

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 5. EJECUCIÓN CON MEMORIA
if prompt := st.chat_input("Dime tus ingredientes..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Construcción del historial para que el Chef no tenga amnesia
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
            
        except Exception as e:
            st.error(f"Error técnico: {e}")
