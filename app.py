import streamlit as st
import google.generativeai as genai
import time

# 1. ESTILO VISUAL: 24px para lectura cómoda y profesional
st.set_page_config(page_title="Tu Chefcito 👨‍🍳", page_icon="👨‍🍳")
st.markdown("""
    <style>
    .stChatMessage, p, li, div {
        font-size: 24px !important;
        line-height: 1.6 !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("👨‍🍳 Tu Chefcito")

# 2. CONEXIÓN AL MOTOR 2.5 FLASH
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Error: Configura la GOOGLE_API_KEY en los Secrets de Streamlit.")
    st.stop()

model = genai.GenerativeModel('gemini-2.5-flash')

# 3. PROMPT MAESTRO (Instrucciones de Personalidad y Lógica)
instrucciones_maestras = (
    "Eres 'Tu Chefcito', un experto culinario global. Habla en PRIMERA PERSONA.\n\n"
    "REGLAS CRÍTICAS:\n"
    "* IDENTIDAD: Eres universal. PROHIBIDO decir que eres de Perú. Adáptate a la región que el usuario mencione.\n"
    "* VALIDACIÓN: Si el usuario no menciona su PAÍS o cuántos COMENSALES son, detente y pídelos amablemente antes de dar la receta.\n"
    "* REGLA DE INGREDIENTES: Si te dan una lista, cocina ÚNICAMENTE con esos ingredientes. Puedes sugerir añadir máximo 1 o 2 ingredientes extra como 'toque especial', pero nada más. EXCEPCIÓN: Si piden un plato específico (ej. Lasaña), usa la receta profesional completa.\n"
    "* TONO: Humano, divertido, cercano y con chispa. Nada de tono de biblioteca.\n"
    "* TIP DE CHEF: Incluye siempre un consejo profesional útil y breve.\n"
    "* NUTRICIÓN FLASH: Resume el balance 50/25/25 y valor nutricional en máximo 3 líneas.\n"
    "* LENGUAJE SENSORIAL: Describe colores (ej. 'amarillo paja'), aromas (ej. 'perfume tostado') y texturas físicas (ej. 'crocante al tacto'). Prohibido usar metáforas poéticas.\n"
    "* FORMATO: Usa viñetas para cada párrafo o paso.\n"
    "* PASOS: Máximo 25 palabras por cada instrucción de preparación.\n"
    "* DESPEDIDA: Si el usuario se despide, responde brevemente y no generes contenido extra.\n"
    "* CIERRE: Finaliza siempre con: '¿Desea que le asista con algún otro platillo?'."
)

# 4. GESTIÓN DEL CHAT
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Mensaje de bienvenida con tu frase especial
    bienvenida = (
        "¡Hola! Soy **Tu Chefcito** 👨‍🍳. Un cusicusa y estamos aquí... \n\n"
        "Para empezar nuestra aventura culinaria, cuéntame:\n"
        "* ¿En qué **país o región** estás?\n"
        "* ¿Qué **ingredientes** tienes a la mano?\n"
        "* ¿Para **cuántos comensales** cocinamos?"
    )
    st.session_state.messages.append({"role": "assistant", "content": bienvenida})

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 5. LÓGICA DE RESPUESTA CON STREAMING (Máquina de escribir)
if prompt := st.chat_input("Dime tus ingredientes o un plato específico..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Enviamos las reglas + el input del usuario
        contexto_envio = f"{instrucciones_maestras}\n\nUsuario dice: {prompt}"
        
        try:
            # Generamos respuesta con streaming
            response = model.generate_content(contexto_envio, stream=True)
            
            placeholder = st.empty()
            full_text = ""
            
            for chunk in response:
                if chunk.text:
                    full_text += chunk.text
                    # Efecto de máquina de escribir letra a letra
                    placeholder.markdown(full_text + "▌")
                    time.sleep(0.015) 
            
            placeholder.markdown(full_text)
            st.session_state.messages.append({"role": "assistant", "content": full_text})
            
        except Exception as e:
            st.error(f"¡Chispazo técnico! {e}")
