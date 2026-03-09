import streamlit as st
import google.generativeai as genai

# 1. ESTILO VISUAL: 24px para tu comodidad total
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

# 2. CONEXIÓN PROFESIONAL (Usando el modelo verificado)
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Error: Configura la GOOGLE_API_KEY en los Secrets de Streamlit.")
    st.stop()

# Inicializamos el motor 2.0 que confirmamos en el escaneo
model = genai.GenerativeModel('gemini-2.0-flash')

# 3. GESTIÓN DEL CHAT
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Saludo guía que diseñamos para tus necesidades
    bienvenida = (
        "¡Hola! Soy **Tu Chefcito** 👨‍🍳. Para cocinar algo increíble hoy en **Perú**, dime:\n\n"
        "* ¿En qué **país o región** te encuentras?\n"
        "* ¿Qué **ingredientes** tienes a la mano?\n"
        "* ¿Para **cuántos comensales** vamos a cocinar?"
    )
    st.session_state.messages.append({"role": "assistant", "content": bienvenida})

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 4. LÓGICA DE COCINA MAESTRA
if prompt := st.chat_input("Tengo arroz, papas y pollo..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Instrucciones de comportamiento del Chef
        instrucciones = (
            "Eres 'Tu Chefcito', un experto culinario de alto nivel. Habla en PRIMERA PERSONA.\n\n"
            "REGLAS DE ORO:\n"
            "* Usa viñetas para cada párrafo y lista de pasos.\n"
            "* FUSIONA en un solo bloque breve: El equilibrio 50% vegetales / 25% proteína / 25% carbohidratos y el valor nutricional.\n"
            "* PASOS: Sé breve, usa lenguaje sensorial (menciona aromas, texturas y colores).\n"
            "* GRAMÁTICA: Fluidez total, sin palabras cortadas ni errores de espaciado.\n"
            "* CIERRE: Finaliza siempre con: '¿Desea que le asista con algún otro platillo?'."
        )
        
        try:
            # Petición al modelo 2.0 (estable y potente)
            response = model.generate_content(instrucciones + prompt)
            texto_final = response.text
            
            st.markdown(texto_final)
            st.session_state.messages.append({"role": "assistant", "content": texto_final})
            
        except Exception as e:
            st.error(f"¡Chispazo! Google está terminando de procesar tu solicitud. Reintenta en unos segundos. (Error: {e})")
